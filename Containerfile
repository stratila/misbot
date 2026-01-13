FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.12-slim
RUN groupadd -g 1004 app && useradd -m -u 1004 -g 1004 app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
USER app
CMD ["/app/.venv/bin/python", "-m", "misbot.server"]