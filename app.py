"""
LLM Reasoning Evaluator — HuggingFace Gradio Space
By Zalina Dezhina, PhD | AI Evaluation Scientist
"""

import os
import json
import gradio as gr
from llm_eval.evaluators import BaseEvaluator
from llm_eval.tasks import TASK_REGISTRY, get_tasks_by_category, get_task_by_id

# ── Constants ────────────────────────────────────────────────────────────────

CATEGORY_LABELS = {
    "statistical_reasoning": "📊 Statistical Reasoning",
    "hallucination": "🔍 Hallucination Detection",
    "chain_of_thought": "🧠 Chain-of-Thought Quality",
    "math_reasoning": "🔢 Math & Multi-step Reasoning",
}

MODEL_OPTIONS = [
    "claude-sonnet-4-20250514",
    "claude-haiku-4-5-20251001",
]

TASK_CHOICES = {
    f"{CATEGORY_LABELS[t.category]} | {t.task_id} [{t.difficulty}] — {t.prompt[:60]}...": t.task_id
    for t in TASK_REGISTRY
}

# ── Evaluation logic ─────────────────────────────────────────────────────────

def run_single_eval(task_label: str, model: str, api_key: str) -> tuple:
    if not api_key.strip():
        return "❌ Please enter your Anthropic API key.", "", "", ""

    task_id = TASK_CHOICES.get(task_label)
    task = get_task_by_id(task_id)
    if not task:
        return "❌ Task not found.", "", "", ""

    try:
        evaluator = BaseEvaluator(model=model, api_key=api_key.strip())
        result = evaluator.evaluate_task(task)
    except Exception as e:
        return f"❌ Error: {e}", "", "", ""

    status = "✅ PASSED" if result.passed else "❌ FAILED"
    score_display = f"**Score: {result.score:.2f} / 1.00** — {status}"

    failure_md = ""
    if result.failure_modes:
        failure_md = "**Failure Modes Detected:**\n" + "\n".join(
            f"- `{fm}`" for fm in result.failure_modes
        )
    else:
        failure_md = "**No failure modes detected** ✓"

    criteria_md = ""
    met = result.metadata.get("criteria_met", [])
    missed = result.metadata.get("criteria_missed", [])
    if met:
        criteria_md += "**✓ Criteria Met:**\n" + "\n".join(f"- {c}" for c in met) + "\n\n"
    if missed:
        criteria_md += "**✗ Criteria Missed:**\n" + "\n".join(f"- {c}" for c in missed)

    return (
        score_display,
        result.model_response,
        failure_md + "\n\n" + (result.reasoning_trace or ""),
        criteria_md,
    )


def run_category_eval(category_label: str, model: str, api_key: str) -> str:
    if not api_key.strip():
        return "❌ Please enter your Anthropic API key."

    # Reverse lookup category key
    cat_key = next((k for k, v in CATEGORY_LABELS.items() if v == category_label), None)
    if not cat_key:
        return "❌ Category not found."

    try:
        evaluator = BaseEvaluator(model=model, api_key=api_key.strip())
        tasks = get_tasks_by_category(cat_key)
        results = evaluator.evaluate_tasks(tasks)
    except Exception as e:
        return f"❌ Error: {e}"

    lines = [f"## {category_label} — Results for `{model}`\n"]
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    avg_score = sum(r.score for r in results) / total if total else 0

    lines.append(f"**Pass Rate:** {passed}/{total} ({passed/total:.0%})")
    lines.append(f"**Avg Score:** {avg_score:.2f}\n")
    lines.append("---")

    for r in results:
        icon = "✅" if r.passed else "❌"
        lines.append(f"### {icon} `{r.task_id}` — Score: {r.score:.2f}")
        if r.failure_modes:
            lines.append("**Failure modes:** " + ", ".join(f"`{fm}`" for fm in r.failure_modes))
        if r.reasoning_trace:
            lines.append(f"*{r.reasoning_trace}*")
        lines.append("")

    # Aggregate failure modes
    all_failures: dict = {}
    for r in results:
        for fm in r.failure_modes:
            all_failures[fm] = all_failures.get(fm, 0) + 1
    if all_failures:
        lines.append("---\n### 🔎 Failure Mode Summary")
        for fm, count in sorted(all_failures.items(), key=lambda x: -x[1]):
            lines.append(f"- `{fm}`: {count}×")

    return "\n".join(lines)


# ── UI ───────────────────────────────────────────────────────────────────────

CSS = """
.gradio-container { font-family: 'IBM Plex Mono', monospace; }
.score-box { font-size: 1.2em; font-weight: bold; }
"""

with gr.Blocks(
    title="LLM Reasoning Evaluator",
    theme=gr.themes.Soft(primary_hue="slate"),
    css=CSS,
) as demo:

    gr.Markdown(
        """
# 🧪 LLM Reasoning Evaluator

**Adversarial evaluation toolkit for frontier language models.**
Tests four failure-prone reasoning categories using an LLM-as-judge framework.

Built by [Zalina Dezhina, PhD](https://linkedin.com/in/zalinadezhina) — AI Evaluation Scientist  
*Based on real evaluation methodology developed at Mercor for frontier AI systems.*

---
        """
    )

    with gr.Row():
        api_key_input = gr.Textbox(
            label="🔑 Anthropic API Key",
            placeholder="sk-ant-...",
            type="password",
            scale=2,
        )
        model_selector = gr.Dropdown(
            choices=MODEL_OPTIONS,
            value=MODEL_OPTIONS[0],
            label="Model to evaluate",
            scale=1,
        )

    with gr.Tabs():

        # ── Tab 1: Single Task ───────────────────────────────────────────────
        with gr.TabItem("🎯 Single Task Evaluation"):
            gr.Markdown(
                "Select an adversarial task and evaluate how a model handles it. "
                "Each task is designed to surface a specific reasoning failure mode."
            )
            task_dropdown = gr.Dropdown(
                choices=list(TASK_CHOICES.keys()),
                label="Select Evaluation Task",
                value=list(TASK_CHOICES.keys())[0],
            )
            run_single_btn = gr.Button("▶ Run Evaluation", variant="primary")

            with gr.Row():
                score_out = gr.Markdown(label="Score", elem_classes=["score-box"])

            with gr.Row():
                with gr.Column():
                    response_out = gr.Textbox(
                        label="Model Response", lines=10, interactive=False
                    )
                with gr.Column():
                    failure_out = gr.Markdown(label="Failure Analysis")
                    criteria_out = gr.Markdown(label="Criteria Breakdown")

            run_single_btn.click(
                fn=run_single_eval,
                inputs=[task_dropdown, model_selector, api_key_input],
                outputs=[score_out, response_out, failure_out, criteria_out],
            )

        # ── Tab 2: Category Sweep ────────────────────────────────────────────
        with gr.TabItem("📊 Category Sweep"):
            gr.Markdown(
                "Run all tasks in a single category and get a full breakdown "
                "with failure mode summary."
            )
            cat_dropdown = gr.Dropdown(
                choices=list(CATEGORY_LABELS.values()),
                label="Select Category",
                value=list(CATEGORY_LABELS.values())[0],
            )
            run_cat_btn = gr.Button("▶ Run Category", variant="primary")
            cat_results_out = gr.Markdown(label="Results")

            run_cat_btn.click(
                fn=run_category_eval,
                inputs=[cat_dropdown, model_selector, api_key_input],
                outputs=[cat_results_out],
            )

        # ── Tab 3: About ─────────────────────────────────────────────────────
        with gr.TabItem("📖 About & Methodology"):
            gr.Markdown(
                """
## Evaluation Design Principles

This toolkit implements the evaluation methodology I developed at Mercor
for assessing frontier AI systems. Four categories were chosen because
they represent the most systematic and consequential failure modes
in deployed LLMs:

### 📊 Statistical Reasoning
Tests whether a model can reason about uncertainty, causality, and
statistical validity — without confusing p-values with proof or
correlation with causation. Tasks include Simpson's paradox,
base-rate neglect, and sampling bias identification.

### 🔍 Hallucination Detection
Probes factuality and epistemic honesty. Tasks include fabricated
citation detection, false premise traps, and code API confabulation.
A well-calibrated model should express uncertainty rather than confabulate.

### 🧠 Chain-of-Thought Quality
Assesses whether the model's reasoning trace is genuine and correct —
not just superficially structured. Tasks include Bayesian updating,
state-space planning, and classic cognitive-reflection problems.

### 🔢 Math & Multi-step Reasoning
Tests mathematical correctness across algebra, probability, and
linear algebra — with explicit verification steps required.
Includes a Bayesian regression task drawn directly from research methodology.

---

## Scoring

Each task is judged by Claude Opus using a structured rubric that checks:
- **Criteria coverage** — does the response address all key points?
- **Failure mode detection** — are any known failure patterns present?
- **Score (0.0–1.0)** — pass threshold at 0.6

---

## Citation

If you use this toolkit, please cite:

```
Dezhina, Z. (2025). LLM Reasoning Evaluator: Adversarial Evaluation
Toolkit for Frontier Language Models. HuggingFace.
```

## Contact

[LinkedIn](https://linkedin.com/in/zalina-dezhina) · dezhina@gmail.com
                """
            )

demo.launch()