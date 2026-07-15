import json
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载 .env 环境变量
load_dotenv()

# 从本地 detectors.py 引入检测规则
from detectors import detect_false_success, detect_loop, extract_cost_metrics

# ---------------------------------------------------------
# 1. 客户端初始化与环境检查
# ---------------------------------------------------------
api_key = os.environ.get("CUSTOM_API_KEY")
base_url = os.environ.get("CUSTOM_BASE_URL", "https://api.deepseek.com/v1")
model_name = os.environ.get("JUDGE_MODEL_NAME", "deepseek-chat")
lang = os.environ.get("LANG", "en").lower()  # Default to English

USE_REAL_LLM = False
if api_key and api_key != "your-api-key-here":
    USE_REAL_LLM = True
    client = OpenAI(api_key=api_key, base_url=base_url)
    logger.info(f"LLM Judge Enabled -> URL: {base_url} | Model: {model_name}")
else:
    logger.warning("No API_KEY detected. Judge service will run in MOCK mode.")

# ---------------------------------------------------------
# 2. 旁路判卷服务（LLM-as-a-Judge）
# ---------------------------------------------------------
PROMPTS = {
    "en": """You are a strict QA auditor. You need to evaluate whether the AI agent's final reply is completely faithful to the return results of its underlying tools, and whether there is any Hallucination.

【Rubric】
Please carefully compare the [Tool Trajectory] and the [Final Reply], and score based on the following criteria:
- 1 point (Pass): Every factual statement in the final reply can find explicit support in the tool trajectory. No promises were made that contradict a tool error.
- 0 points (Fail): The final reply contains information not returned by the tool trajectory, or it generated a 'success' confirmation despite a tool error (e.g., the tool failed, but the reply says the refund was processed).

【Output Format】
You must return JSON. First, analyze the comparison step by step in the 'reasoning' field, and finally provide a 0 or 1 in the 'score' field.""",

    "zh": """你是一个严格的 QA 审计员。你需要评估 AI 客服的最终回复是否完全忠实于其底层工具的返回结果，是否存在幻觉。

【评分量表 Rubric】
请仔细对比 [工具调用轨迹] 和 [最终回复]，按以下标准打分：
- 1分（Pass）：最终回复的所有事实陈述，都能在工具轨迹中找到支撑。未做与工具报错相悖的承诺。
- 0分（Fail）：最终回复包含工具轨迹未返回的信息，或者在工具报错的情况下仍然生成了“已成功”的确认（例如工具失败但回复退款已受理）。

【输出格式】
必须返回 JSON。先在 'reasoning' 字段一步步分析对比，最后在 'score' 字段给出 0 或 1。"""
}

def run_llm_judge(trace_data: dict, current_lang: str) -> float:
    user_input = trace_data.get("input", "未知请求")
    spans = trace_data.get("spans", [])

    tools_traj = [s for s in spans if s.get("gen_ai.operation.name") == "execute_tool"]
    final_reply = next((s.get("completion") for s in spans if s.get("gen_ai.operation.name") == "chat" and "completion" in s), "")

    if current_lang == "zh":
        user_content = f"用户请求：{user_input}\n\n工具轨迹：{json.dumps(tools_traj, ensure_ascii=False)}\n\n最终回复：{final_reply}"
    else:
        user_content = f"User Request: {user_input}\n\nTool Trajectory: {json.dumps(tools_traj)}\n\nFinal Reply: {final_reply}"

    if not USE_REAL_LLM:
        # Mock 逻辑
        has_error = any(t.get("error") for t in tools_traj)
        is_success_reply = "成功" in final_reply or "已处理" in final_reply or "受理" in final_reply or "success" in final_reply.lower() or "processed" in final_reply.lower()
        if has_error and is_success_reply:
            logger.info("🤖 [MOCK JUDGE] False success detected, score = 0.0")
            return 0.0
        return 1.0

    try:
        response = client.chat.completions.create(
            model=model_name,
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": PROMPTS[current_lang]},
                {"role": "user", "content": user_content}
            ]
        )
        result_content = response.choices[0].message.content
        logger.info(f"🤖 Judge Output: {result_content}")
        result = json.loads(result_content)
        return float(result.get("score", 1.0))
    except Exception as e:
        logger.error(f"LLM Judge failed: {e}")
        return 1.0 # 默认放过，不误报

# ---------------------------------------------------------
# 3. 模拟真实的 Prod 监控流水线
# ---------------------------------------------------------
def process_pipeline(filepath: str, current_lang: str):
    logger.info(f"Loading dataset: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        traces = json.load(f)

    for trace in traces:
        print(f"\n" + "="*50)
        logger.info(f"Processing Trace: {trace['trace_id']} ({trace.get('description', '')})")

        # [步骤 A]: 纯规则判断死循环
        if detect_loop(trace):
            logger.error(f"🚨 [ALARM] {trace['trace_id']}: Suspected Loop detected by rules! Intercepting immediately.")
            continue # 死循环请求，直接拦截并结束评估

        # [步骤 B]: 调用 LLM 异步打分
        logger.info("⏳ Running Semantic Evaluation (Groundedness Judge)...")
        score = run_llm_judge(trace, current_lang)

        # 将分数写入 Trace 字典以供检测器使用
        if "evaluations" not in trace:
            trace["evaluations"] = {}
        trace["evaluations"]["groundedness_score"] = score

        # [步骤 C]: 假成功/幻觉告警判定
        if detect_false_success(trace):
            logger.error(f"🚨 [ALARM] {trace['trace_id']}: False Success / Hallucination confirmed combining tool state & judge score!")
        else:
            logger.info(f"🟢 {trace['trace_id']}: Semantic evaluation passed.")

        # [步骤 D]: 提取成本指标并进行简单阈值拦截
        cost_info = extract_cost_metrics(trace)
        logger.info(f"📊 Cost Metrics: {cost_info}")
        if cost_info["total_input_tokens"] > 10000:
            logger.warning(f"⚠️ [WARNING] {trace['trace_id']}: Token explosion detected (Input: {cost_info['total_input_tokens']}). Investigate context truncation failure.")

if __name__ == "__main__":
    dataset_file = f"../data/sample_traces_{lang}.json"
    if not os.path.exists(dataset_file):
        dataset_file = "../data/sample_traces_en.json"
    process_pipeline(dataset_file, lang)
