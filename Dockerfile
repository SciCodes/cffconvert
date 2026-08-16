# syntax=docker/dockerfile:1

# ---- build stage ----
# Uses python:3.12-slim for both builder and runtime so the venv's
# Python symlink resolves identically in both stages.
FROM python:3.12-slim AS builder

RUN pip install uv

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
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.version="3.0.0a0"

# Copy the pre-built venv from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Put the venv on PATH so `cffconvert` is directly callable
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
ENTRYPOINT ["cffconvert"]
