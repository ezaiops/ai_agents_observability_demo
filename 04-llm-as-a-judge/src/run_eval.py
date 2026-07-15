import json
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging to display English output clearly
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

load_dotenv()
api_key = os.environ.get("CUSTOM_API_KEY", "your-api-key")
base_url = os.environ.get("CUSTOM_BASE_URL", "https://api.deepseek.com/v1")
model_name = os.environ.get("JUDGE_MODEL_NAME", "deepseek-chat")
lang = os.environ.get("LANG", "en").lower()  # Default to English

client = OpenAI(api_key=api_key, base_url=base_url)

# ==========================================
# Multilingual Prompts
# ==========================================
PROMPTS = {
    "en": """You are a strict QA auditor. You need to evaluate whether the AI agent's final reply is completely faithful to the return results of its underlying tools, and whether there is any Hallucination.

【Rubric】
Please carefully compare the [Tool Trajectory] and the [Final Reply], and score based on the following criteria:
- 1 point (Pass): Every factual statement in the final reply can find explicit support in the tool trajectory. No promises were made that contradict a tool error.
- 0 points (Fail): The final reply contains information not returned by the tool trajectory, or it generated a 'success' confirmation despite a tool error (e.g., the tool failed, but the reply says the refund was processed).

【Output Format】
You must return JSON. First, analyze the comparison step by step in the 'reasoning' field, and finally provide a 0 or 1 in the 'score' field.""",

    "zh": """你是一个严格的 QA 审计员。你需要评估 AI 客服的最终回复是否完全忠实于其底层工具的返回结果，是否存在幻觉（Hallucination）。

【评分量表 Rubric】
请仔细对比 [工具调用轨迹] 和 [最终回复]，按以下标准打分：
- 1分（Pass）：最终回复的所有事实陈述，都能在工具轨迹中找到支撑。未做与工具报错相悖的承诺。
- 0分（Fail）：最终回复包含工具轨迹未返回的信息，或者在工具报错的情况下仍然生成了“已成功”的确认（例如工具失败但回复退款已受理）。

【输出格式】
必须返回 JSON。先在 'reasoning' 字段一步步分析对比，最后在 'score' 字段给出 0 或 1。"""
}

def evaluate_groundedness(trace_data: dict, current_lang: str) -> dict:
    """ Offline/asynchronous scoring for an Agent Trace """
    user_input = trace_data["input"]
    tools_output = json.dumps(trace_data["tools_trajectory"], ensure_ascii=False)
    final_reply = trace_data["final_response"]

    # Formatting user content based on language
    if current_lang == "zh":
        user_content = f"用户请求：{user_input}\n工具轨迹：{tools_output}\n最终回复：{final_reply}"
    else:
        user_content = f"User Request: {user_input}\nTool Trajectory: {tools_output}\nFinal Reply: {final_reply}"

    response = client.chat.completions.create(
        model=model_name,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": PROMPTS[current_lang]},
            {"role": "user", "content": user_content}
        ]
    )

    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    logging.info("--- Starting LLM-as-a-Judge Offline Evaluation ---")

    # Load dataset based on language
    dataset_file = f"../data/eval_dataset_{lang}.json"
    if not os.path.exists(dataset_file):
        dataset_file = "../data/eval_dataset_en.json"

    logging.info(f"Loading dataset: {dataset_file}")

    with open(dataset_file, "r", encoding="utf-8") as f:
        traces = json.load(f)
        for t in traces:
            logging.info(f"Evaluating Trace ID: {t['trace_id']}")
            result = evaluate_groundedness(t, lang)
            logging.info(f"Score: {result.get('score')}")
            logging.info(f"Reasoning: {result.get('reasoning')}\n")
