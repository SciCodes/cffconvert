# syntax=docker/dockerfile:1

# ---- build stage ----
FROM ghcr.io/astral-sh/uv:debian AS builder

WORKDIR /app

# Enable bytecode compilation and copy caching for faster rebuilds
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINKER=system
ENV UV_PYTHON_DOWNLOADS=never

# Install cffconvert from PyPI into an isolated venv (single RUN line for version-sync test compatibility)
RUN uv venv /app/.venv && uv pip install --python /app/.venv/bin/python cffconvert==3.0.0a0

# ---- runtime stage ----
FROM python:3.12-slim AS runtime

# Copy the pre-built venv from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Put the venv on PATH so `cffconvert` is directly callable
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
ENTRYPOINT ["cffconvert"]
