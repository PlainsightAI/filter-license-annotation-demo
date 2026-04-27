# syntax=docker/dockerfile:1.4
FROM python:3.11.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash appuser
WORKDIR /app

COPY pyproject.toml README.md VERSION ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

COPY . .

RUN mkdir -p /app/logs && chown -R appuser:appuser /app

USER appuser
CMD ["python", "-m", "filter_license_annotation_demo.filter"]
