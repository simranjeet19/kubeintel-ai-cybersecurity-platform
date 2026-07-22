# builder stage
FROM python:3.12-alpine AS builder

WORKDIR /build

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev libffi-dev \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt


# runtime stage
FROM python:3.12-alpine AS runtime

RUN addgroup -S -g 1000 appgroup \
 && adduser  -S -u 1000 -G appgroup appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
