# 06 - 参考架构与本地 Trace 路由教学 Demo

本目录是《AI Agent 可观测性（六）》文章的配套代码。

本 Demo 为你一键拉起了一套**基于 OpenTelemetry 的本地参考架构子集**：
- **OpenTelemetry Collector**：作为中转枢纽接收 Trace。
- **Arize Phoenix**：AI-Native 的 Trace 展现大盘（开源且支持 OTel）。

> ⚠️ **生产环境边界声明**：
> 1. 本 Demo **不包含** Prometheus、业务 Metrics（无 MeterProvider）、告警、Dataset 沉淀、离线打分与 CI 门禁等后续生产扩展。
> 2. 本 Demo 仅展示了 OTLP → Collector → Phoenix 的 **Trace 路由链路**。
> 3. 本 Demo 专为**本地开发和教学**设计。所有容器绑定在 127.0.0.1，无 TLS 加密，无身份鉴权。绝不能将其直接部署到公网或生产环境。
> 4. LLM 的行为具有非确定性，由于模型版本或提供商限制，在运行时未必能百分百复现“大模型恰好调用两个工具并决定掩盖错误”的幻觉形态。

## 如何运行

在 `06-end-to-end-platform` 根目录下，按顺序执行：

### 1. 准备配置并安装依赖
```bash
# macOS / Linux / Git Bash
cp src/.env.example src/.env
python -m pip install -r src/requirements.txt
```
*(Windows PowerShell 请使用 `Copy-Item src/.env.example src/.env`)*

**请打开 `src/.env` 并填入你真实的 API Key！**

### 2. 拉起底层观测平台基础设施
```bash
docker compose up -d
```

**请确认 Phoenix Dashboard 可通过 `http://127.0.0.1:6060` 访问后，再运行下面的 Agent 脚本。**  
*(若 Trace 未出现，请执行 `docker compose logs phoenix otel-collector` 检查状态)*

### 3. 运行退款 Agent 脚本发送 Trace 

> **隐私安全提示**：默认执行会关闭 LLM Prompt/Completion 的专用采集属性；但当前探针实现可能仍会记录 chain 与 tool 的输入输出。本 Demo 仅使用代码中内嵌的合成数据，**绝不要在此输入真实的客户、订单或生产数据。** 生产环境必须在探针或 Collector 层面配置字段过滤和脱敏。

默认运行（保护隐私）：
```bash
python src/e2e_agent.py
```

**[可选但危险] 强行开启内容捕获 (Content Capture):**
只有开启此选项，你才能在 Phoenix 瀑布流中查看到被大模型掩盖的具体 Prompt 细节：
```bash
# macOS / Linux / Git Bash:
CAPTURE_MESSAGE_CONTENT=true python src/e2e_agent.py

# Windows PowerShell:
# $env:CAPTURE_MESSAGE_CONTENT="true"; python src/e2e_agent.py
```

### 4. 在大盘中查看结果
访问 🌟 **Phoenix 大盘**：`http://127.0.0.1:6060` -> 你会看到带有刚才 Agent 调用的完整 Trace 瀑布流！具体工具调用与模型输出因模型版本和提供方行为而变化。

### 清理环境
测试完毕后，务必清理容器：
```bash
docker compose down
```
