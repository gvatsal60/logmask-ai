---
title: logmask-ai
sdk: docker
python_version: 3.12
app_port: 8501
tags:
- streamlit
- genai
- python
pinned: false
short_description: AI-Powered Generic Log Anonymization
license: apache-2.0
---

<!-- markdownlint-disable MD025 -->
# logmask-ai

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/gvatsal60/logmask-ai/blob/HEAD/LICENSE)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=gvatsal60_logmask-ai&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=gvatsal60_logmask-ai)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/gvatsal60/logmask-ai/master.svg)](https://results.pre-commit.ci/latest/github/gvatsal60/logmask-ai/HEAD)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/8eaddb15db414c6d8508d09edf485629)](https://app.codacy.com/gh/gvatsal60/logmask-ai/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![CodeFactor](https://www.codefactor.io/repository/github/gvatsal60/logmask-ai/badge)](https://www.codefactor.io/repository/github/gvatsal60/logmask-ai)

`logmask-ai` is a Streamlit application for **PII detection and de-identification** in text.

## Presidio-Based Architecture

This project is explicitly built on **Microsoft Presidio** (sometimes misspelled as "persidio").

- Detection is powered by `presidio-analyzer`.
- De-identification is powered by `presidio-anonymizer`.
- The app combines Presidio recognizers with selectable NLP backends (spaCy, Stanza, and transformers support in helper code).

No custom regex-only masking pipeline is used as the primary anonymization flow. The core anonymization path is Presidio-based.

## Features

- Interactive Streamlit UI for input and output text comparison
- Configurable de-identification operators:
 	- `replace`
 	- `redact`
 	- `mask`
 	- `hash`
 	- `encrypt`
 	- `highlight`
- Adjustable analysis confidence threshold
- Dynamic entity selection based on loaded recognizers/model
- Optional allowlist and denylist controls
- Findings table with confidence scores and optional decision-process metadata

## Setup

```bash
make sync
```

## Run

```bash
make run
```

Or directly:

```bash
uv run streamlit run src/app.py
```

## Test

```bash
make test
```

## Models

The UI currently exposes:

- `spaCy/en_core_web_lg`
- `stanza/en`

The helper layer also supports a transformers-based NLP engine configuration.

## Optional: Presidio Service Containers

`docker-compose.yml` includes container definitions for:

- `mcr.microsoft.com/presidio-analyzer`
- `mcr.microsoft.com/presidio-anonymizer`

These are useful if you want to run Presidio services in containers. The current Streamlit app implementation uses the Presidio Python packages directly.

## Project Structure

```text
src/
 app.py                # Streamlit UI
 helpers.py            # Presidio analysis/anonymization helpers
 nlp_engine_config.py  # NLP engine wiring (spaCy/Stanza/transformers)
 _const.py             # App constants and sample text
test/
 test_helpers.py       # Unit tests for helper logic
```

## Why Presidio?

Presidio provides:

- mature recognizers for common PII entities
- explainable detection results with scores
- multiple anonymization operators
- extensibility with custom recognizers and deny lists

This makes it a strong fit for privacy-first log and text sanitization workflows.

## Attribution

Parts of this project are adapted from Microsoft Presidio samples.

- Upstream project: <https://github.com/microsoft/presidio>
- Upstream license: MIT License

Presidio copyright and license notices apply to the adapted portions.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🛡️ License

This project is licensed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.

