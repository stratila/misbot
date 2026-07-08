FROM python:3.12-slim AS deps
COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /uvx /bin/

ENV UV_LINK_MODE=copy
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --active --no-install-project --no-editable

FROM deps AS builder
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --active --no-editable


FROM python:3.12-slim AS prod
RUN useradd -m app
COPY --from=builder --chown=app:app /opt/venv/ /opt/venv/
COPY --from=builder --chown=app:app /app/alembic /app/alembic
COPY --from=builder --chown=app:app /app/alembic.ini /app/alembic.ini
COPY --chown=app:app entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
USER app
ENTRYPOINT ["/app/entrypoint.sh"]


FROM deps AS dev
WORKDIR /app
# Install project as editable (points to /app)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=.,target=. \
    uv sync --locked --active
ENTRYPOINT ["/app/entrypoint.sh"]
