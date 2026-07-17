FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /uvx /bin/

ENV UV_LINK_MODE=copy
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# ---------------------------------
# Production stage
# ---------------------------------
FROM base AS deps_prod
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --active --no-install-project --no-editable --no-dev

FROM deps_prod AS builder_prod
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --active --no-editable


FROM python:3.12-slim AS prod
RUN useradd -m app
COPY --from=builder_prod --chown=app:app /opt/venv/ /opt/venv/
COPY --from=builder_prod --chown=app:app /app/alembic /app/alembic
COPY --from=builder_prod --chown=app:app /app/alembic.ini /app/alembic.ini
COPY --chown=app:app entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
USER app
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/opt/venv/bin/python", "-m", "misbot.app"]

# ---------------------------------
# Test stage
# ---------------------------------
FROM builder_prod AS test_builder_prod
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --active --only-group test --inexact


FROM prod AS test
USER root
COPY --from=test_builder_prod --chown=app:app /opt/venv/ /opt/venv/
COPY --chown=app:app tests /app/tests
WORKDIR /app
USER app
ENTRYPOINT []
CMD ["/opt/venv/bin/pytest"]


# ---------------------------------
# Development stage
# ---------------------------------
FROM base AS deps_dev
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --active --no-install-project


FROM deps_dev AS dev
WORKDIR /app
# Install project as editable (points to /app)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=.,target=. \
    uv sync --locked --active
ENV EXECUTE_MIGRATIONS=true
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/opt/venv/bin/python", "-m", "misbot.app"]
