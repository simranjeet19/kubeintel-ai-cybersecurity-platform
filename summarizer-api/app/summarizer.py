import asyncio

import anthropic

from app.config import settings
from app.logging_config import logger
from app.models import SummarizeResponse

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


PROMPT_TEMPLATE = """You are a cybersecurity and AI research analyst.

Summarize the following research item concisely. Then assess the risk level.

Title: {title}
Category: {category}

Content:
{content}

Respond in this exact format:
SUMMARY: <2-3 sentence summary>
RISK_LEVEL: <Low | Medium | High | Critical>"""

VALID_RISK_LEVELS = {"Low", "Medium", "High", "Critical"}


def _call_claude(title: str, content: str, category: str) -> SummarizeResponse:
    prompt = PROMPT_TEMPLATE.format(title=title, content=content, category=category)

    message = get_client().messages.create(
        model=settings.model,
        max_tokens=settings.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    summary = ""
    risk_level = "Low"

    for line in response_text.strip().splitlines():
        if line.startswith("SUMMARY:"):
            summary = line.removeprefix("SUMMARY:").strip()
        elif line.startswith("RISK_LEVEL:"):
            risk_level = line.removeprefix("RISK_LEVEL:").strip()

    if not summary:
        raise ValueError("Claude response missing SUMMARY field")
    if risk_level not in VALID_RISK_LEVELS:
        logger.warning("unexpected risk level value", extra={"risk_level": risk_level})
        risk_level = "Low"

    return SummarizeResponse(
        title=title,
        summary=summary,
        risk_level=risk_level,
        category=category,
    )


async def summarize_content(
    title: str, content: str, category: str
) -> SummarizeResponse:
    logger.info(
        "calling claude api",
        extra={"title": title, "category": category, "model": settings.model},
    )
    result = await asyncio.to_thread(_call_claude, title, content, category)
    logger.info(
        "summarization complete",
        extra={"title": title, "risk_level": result.risk_level},
    )
    return result
