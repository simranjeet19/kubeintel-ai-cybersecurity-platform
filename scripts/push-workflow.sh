#!/usr/bin/env bash
# push-workflow.sh — imports a workflow JSON into n8n via the REST API
# Usage: N8N_API_KEY=<key> ./scripts/push-workflow.sh [workflow-file]

set -euo pipefail

N8N_URL="${N8N_URL:-http://localhost:5678}"
WORKFLOW_FILE="${1:-workflows/n8n/kubeintel-intel-pipeline.json}"

if [[ -z "${N8N_API_KEY:-}" ]]; then
  echo "ERROR: N8N_API_KEY is not set"
  exit 1
fi

if [[ ! -f "$WORKFLOW_FILE" ]]; then
  echo "ERROR: workflow file not found: $WORKFLOW_FILE"
  exit 1
fi

WORKFLOW_NAME=$(python3 -c "import sys,json; print(json.load(open('$WORKFLOW_FILE'))['name'])")
echo "pushing workflow: ${WORKFLOW_NAME}"

# check if workflow already exists
EXISTING_ID=$(curl -s \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "${N8N_URL}/api/v1/workflows" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
name = '${WORKFLOW_NAME}'
for w in data.get('data', []):
    if w['name'] == name:
        print(w['id'])
        break
" 2>/dev/null || true)

if [[ -n "$EXISTING_ID" ]]; then
  echo "updating existing workflow id: ${EXISTING_ID}"
  HTTP_METHOD="PUT"
  URL="${N8N_URL}/api/v1/workflows/${EXISTING_ID}"
else
  echo "creating new workflow"
  HTTP_METHOD="POST"
  URL="${N8N_URL}/api/v1/workflows"
fi

response=$(curl -s -w "\n%{http_code}" -X "${HTTP_METHOD}" "${URL}" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"${WORKFLOW_FILE}")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
  workflow_id=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
  echo "done — workflow id: ${workflow_id}"
  echo "open: ${N8N_URL}/workflow/${workflow_id}"
else
  echo "ERROR: HTTP ${http_code}"
  echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
  exit 1
fi
