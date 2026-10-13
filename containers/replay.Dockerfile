FROM python:3.13.12-slim
WORKDIR /opt/rewind
RUN python -m pip install --no-cache-dir uv==0.13.0
COPY pyproject.toml uv.lock ./
COPY packages/ ./packages/
COPY services/api/rewind_api/ ./services/api/rewind_api/
RUN uv sync --frozen --no-dev --python /usr/local/bin/python --no-cache
COPY fixtures/scenarios/ ./fixtures/scenarios/
COPY fixtures/manifest.json ./fixtures/manifest.json
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 10001:10001
ENTRYPOINT ["/opt/rewind/.venv/bin/python", "-m", "rewind_replay.worker"]
