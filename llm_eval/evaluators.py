"""
Core evaluators for llm-eval-toolkit.
Uses an LLM-as-judge pattern via Anthropic API for scalable evaluation.
"""

import os
import re
import json
from typing import List, Optional

import anthropic

from .scoring import EvalResult, SuiteResult
from .tasks import EvalTask, TASK_REGISTRY, get_tasks_by_category


# ── Anthropic client (lazy init) ─────────────────────────────────────────────

def _get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set. "
            "Export it or pass via HuggingFace Space secrets."
        )
    return anthropic.Anthropic(api_key=api_key)


def _call_model(client: anthropic.Anthropic, prompt: str, model: str) -> str:
    """Call a model and return the text response."""
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ── LLM-as-Judge ────────────────────────────────────────────────────────────

JUDGE_PROMPT = """You are an expert AI evaluation judge. Your task is to assess a model response against gold criteria.

## Task
{prompt}

## Model Response
{response}

## Gold Criteria (what a correct response must address)
{criteria}

## Failure Indicators (patterns that suggest the response is wrong)
{failure_indicators}

## Your Assessment
Evaluate the response on a 0.0–1.0 scale. Be strict — partial credit for partial reasoning.

Respond in this exact JSON format:
{{
  "score": <float 0.0-1.0>,
  "passed": <true if score >= 0.6>,
  "criteria_met": [<list of criteria that were met>],
  "criteria_missed": [<list of criteria that were missed>],
  "failure_modes": [<list of specific failure modes detected, e.g. "base-rate neglect", "causal confusion", "hallucination", "shallow CoT">],
  "reasoning": "<1-2 sentence explanation of your score>"
}}
"""


def _judge_response(
    client: anthropic.Anthropic,
    task: EvalTask,
    model_response: str,
    judge_model: str = "claude-opus-4-5-20251101",
) -> dict:
    """Use Claude as judge to score a model response."""
    judge_input = JUDGE_PROMPT.format(
        prompt=task.prompt,
        response=model_response,
        criteria="\n".join(f"- {c}" for c in task.gold_criteria),
        failure_indicators="\n".join(f"- {fi}" for fi in task.failure_indicators),
    )
    raw = _call_model(client, judge_input, judge_model)

    # Strip markdown fences if present
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Fallback: partial parse
        return {
            "score": 0.5,
            "passed": False,
            "criteria_met": [],
            "criteria_missed": task.gold_criteria,
            "failure_modes": ["judge_parse_error"],
            "reasoning": "Could not parse judge response.",
        }


# ── Base Evaluator ───────────────────────────────────────────────────────────

class BaseEvaluator:
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        judge_model: str = "claude-opus-4-5-20251101",
        api_key: Optional[str] = None,
    ):
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        self.client = _get_client()
        self.model = model
        self.judge_model = judge_model

    def evaluate_task(self, task: EvalTask) -> EvalResult:
        response = _call_model(self.client, task.prompt, self.model)
        judgment = _judge_response(self.client, task, response, self.judge_model)

        return EvalResult(
            task_id=task.task_id,
            category=task.category,
            score=float(judgment.get("score", 0.5)),
            passed=bool(judgment.get("passed", False)),
            model_response=response,
            reasoning_trace=judgment.get("reasoning"),
            failure_modes=judgment.get("failure_modes", []),
            metadata={
                "criteria_met": judgment.get("criteria_met", []),
                "criteria_missed": judgment.get("criteria_missed", []),
                "model": self.model,
                "task_difficulty": task.difficulty,
            },
        )

    def evaluate_tasks(self, tasks: List[EvalTask]) -> List[EvalResult]:
        return [self.evaluate_task(t) for t in tasks]


# ── Specialised Evaluators ───────────────────────────────────────────────────

class StatisticalReasoningEvaluator(BaseEvaluator):
    """Evaluate LLM statistical reasoning: causal inference, p-values, bias."""

    def run(self) -> SuiteResult:
        tasks = get_tasks_by_category("statistical_reasoning")
        results = self.evaluate_tasks(tasks)
        return SuiteResult(model=self.model, results=results)


class HallucinationEvaluator(BaseEvaluator):
    """Evaluate hallucination and factuality: fabricated citations, false facts."""

    def run(self) -> SuiteResult:
        tasks = get_tasks_by_category("hallucination")
        results = self.evaluate_tasks(tasks)
        return SuiteResult(model=self.model, results=results)


class ChainOfThoughtEvaluator(BaseEvaluator):
    """Evaluate chain-of-thought quality: depth, correctness, intermediate steps."""

    def run(self) -> SuiteResult:
        tasks = get_tasks_by_category("chain_of_thought")
        results = self.evaluate_tasks(tasks)
        return SuiteResult(model=self.model, results=results)


class MathReasoningEvaluator(BaseEvaluator):
    """Evaluate multi-step mathematical and probabilistic reasoning."""

    def run(self) -> SuiteResult:
        tasks = get_tasks_by_category("math_reasoning")
        results = self.evaluate_tasks(tasks)
        return SuiteResult(model=self.model, results=results)


# ── Full Evaluation Suite ────────────────────────────────────────────────────

class EvalSuite(BaseEvaluator):
    """
    Run all four evaluation categories and return a unified SuiteResult.

    Example:
        suite = EvalSuite(model="claude-sonnet-4-20250514")
        result = suite.run()
        print(result)
        print(result.by_category())
        print(result.failure_mode_summary())
    """

    def run(self, categories: Optional[List[str]] = None) -> SuiteResult:
        all_categories = [
            "statistical_reasoning",
            "hallucination",
            "chain_of_thought",
            "math_reasoning",
        ]
        active = categories or all_categories
        tasks = [t for t in TASK_REGISTRY if t.category in active]
        results = self.evaluate_tasks(tasks)
        return SuiteResult(model=self.model, results=results)