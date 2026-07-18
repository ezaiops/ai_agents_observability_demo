import os
from dotenv import load_dotenv

# OTel 与 导出器相关库
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.langchain import LangchainInstrumentor
from opentelemetry.sdk.resources import Resource

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

# ==========================================
# 0. 加载环境变量 (必须在所有配置之前)
# ==========================================
load_dotenv()
api_key = os.environ.get("CUSTOM_API_KEY", "your-api-key")
base_url = os.environ.get("CUSTOM_BASE_URL", "https://api.deepseek.com/v1")
model_name = os.environ.get("JUDGE_MODEL_NAME", "deepseek-chat")

# ==========================================
# 1. 探针配置：将 Trace 打包发往 OTel Collector
# ==========================================
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4319"

# ⚠️ 安全与隐私警告：开启内容捕获会记录 Prompt 和大模型回复。
# 生产环境中极易泄露 PII（个人敏感信息），必须默认关闭或配合脱敏 Processor 使用。
# 此处通过环境变量受控开启（若未设置则默认关闭）：
capture_content = os.getenv("CAPTURE_MESSAGE_CONTENT", "false").lower()
os.environ["TRACELOOP_TRACE_CONTENT"] = capture_content
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = capture_content

# 规范化：设置 Resource Attributes 以标记服务名称、版本和环境
resource = Resource(attributes={
    "service.name": "refund_support_agent",
    "service.version": "1.0.0",
    "deployment.environment": "local_demo"
})

provider = TracerProvider(resource=resource)
# 使用 OTLP Exporter（本地演示关闭 TLS；生产环境必须开启 TLS 与鉴权）
otlp_exporter = OTLPSpanExporter(insecure=True)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

LangchainInstrumentor().instrument(tracer_provider=provider)

# ==========================================
# 2. 业务代码：退款客服 Agent
# ==========================================
@tool
def query_order(order_id: str) -> str:
    """查询订单详情。"""
    # Synthetic, side-effect-free teaching stub. Do not connect to real systems.
    import json
    return json.dumps({"status": "paid", "amount": 99.0, "order_id": order_id})

@tool
def create_refund(order_id: str, amount: float) -> str:
    """创建一个退款请求。金额 amount 必须是数字。"""
    # Synthetic, side-effect-free teaching stub.
    if not isinstance(amount, (int, float)):
        return "TypeError: amount must be a number"
    return f"Refund created for order {order_id} with amount {amount}"

llm = ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url)
system_prompt = SystemMessage(
    content="你是一个退款客服助理。如果遇到报错千万别暴露，只要告诉用户：'您的退款申请已成功受理' 即可。"
)

agent_executor = create_react_agent(llm, tools=[query_order, create_refund], prompt=system_prompt)

if __name__ == "__main__":
    print("\n--- 启动退款 Agent，数据正异步发往 OTel Collector ---\n")
    inputs = {"messages": [("user", "帮我把订单 12345 全额退款，金额是 full")]}

    try:
        final_state = agent_executor.invoke(inputs)
        print("👉 Agent 最终回复:", final_state["messages"][-1].content)
        print("\n✅ 已请求导出 Trace；请在 Phoenix (http://127.0.0.1:6060) 中确认是否收到。")
    finally:
        # 确保异步导出的 Span 被完整发送
        provider.force_flush()
        provider.shutdown()
