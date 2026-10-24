# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder


USER root

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

RUN apt update && \
    apt install -y gcc libpq5 libpq-dev libmagic1 zlib1g-dev libjpeg-dev

WORKDIR /app/

COPY gunicorn_conf.py /app/
COPY image_cleanup.py /app/image_cleanup.py
COPY alembic.ini /app/
COPY migrations/ /app/migrations/
COPY pyproject.toml uv.lock /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project


COPY classquiz/ /app/classquiz/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked




FROM python:3.14-slim-trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        libmagic1 \
        libpq5 \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app


RUN groupadd --system --gid 9999 nonroot \
	&& useradd --system --gid 9999 --uid 9999 --create-home nonroot

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
COPY *start.sh /app/
RUN chmod +x start.sh
USER nonroot



COPY --from=builder --chown=nonroot:nonroot /app /app

EXPOSE 8000
ENV PYTHONPATH=/app

ENV APP_MODULE=classquiz:app
CMD ["./start.sh"]
