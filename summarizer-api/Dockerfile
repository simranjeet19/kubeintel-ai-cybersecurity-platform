# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-alpine AS builder

WORKDIR /build

COPY requirements.txt .

# gcc + musl-dev needed to compile some python packages on alpine
RUN apk add --no-cache gcc musl-dev libffi-dev \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-alpine AS runtime

# non-root user — never run as root in production
RUN addgroup -S -g 1000 appgroup \
 && adduser  -S -u 1000 -G appgroup appuser

WORKDIR /app

# copy installed deps from builder
COPY --from=builder /install /usr/local

# copy application code
COPY app/ ./app/

# drop to non-root
USER appuser

EXPOSE 8000

# exec form so signals reach uvicorn directly (clean shutdown)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
