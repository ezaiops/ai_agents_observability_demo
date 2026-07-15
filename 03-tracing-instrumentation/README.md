# 03 - Decoding an Agent Trace

*Read this in [中文](README_zh.md).*

This directory contains the companion code for **Part 3: Decoding an Agent Trace**.

In this demo, we build a **Refund Support Agent** using LangGraph. We intentionally inject a "malicious" System Prompt to force the LLM to cover up underlying system errors and reply to the user with a hallucinated "success" message.

## Prerequisites

1. Ensure you have installed the dependencies from the `requirements.txt` within this directory (`pip install -r requirements.txt`).
2. Copy `.env.example` to `.env` inside the `src/` directory.
3. Fill in your `CUSTOM_API_KEY` (OpenAI, DeepSeek, or any OpenAI-compatible API) in the `.env` file.

## How to Run

Navigate to the `src` directory and run the agent script:

```bash
cd src
python refund_agent.py
```

## What to Expect?

1. **Zero External Dependencies**: You don't need to spin up Jaeger, Langfuse, or any observability backend. We use `ConsoleSpanExporter` to print the raw OpenTelemetry Trace JSON directly to your terminal.
2. **The Tracing Process**: You will see a flood of Spans tagged with `gen_ai.operation.name: execute_tool` and `chat`.
3. **Reproducing the Hallucination**: You will see the LLM pass the wrong parameter type to the `create_refund` tool (causing a `TypeError`). However, the final terminal output will be:
   > `👉 Agent Final Reply: Your refund has been processed, please check your bill.`
   
This perfectly reproduces the "HTTP 200, but business logic failed" crime scene described at the beginning of the article!
