# AI Agent Observability Labs 🔬

这个仓库是《AI Agent 可观测性》系列文章的官方配套代码库。
我们的目标是：**提供能落地、能跑、能抄的工程物料。**

## 目录结构

* **`01-02-theory/`**: 前两篇的理论基础（无代码）。
* **`03-tracing-instrumentation/`**: 第 3 篇 Demo —— 给 LangGraph Agent 挂载 OTel 探针，并在终端直接打印真实的 Trace JSON。
* **`04-llm-as-a-judge/`**: 第 4 篇 Demo —— 用大模型作为裁判，离线加载 Trace 数据进行语义打分。
* **`05-signals-slos-alerts/`**: 第 5 篇 Demo —— 不依赖大模型的纯规则检测器，抓取死循环、计算成本，并演示 Prometheus 告警规则。
* **`06-end-to-end-platform/`**: 第 6 篇 Demo —— 本地参考架构子集，拉起 OpenTelemetry Collector 和 Arize Phoenix，演示 Trace 从应用层经由 Collector 路由分发到可视化大盘的链路。

## 快速开始

所有的实战 Demo 都位于各自的目录下。请进入对应目录，按照指示配置 `.env` 文件（需要提供 OpenAI 兼容的 API Key）即可开始运行。
