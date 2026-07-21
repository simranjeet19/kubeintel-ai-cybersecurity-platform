# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-alpine AS builder

WORKDIR /build

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev libpq-dev \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-alpine AS runtime

RUN apk add --no-cache libpq \
 && addgroup -S -g 1000 appgroup \
 && adduser  -S -u 1000 -G appgroup appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY exporter.py .

USER appuser

CMD ["python3", "exporter.py"]
