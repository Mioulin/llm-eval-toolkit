"""Scoring primitives for llm-eval-toolkit."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EvalResult:
    """Result of a single evaluation task."""
    task_id: str
    category: str
    score: float                      # 0.0 – 1.0
    passed: bool
    model_response: str
    reasoning_trace: Optional[str]
    failure_modes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"EvalResult({self.task_id} | {status} | score={self.score:.2f})"


@dataclass
class SuiteResult:
    """Aggregated results for a full evaluation suite."""
    model: str
    results: List[EvalResult] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    def by_category(self) -> Dict[str, float]:
        cats: Dict[str, List[float]] = {}
        for r in self.results:
            cats.setdefault(r.category, []).append(r.score)
        return {k: sum(v) / len(v) for k, v in cats.items()}

    def failure_mode_summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for r in self.results:
            for fm in r.failure_modes:
                counts[fm] = counts.get(fm, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    def __repr__(self):
        return (
            f"SuiteResult(model={self.model!r}, "
            f"tasks={len(self.results)}, "
            f"score={self.overall_score:.2f}, "
            f"pass_rate={self.pass_rate:.0%})"
        )