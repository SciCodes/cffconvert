# syntax=docker/dockerfile:1

# ---- build stage ----
# Uses the same pinned Python image in both stages so the venv's
# Python symlink resolves identically.
FROM python:3.12.14-alpine3.24@sha256:d09d15e60962ca365d1cd544a48773bac9d33f2fb1b00f2aa0deec78ade7dc31 AS builder

RUN pip install uv==0.12.5

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINKER=system
ENV UV_PYTHON_DOWNLOADS=never

# Copy the source tree and install from local source
COPY . .
RUN uv venv /app/.venv && uv pip install --python /app/.venv/bin/python .

# ---- test stage ----
# Extends builder with testing dependencies; used by `make test`
FROM builder AS test

RUN uv pip install --python /app/.venv/bin/python ".[testing]"

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
CMD ["pytest", "tests/"]

# ---- runtime stage ----
FROM python:3.12.14-alpine3.24@sha256:d09d15e60962ca365d1cd544a48773bac9d33f2fb1b00f2aa0deec78ade7dc31 AS runtime

LABEL org.opencontainers.image.source="https://github.com/scicodes/cffconvert"

# Copy the pre-built venv from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Put the venv on PATH so `cffconvert` is directly callable
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
ENTRYPOINT ["cffconvert"]
