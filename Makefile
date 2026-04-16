#***************************************************************************************
# * File: Makefile
# * Author: Vatsal Gupta
# * Date: 04-Apr-2026
# * Description: Makefile for managing the GenAI application.
# **************************************************************************************/

#***************************************************************************************
# * License
# **************************************************************************************/
# This file is licensed under the Apache 2.0 License.
# License information should be updated as necessary.

#***************************************************************************************
# * Variables
# **************************************************************************************/
TOP_DIR := $(shell git rev-parse --show-toplevel)
SRC_DIR := $(TOP_DIR)/src

#***************************************************************************************
# * Targets
# **************************************************************************************/
.PHONY: all run clean

all: sync run

add:
	@if [ -z "$(pkg)" ]; then \
		echo "❌ Usage: make $@ pkg=\"package_name\"\n"; \
		exit 1; \
	fi
	@uv add --no-cache $(pkg)

sync:
	@uv sync --no-cache --all-extras

debug: sync
	@uv run streamlit run "$(SRC_DIR)/app.py" --server.runOnSave true

run: sync
	@uv run streamlit run "$(SRC_DIR)/app.py"

clean:
	@uv clean
	@rm -rf .venv __pycache__ .mypy_cache
