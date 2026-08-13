# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

TOP_DIR := $(shell git rev-parse --show-toplevel)
SRC_DIR := $(TOP_DIR)/src

.PHONY: all run test clean

all: sync run

add:
	@if [ -z "$(pkg)" ]; then \
		echo "❌ Usage: make $@ pkg=\"package_name\"\n"; \
		exit 1; \
	fi
	@uv add --no-cache $(pkg)

sync:
	@uv sync --no-cache --all-extras

debug:
	@uv run streamlit run "$(SRC_DIR)/app.py" --server.runOnSave true

run: sync
	@uv run streamlit run "$(SRC_DIR)/app.py"

test:
	@echo "Running tests..."
	@uv run python -m pytest

clean:
	@uv clean
	@rm -rf .venv __pycache__ .mypy_cache
