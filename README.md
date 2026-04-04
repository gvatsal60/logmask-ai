# Log Masking and Analysis App

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/gvatsal60/logmask-ai/blob/HEAD/LICENSE)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=gvatsal60_logmask-ai&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=gvatsal60_logmask-ai)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/gvatsal60/logmask-ai/master.svg)](https://results.pre-commit.ci/latest/github/gvatsal60/logmask-ai/HEAD)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/8eaddb15db414c6d8508d09edf485629)](https://app.codacy.com/gh/gvatsal60/logmask-ai/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![CodeFactor](https://www.codefactor.io/repository/github/gvatsal60/logmask-ai/badge)](https://www.codefactor.io/repository/github/gvatsal60/logmask-ai)

This project can:

- Scan `.log` files from a folder (default: `logs/`)
- Mask sensitive data using Presidio analyzer/anonymizer services
- Analyze masked content with built-in heuristics
- Optionally send masked content to an Ollama model through LiteLLM for deeper analysis

## Setup

```bash
make sync
make up
```

## Usage

### 1. Process all logs from `logs/`

```bash
uv run python main.py
```

Masked files are written to `masked_logs/`.

### 2. Process logs from a custom folder

```bash
uv run python main.py --log-dir ./logs --file-glob "*" --output-dir ./masked_logs
```

### 3. Process direct input text

```bash
uv run python main.py --input-text "User email is test@example.com and IP 10.0.0.10" --print-masked
```

### 4. Process a single input file

```bash
uv run python main.py --input-file ./logs/sip.log --output-dir ./masked_logs --print-masked
```

### 5. Include LLM analysis (on masked content)

```bash
uv run python main.py --analyze
```

You can override model and endpoint:

```bash
uv run python main.py --analyze --model ollama/tinyllama --api-base http://localhost:11434
```

### 6. Override Presidio endpoints

```bash
uv run python main.py \
	--presidio-analyzer-url http://localhost:5002/analyze \
	--presidio-anonymizer-url http://localhost:5001/anonymize
```

## Notes

- Masking is performed by Presidio APIs (no Python regex masking in the app).
- LLM analysis is always run on masked text, not raw input.
- If no `--input-text` or `--input-file` is passed, the app scans `--log-dir`.
- If `--model` is not passed, model falls back to `model_name` from `config.yaml`, then `ollama/tinyllama`.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🛡️ License

This project is licensed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.
