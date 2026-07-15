# 05 - Catching Hallucinations, Loops, and Cost Runaways

*Read this in [中文](README_zh.md).*

This directory contains the companion code for **Part 5: Catching Silent Failures**.

We demonstrate how to transform the Traces and Evaluations learned in previous chapters into actionable **Signals** for SREs, utilizing pure code-based detectors and alerting YAML configurations.

## Prerequisites

1. Prepare your `.env` file in the `src/` directory. An OpenAI-compatible API key is recommended for the LLM Judge step, but the script will gracefully degrade to a **MOCK Judge** mode if omitted, allowing the pure-Python rules (like loop detection) to still run!
2. Dataset: We have prepared 4 highly typical production failure simulations in `data/sample_traces_en.json`:
   - `001`: Normal request.
   - `002`: False Success / Hallucination (combining Tool status with LLM Judge score).
   - `003`: Infinite Loop with no state progression (repeatedly querying a non-existent order).
   - `004`: Cost Runaway (A simple query burned 125k tokens because context truncation failed).

## How to Run

This demo strings together the concepts from the first four parts to form an "Asynchronous Observability Pipeline."

```bash
cd src
python main.py
```

## What to Expect?

The execution results will vividly demonstrate how a **"Multi-Tier Funnel"** saves the company money and prevents customer complaints:

1. **`trace-001`**: Passes all checks, and the script calculates its extremely low cost.
2. **`trace-002`**: The async LLM Judge gives it a score of 0. Combined with the underlying tool error, the system flags it as a [False Success] and triggers an ALARM!
3. **`trace-003`**: **The best part.** The pure Python rule `detect_loop` instantly identifies an infinite loop. The pipeline **blocks it immediately, entirely bypassing the expensive LLM Judge API call**, and fires an ALARM.
4. **`trace-004`**: Caught by the cost metric extractor for burning $0.6+ on a single task, triggering a Warning.

Beyond the Python code, the `rules/alerts.yaml` in this directory provides a sample alert configuration that you can directly apply to Prometheus or Datadog.