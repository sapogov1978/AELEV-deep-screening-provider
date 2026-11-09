FROM python:3.13.7-slim-bookworm AS python-bookworm

RUN apt-get update \
    && apt-get upgrade --yes \
    && rm -rf /var/lib/apt/lists/*

FROM python-bookworm AS poetry-base
ENV POETRY_VERSION=2.2.1 POETRY_NO_INTERACTION=1 POETRY_VIRTUALENVS_IN_PROJECT=1
WORKDIR /opt/aelev
RUN --mount=type=cache,id=aelev-dss-provider-pip,target=/root/.cache/pip pip install "poetry==${POETRY_VERSION}"
COPY pyproject.toml poetry.lock ./

FROM poetry-base AS dependencies
RUN --mount=type=cache,id=aelev-dss-provider-poetry,target=/root/.cache/pypoetry poetry install --only main --no-root --no-ansi

FROM dependencies AS test
RUN --mount=type=cache,id=aelev-dss-provider-poetry,target=/root/.cache/pypoetry poetry install --only main,dev --no-root --no-ansi
ENV PYTHONPATH=/opt/aelev/src VIRTUAL_ENV=/opt/aelev/.venv PATH=/opt/aelev/.venv/bin:$PATH
COPY src ./src
COPY test ./test
COPY prompts ./prompts
COPY contracts ./contracts
COPY provider.lock.json release.json ./
CMD ["poetry", "run", "pytest", "-q"]

FROM dependencies AS runtime
LABEL org.opencontainers.image.source="https://github.com/sapogov1978/AELEV-deep-screening-provider" \
      io.aelev.owner="deep-screening" \
      io.aelev.deep-screening.compute-contract="opaque-provider-v1"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/opt/aelev/src VIRTUAL_ENV=/opt/aelev/.venv PATH=/opt/aelev/.venv/bin:$PATH HOME=/tmp XDG_CACHE_HOME=/tmp OPENAI_API_KEY_FILE=/run/secrets/provider/credential.env
RUN groupadd --system --gid 10001 aelev && useradd --system --uid 10001 --gid aelev --home-dir /nonexistent aelev
WORKDIR /opt/aelev
COPY --from=dependencies /opt/aelev/.venv ./.venv
RUN python -m pip uninstall --yes pip && rm -rf /usr/local/lib/python3.13/ensurepip/_bundled
COPY --chown=10001:10001 --chmod=0444 provider.lock.json release.json ./
COPY --chown=10001:10001 src ./src
COPY --chown=10001:10001 prompts ./prompts
RUN chmod 0555 ./prompts && chmod 0444 ./prompts/*.txt
USER 10001:10001
RUN python -m aelev_deep_screening_provider verify-config
HEALTHCHECK --interval=10s --timeout=5s --retries=3 CMD ["python", "-c", "import socket; socket.create_connection(('127.0.0.1',18486),3).close()"]
ENTRYPOINT ["python", "-m", "aelev_deep_screening_provider"]
CMD ["serve"]
