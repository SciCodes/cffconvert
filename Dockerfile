# syntax=docker/dockerfile:1

FROM python:3.12-alpine AS builder

RUN pip install --no-cache-dir uv==0.12.5

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /app/.venv && \
    uv pip install --python /app/.venv/bin/python .

FROM builder AS test

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /app/.venv/bin/python ".[testing]"

ENV PATH="/app/.venv/bin:$PATH"
CMD ["pytest", "tests/"]

FROM python:3.12-alpine AS runtime

LABEL org.opencontainers.image.source="https://github.com/scicodes/cffconvert"

RUN addgroup -S -g 10001 cffconvert && \
    adduser -S -D -H -u 10001 -G cffconvert cffconvert

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
USER 10001:10001

ENTRYPOINT ["cffconvert"]
