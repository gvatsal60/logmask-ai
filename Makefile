# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' || echo "No annotated targets found."

TOP_DIR := $(shell git rev-parse --show-toplevel)
SRC_DIR := $(TOP_DIR)/src

.PHONY: help all run test clean sync debug add

all: sync run ## Run sync then start the app

add: ## Add a new package (usage: make add pkg="package_name")
	@if [ -z "$(pkg)" ]; then \
		echo "❌ Usage: make $@ pkg=\"package_name\"\n"; \
		exit 1; \
	fi
	@uv add --no-cache $(pkg)

sync: ## Sync project dependencies
	@uv sync --no-cache --all-extras

debug: ## Run the app in debug mode with auto-reload
	@uv run streamlit run "$(SRC_DIR)/app.py" --server.runOnSave true

run: sync ## Start the Streamlit app
	@uv run streamlit run "$(SRC_DIR)/app.py"

test: ## Run the test suite
	@echo "Running tests..."
	@uv run python -m pytest

clean: ## Clean build artifacts and caches
	@uv clean
	@rm -rf .venv __pycache__ .mypy_cache
