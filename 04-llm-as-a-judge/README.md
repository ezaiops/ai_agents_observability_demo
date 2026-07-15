# 04 - LLM-as-a-Judge Offline Evaluation

*Read this in [中文](README_zh.md).*

This directory contains the companion code for **Part 4: How to Score "Right vs. Wrong"**.

In Part 3's demo, we caught the agent's hallucination by manually inspecting the Trace. However, with tens of thousands of traces generated daily in production, we need an automated way to score them. This demo illustrates how to use a smarter LLM as a Judge, paired with a structured Rubric, to perform offline evaluation.

## Prerequisites

1. Copy `.env.example` to `.env` inside the `src/` directory and fill in your API Key. **Highly Recommended:** Use a model with excellent reasoning and instruction-following capabilities (e.g., GPT-4o, DeepSeek-Chat) as the Judge.
2. Dataset: We have prepared a minimal trace dataset in `data/eval_dataset_en.json`:
   - `001`: A normal, successful refund request.
   - `002`: The "false success" (hallucination) trace from Part 3, where the tool failed but the agent claimed success.

## How to Run

Navigate to the `src` directory and run the evaluation script:

```bash
cd src
python run_eval.py
```

## What to Expect?

1. **Structured CoT Output**: The script will print the Judge's analytical thought process (`Reasoning`) followed by the final `Score` for each trace.
2. **An Impartial Judge**:
   - For the normal request (`001`), the Judge will output a score of **1**, explicitly citing the `SUCCESS` status from the tool trajectory as evidence in its reasoning.
   - For the hallucinated request (`002`), the Judge will point out the severe contradiction: the tool threw a `TypeError` while the reply confirmed success. It will mercilessly hand down a score of **0**.

Feel free to tweak the `JUDGE_RUBRIC_PROMPT` in `run_eval.py` to see how the Judge's scoring and reasoning behaviors change.