# 03 - 读懂一条真实的 Agent Trace

本目录是《AI Agent 可观测性（三）》文章的配套代码。

我们在这个 Demo 中，用 LangGraph 编写了一个**退款客服 Agent**。并且，我们给大模型植入了一个“恶劣”的 System Prompt，强制它在遇到系统报错时向用户“报喜不报忧”。

## 运行前提

1. 确保已在根目录运行 `pip install -r requirements.txt`，并安装了相关的依赖（如 `langchain-openai`, `langgraph`, `opentelemetry-sdk` 等）。
2. 在 `src/` 目录下复制一份 `.env.example` 为 `.env`。
3. 在 `.env` 中填入你自己的 OpenAI（或 DeepSeek、阿里云等兼容 OpenAI 格式）的 `CUSTOM_API_KEY`。

## 如何运行

进入 `src` 目录，直接运行脚本：

```bash
cd src
python refund_agent.py
```

## 期待看到什么？

1. **零外部依赖**：你不需要启动任何可观测性后端（如 Jaeger 或 Langfuse）。探针配置中使用了 `ConsoleSpanExporter`，它会把抓取到的底层 Trace JSON 直接在终端打印出来。
2. **抓取过程**：你会看到控制台涌出大量带有 `gen_ai.operation.name: execute_tool` 或 `chat` 标签的 Span。
3. **幻觉复现**：你会看到大模型在 `create_refund` 工具中传错了参数（导致 TypeError），但在脚本执行完毕时，终端的最后一行打印出：
   > `👉 Agent 最终回复: 您的退款申请已成功受理，请留意账单。`
   
这就完美复现了文章开篇那个“HTTP 200，但业务挂了”的悬案现场！