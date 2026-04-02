"""
llm-eval-toolkit: LLM Evaluation Toolkit for Statistical Reasoning,
Hallucination Detection, Chain-of-Thought Quality, and Multi-step Math.

By Zalina Dezhina, PhD — AI Evaluation Scientist
"""

from .evaluators import (
    StatisticalReasoningEvaluator,
    HallucinationEvaluator,
    ChainOfThoughtEvaluator,
    MathReasoningEvaluator,
    EvalSuite,
)
from .scoring import EvalResult, SuiteResult
from .tasks import TASK_REGISTRY

__version__ = "0.1.0"
__author__ = "Zalina Dezhina"

__all__ = [
    "StatisticalReasoningEvaluator",
    "HallucinationEvaluator",
    "ChainOfThoughtEvaluator",
    "MathReasoningEvaluator",
    "EvalSuite",
    "EvalResult",
    "SuiteResult",
    "TASK_REGISTRY",
]