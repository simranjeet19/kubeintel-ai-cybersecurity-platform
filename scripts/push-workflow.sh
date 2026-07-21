#!/usr/bin/env bash
# push-workflow.sh — imports a workflow JSON into n8n via the REST API
# Usage: N8N_API_KEY=<key> ./scripts/push-workflow.sh

set -euo pipefail

N8N_URL="${N8N_URL:-http://localhost:5678}"
WORKFLOW_FILE="workflows/n8n/kubeintel-research-digest.json"

if [[ -z "${N8N_API_KEY:-}" ]]; then
  echo "ERROR: N8N_API_KEY is not set"
  exit 1
fi

echo "pushing workflow to ${N8N_URL}..."

response=$(curl -s -w "\n%{http_code}" -X POST "${N8N_URL}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"${WORKFLOW_FILE}")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
  workflow_id=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
  echo "workflow created — id: ${workflow_id}"
else
  echo "ERROR: HTTP ${http_code}"
  echo "$body"
  exit 1
fi
