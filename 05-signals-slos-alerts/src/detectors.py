import json
from typing import Dict, Any

# ==========================================
# Signal 1: 发现幻觉与假成功 (False Success)
# ==========================================
def detect_false_success(trace: Dict[str, Any]) -> bool:
    """
    判断一条 Trace 是否发生了“假成功”。
    规则: 底层工具明确报错 + Groundedness Judge 打了极低分(0) + 业务库查证未成功
    """
    has_tool_error = any(
        span.get("gen_ai.operation.name") == "execute_tool" and span.get("error") is True
        for span in trace.get("spans", [])
    )

    # 获取异步 Evaluation 分数 (0=Fail, 1=Pass)
    evals = trace.get("evaluations", {})
    groundedness_failed = evals.get("groundedness_score", 1.0) == 0.0

    # 终极业务兜底核查（如果有条件关联业务DB）
    business_failed = trace.get("business_state", {}).get("db_refund_status") == "FAILED"

    return has_tool_error and groundedness_failed and business_failed

# ==========================================
# Signal 2: 识别无状态推进的死循环 (Suspected Loop)
# ==========================================
def detect_loop(trace: Dict[str, Any], loop_threshold: int = 3) -> bool:
    """
    识别死循环。
    核心逻辑: 并非步骤多就是死循环，而是连续调用[同一个工具]，连续获得[error]，且没有明显的状态转移。
    """
    consecutive_errors = 0
    last_tool_name = None

    for span in trace.get("spans", []):
        if span.get("gen_ai.operation.name") == "execute_tool":
            current_tool = span.get("gen_ai.tool.name")
            is_error = span.get("error", False)

            if current_tool == last_tool_name and is_error:
                consecutive_errors += 1
            else:
                consecutive_errors = 1 if is_error else 0
                last_tool_name = current_tool

            if consecutive_errors >= loop_threshold:
                return True
    return False

# ==========================================
# Signal 3: 提取核心成本指标 (Cost Metrics)
# ==========================================
def extract_cost_metrics(trace: Dict[str, Any]) -> Dict[str, Any]:
    """
    提取成本告警所需的核心指标，重点关注 Token 爆炸。
    """
    total_input_tokens = 0
    total_output_tokens = 0

    for span in trace.get("spans", []):
        if span.get("gen_ai.operation.name") == "chat":
            total_input_tokens += span.get("gen_ai.usage.input_tokens", 0)
            total_output_tokens += span.get("gen_ai.usage.output_tokens", 0)

    # 模拟简单的计费公式 (假设某模型费率, 仅做演示)
    estimated_cost = (total_input_tokens * 0.005 / 1000) + (total_output_tokens * 0.015 / 1000)

    return {
        "trace_id": trace["trace_id"],
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "estimated_cost_usd": round(estimated_cost, 4)
    }
