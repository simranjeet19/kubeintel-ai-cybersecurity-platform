# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# non-root user — never run as root in production
RUN addgroup --system --gid 1000 appgroup \
 && adduser  --system --uid 1000 --ingroup appgroup --no-create-home appuser

WORKDIR /app

# copy installed deps from builder
COPY --from=builder /install /usr/local

# copy application code
COPY app/ ./app/

# drop to non-root
USER appuser

EXPOSE 8000

# use exec form so signals reach uvicorn directly (clean shutdown)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
