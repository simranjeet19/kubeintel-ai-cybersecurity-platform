#!/usr/bin/env python3
"""
digest-exporter — reads latest research digests from PostgreSQL
and pushes digest.json to the kubeintel-digests GitHub repo.

Runs as a Kubernetes CronJob. All credentials come from env vars
injected via Kubernetes Secrets — nothing is hardcoded.
"""

import json
import os
import sys
import base64
import datetime
import logging

import psycopg2
import requests

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("digest-exporter")


def get_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        log.error("missing required env var: %s", key)
        sys.exit(1)
    return val


def fetch_digests(db_url: str, limit: int = 10) -> list[dict]:
    log.info("connecting to postgres")
    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT title, source_url, category, summary, risk_level, created_at
                FROM research_digests
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    items = []
    for row in rows:
        title, source_url, category, summary, risk_level, created_at = row
        items.append(
            {
                "title": title,
                "source_url": source_url or "",
                "category": category or "",
                "summary": summary or "",
                "risk_level": risk_level or "Low",
                "updated_at": created_at.isoformat() if created_at else "",
            }
        )
    log.info("fetched %d digest items", len(items))
    return items


def get_file_sha(repo: str, path: str, token: str) -> str | None:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers={"Authorization": f"token {token}"}, timeout=10)
    if resp.status_code == 200:
        return resp.json()["sha"]
    if resp.status_code == 404:
        return None
    resp.raise_for_status()


def push_digest(repo: str, path: str, token: str, content: dict, sha: str | None):
    digest = {
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "items": content,
    }
    encoded = base64.b64encode(
        json.dumps(digest, indent=2, ensure_ascii=False).encode()
    ).decode()

    today = datetime.date.today().isoformat()
    payload = {
        "message": f"chore: update intel digest {today}",
        "content": encoded,
    }
    if sha:
        payload["sha"] = sha

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    resp = requests.put(
        url,
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    log.info("pushed digest.json to %s — status %s", repo, resp.status_code)


def main():
    db_url = get_env("DATABASE_URL")
    github_token = get_env("GITHUB_TOKEN")
    github_repo = os.environ.get("GITHUB_REPO", "simranjeet19/kubeintel-digests")
    github_path = os.environ.get("GITHUB_PATH", "digest.json")
    digest_limit = int(os.environ.get("DIGEST_LIMIT", "10"))

    items = fetch_digests(db_url, limit=digest_limit)

    if not items:
        log.warning("no digest items found — skipping push")
        sys.exit(0)

    sha = get_file_sha(github_repo, github_path, github_token)
    push_digest(github_repo, github_path, github_token, items, sha)
    log.info("digest export complete")


if __name__ == "__main__":
    main()
