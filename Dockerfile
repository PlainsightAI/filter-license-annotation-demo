# syntax=docker/dockerfile:1.4
FROM python:3.11.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash appuser
WORKDIR /app

COPY --chown=appuser:appuser . .
# The release workflow writes ./GITHUB_SHA before build; openfilter reads VERSION_SHA to report version_sha.
RUN if [ -f GITHUB_SHA ]; then mv GITHUB_SHA VERSION_SHA; fi
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

USER appuser
CMD ["python", "-m", "filter_license_annotation_demo.filter"]
