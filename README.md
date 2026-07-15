# AI Agent Observability Labs 🔬

*Read this in [中文](README_zh.md).*

This repository is the official companion code for the **"AI Agent Observability"** article series. 
Our goal is to provide **actionable, runnable, and copy-pasteable engineering assets** for SREs and AI Engineers.

## Directory Structure

* **`01-02-theory/`**: Theoretical foundations from Parts 1 & 2 (No code).
* **`03-tracing-instrumentation/`**: Demo for Part 3 — Instrumenting a LangGraph Agent with OpenTelemetry and printing raw Trace JSONs directly to the terminal.
* **`04-llm-as-a-judge/`**: Demo for Part 4 — Using an LLM as a judge to evaluate offline trace data with structured Chain-of-Thought (CoT) and strict rubrics.
* **`05-signals-slos-alerts/`**: Demo for Part 5 — Building an asynchronous observability pipeline. Detects infinite loops via pure Python rules (saving LLM API costs), aggregates costs, and demonstrates Prometheus-style alert rules.

## Quick Start

All hands-on demos are self-contained within their respective directories. Please navigate to the desired directory, configure the `.env` file as instructed (an OpenAI-compatible API key is required), and run the scripts!
