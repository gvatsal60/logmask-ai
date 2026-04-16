# ##########################################################################
# File: Dockerfile
# Author: Vatsal Gupta (gvatsal60)
# Date: 21-Sep-2025
# Description: Dockerfile for a Streamlit application.
# ##########################################################################

# ##########################################################################
# License
# ##########################################################################
# This Dockerfile is licensed under the Apache 2.0 License.
# License information should be updated as necessary.
# ##########################################################################

# ##########################################################################
# Base Image
# ##########################################################################
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# ##########################################################################
# Maintainer
# ##########################################################################
LABEL maintainer="Vatsal Gupta (gvatsal60)"

# Add non-root user
RUN addgroup --system nonroot \
  && adduser --system --ingroup nonroot nonroot \
  && apt-get update && apt-get install -y --no-install-recommends \
  libsndfile1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# ##########################################################################
# Set Working Directory
# ##########################################################################
WORKDIR /app

# Set cache directory to /tmp to avoid permission issues
ENV XDG_CACHE_HOME=/tmp/.cache
RUN mkdir -p XDG_CACHE_HOME \
  && chmod -R 777 XDG_CACHE_HOME

# ##########################################################################
# Copy Files
# ##########################################################################
# Copy dependency files first for better caching
COPY pyproject.toml ./

# Install dependencies into a local folder
RUN uv sync --no-cache \
  && uv pip install spacy \
  && uv run python -m spacy download en_core_web_sm

# Copy source code
COPY src/ ./

# ##########################################################################
# Expose Port
# ##########################################################################
EXPOSE 8501

# ##########################################################################
# Command to Run
# ##########################################################################
# Switch to non-root user
USER nonroot

ENTRYPOINT [ "uv", "run", \
  "streamlit", "run", "app.py", \
  "--server.port=8501", \
  "--server.address=0.0.0.0"]
