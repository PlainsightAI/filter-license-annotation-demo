# syntax=docker/dockerfile:1.4
# openfilter-base = python:3.11-slim + all outstanding Debian security patches
# (rebuilt weekly): provides the PYTHONDONTWRITEBYTECODE/PYTHONUNBUFFERED env, the
# appuser account, and /app (WORKDIR) + /app/logs — so none of that is repeated here.
FROM plainsightai/openfilter-base:py3.11

COPY --chown=appuser:appuser . .
# The release workflow writes ./GITHUB_SHA before build; openfilter reads VERSION_SHA to report version_sha.
RUN if [ -f GITHUB_SHA ]; then mv GITHUB_SHA VERSION_SHA; fi
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

USER appuser
CMD ["python", "-m", "filter_license_annotation_demo.filter"]
