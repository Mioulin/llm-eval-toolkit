---
license: mit
title: LLM Reasoning Evaluator
sdk: gradio
colorFrom: blue
colorTo: indigo
sdk_version: "4.40.0"
app_file: app.py
pinned: true
short_description: Adversarial evaluation toolkit for frontier language models
---


Built by **Zalina Dezhina, PhD** — AI Evaluation Scientist  
*Methodology developed at Mercor for frontier AI systems (GPT-4, Claude, Gemini class).*

---

## What This Does

Four evaluation categories, each targeting a systematic LLM failure mode:

| Category | What it tests | Why it matters |
|---|---|---|
| 📊 **Statistical Reasoning** | Causal inference, p-value interpretation, sampling bias | Most LLMs confidently produce statistically invalid conclusions |
| 🔍 **Hallucination Detection** | Fabricated citations, false premise acceptance, API confabulation | Models confabulate rather than express uncertainty |
| 🧠 **Chain-of-Thought Quality** | Genuine intermediate reasoning vs. post-hoc rationalisation | Superficial CoT structure ≠ correct reasoning |
| 🔢 **Math & Multi-step Reasoning** | Algebra, probability, Bayesian inference | Multi-step errors compound; verification is rarely done |

---

## Quick Start

```bash
pip install llm-eval-toolkit
```

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

from llm_eval import EvalSuite, StatisticalReasoningEvaluator

# Run full suite
suite = EvalSuite(model="claude-sonnet-4-20250514")
result = suite.run()

print(result)
# SuiteResult(model='claude-sonnet-4-20250514', tasks=11, score=0.78, pass_rate=73%)

print(result.by_category())
# {'statistical_reasoning': 0.71, 'hallucination': 0.85, 'chain_of_thought': 0.82, 'math_reasoning': 0.73}

print(result.failure_mode_summary())
# {'base-rate neglect': 2, 'causal confusion': 2, 'shallow CoT': 1}

# Run single category
stat_eval = StatisticalReasoningEvaluator(model="claude-haiku-4-5-20251001")
stat_result = stat_eval.run()
for r in stat_result.results:
    print(r)
```

---

## Evaluation Design

### Adversarial by Default

Every task is designed so that:
- The **naive/intuitive answer is wrong**
- A model that pattern-matches without reasoning **will fail**
- Correct answers require **explicit intermediate steps**

Examples:
- The Bayesian base-rate task (medical test) — most LLMs report ~99% when the correct answer is ~2%
- The hospital mortality task — requires Simpson's paradox reasoning, not raw rate comparison
- The fabricated paper citation — a well-calibrated model must say "I cannot verify this"

### LLM-as-Judge

Scoring uses Claude Opus as judge, with structured rubrics checking:
- **Criteria coverage** — does the response address all key reasoning steps?
- **Failure mode detection** — are known failure patterns present?
- **Score 0.0–1.0** (pass threshold: 0.6)

This mirrors production RLHF evaluation methodology.

---

## Task Registry

```python
from llm_eval import TASK_REGISTRY

for task in TASK_REGISTRY:
    print(f"{task.task_id:12} | {task.category:25} | {task.difficulty}")
```

```
stat_001     | statistical_reasoning    | medium
stat_002     | statistical_reasoning    | easy
stat_003     | statistical_reasoning    | hard
halluc_001   | hallucination            | medium
halluc_002   | hallucination            | hard
halluc_003   | hallucination            | easy
cot_001      | chain_of_thought         | easy
cot_002      | chain_of_thought         | medium
cot_003      | chain_of_thought         | hard
math_001     | math_reasoning           | medium
math_002     | math_reasoning           | hard
math_003     | math_reasoning           | hard
```

---

## Methodology Background

This toolkit emerged from evaluation work at Mercor where I designed and executed
adversarial STEM evaluation tasks for frontier AI systems. The four categories
reflect the failure modes I observed most consistently across GPT-4-class and
Claude-class models when tasked with scientific and quantitative reasoning.

The Bayesian reasoning tasks (stat_003, cot_003, math_003) draw directly from
my PhD research in computational neuroscience, where rigorous probabilistic
reasoning is non-negotiable.

**Related publication:**  
Dezhina, Z. et al. (2023). *Establishing Brain States in Neuroimaging Data.*  
PLOS Computational Biology.

---

## Roadmap

- [ ] Multi-model leaderboard (compare Sonnet vs Haiku vs GPT-4o)
- [ ] Export results to CSV / JSON
- [ ] Custom task injection (`EvalSuite.add_task(...)`)
- [ ] Selection Entropy metric for token-level uncertainty analysis

---

## Citation

```bibtex
@software{dezhina2025llmeval,
  author = {Dezhina, Zalina},
  title  = {LLM Reasoning Evaluator: Adversarial Evaluation Toolkit},
  year   = {2025},
  url    = {https://huggingface.co/spaces/zalinadezhina/llm-reasoning-evaluator}
}
```

## Contact

[LinkedIn](https://linkedin.com/in/zalinadezhina) · dezhina@gmail.com  
*Open to AI Research Scientist, LLM Evaluation, and Senior ML Engineer roles.*