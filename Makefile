#***************************************************************************************
# * File: Makefile
# * Author: Vatsal Gupta
# * Date: 26-Sep-2025
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
SRC_DIR := src

#***************************************************************************************
# * Targets
# **************************************************************************************/
.PHONY: all run test clean

all: sync run

sync:
	@uv sync
run: sync
	@uv run --directory $(SRC_DIR) streamlit run app.py --browser.gatherUsageStats false
test: sync
	@echo "No tests available currently."
# 	@uv test
clean:
	@uv clean
