# 06 - Reference Architecture & Local Trace Routing Demo

*Read this in [中文](README_zh.md).*

This directory contains the companion code for Part 6. 

This demo spins up a **local subset of the reference architecture based on OpenTelemetry**:
- **OpenTelemetry Collector**: Acts as a hub to receive Traces.
- **Arize Phoenix**: An AI-Native Trace dashboard (open-source and OTel compatible).

> ⚠️ **Security & Production Boundaries Warning**:
> 1. This demo **does NOT include** Prometheus, business Metrics (no MeterProvider), Alerts, Datasets, Evaluation scoring, or CI release gates. Those are production extensions.
> 2. This demo illustrates only the flow of application traces via OTLP → Collector → Phoenix.
> 3. This demo is designed strictly for **local development and teaching**. Containers are bound to 127.0.0.1 without TLS encryption or authentication. Do not deploy this to a public or production environment.
> 4. Due to LLM non-determinism, the model may not perfectly reproduce the "tool error cover-up" hallucination during your run.

## How to Run

From the `06-end-to-end-platform` root directory, execute:

### 1. Initialize Configuration and Install Dependencies
```bash
# macOS / Linux / Git Bash
cp src/.env.example src/.env
python -m pip install -r src/requirements.txt
```
*(Windows PowerShell: use `Copy-Item src/.env.example src/.env`)*

**Please open `src/.env` and fill in your real API Key!**

### 2. Spin up the infrastructure
```bash
docker compose up -d
```
Please verify that the Phoenix Dashboard is accessible at `http://127.0.0.1:6060` before running the Agent script below.
*(If Traces do not appear, please run `docker compose logs phoenix otel-collector` to check the status)*

### 3. Run the Agent to generate Traces
By default, the script does not capture prompt/message content to protect privacy:
```bash
python src/e2e_agent.py
```

**[Optional but DANGEROUS] Forcefully enable Content Capture:**
> ⚠️ Only enable this with the repository's synthetic input. Never enter real customer, order, payment, address, authentication, or production data.

```bash
# macOS / Linux / Git Bash:
CAPTURE_MESSAGE_CONTENT=true python src/e2e_agent.py

# Windows PowerShell:
# $env:CAPTURE_MESSAGE_CONTENT="true"; python src/e2e_agent.py
```

### 4. See the Data in the Dashboard

Once the script finishes, you can visit:
- 🌟 **Phoenix Dashboard**: `http://127.0.0.1:6060` -> You will see the Trace waterfall sent by the application! Specific tool calls and outputs may vary based on model behavior.

### Cleanup

To tear down the environment:
```bash
docker compose down
```
