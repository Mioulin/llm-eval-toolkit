"""
Built-in evaluation tasks for llm-eval-toolkit.
Tasks are designed to be adversarial and probe genuine reasoning,
not surface-level pattern matching.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EvalTask:
    task_id: str
    category: str
    prompt: str
    gold_criteria: List[str]          # what a correct answer must contain
    failure_indicators: List[str]     # phrases/patterns that signal failure mode
    difficulty: str = "medium"        # easy / medium / hard
    notes: Optional[str] = None


TASK_REGISTRY: List[EvalTask] = [

    # ── STATISTICAL REASONING ───────────────────────────────────────────────
    EvalTask(
        task_id="stat_001",
        category="statistical_reasoning",
        prompt=(
            "A clinical trial reports that patients taking Drug X had a 30% lower "
            "mortality rate compared to placebo (p=0.03). The trial had 40 patients. "
            "A journalist writes: 'Drug X proven to save lives.' "
            "Evaluate the statistical validity of this claim."
        ),
        gold_criteria=[
            "small sample size concern",
            "statistical significance does not equal practical significance or proof",
            "need for replication",
            "effect size or confidence interval discussion",
        ],
        failure_indicators=[
            "the drug is effective",
            "the claim is correct",
            "p < 0.05 confirms",
        ],
        difficulty="medium",
        notes="Tests conflation of p-value with proof; common LLM failure mode.",
    ),

    EvalTask(
        task_id="stat_002",
        category="statistical_reasoning",
        prompt=(
            "In a study, 80% of people who ate breakfast daily scored above average "
            "on productivity tests. Can we conclude that eating breakfast causes "
            "higher productivity? Explain your reasoning step by step."
        ),
        gold_criteria=[
            "correlation does not imply causation",
            "confounding variables",
            "selection bias or reverse causality",
            "need for randomised controlled trial",
        ],
        failure_indicators=[
            "yes, breakfast causes",
            "the data shows that breakfast improves",
            "we can conclude",
        ],
        difficulty="easy",
        notes="Classic causal inference trap. Tests whether model conflates correlation with causation.",
    ),

    EvalTask(
        task_id="stat_003",
        category="statistical_reasoning",
        prompt=(
            "A hospital reports that its ICU mortality rate is 25%, higher than "
            "the national average of 18%. A critic says the hospital is performing "
            "poorly. The hospital's director says the comparison is unfair. "
            "Who is more likely correct, and why?"
        ),
        gold_criteria=[
            "simpson's paradox or case-mix adjustment",
            "severity of illness / patient acuity",
            "risk adjustment or confounding",
            "naive comparison is misleading",
        ],
        failure_indicators=[
            "the hospital is underperforming",
            "the critic is correct",
            "25% is clearly worse",
        ],
        difficulty="hard",
        notes="Simpson's paradox / severity adjustment. Sophisticated causal reasoning required.",
    ),

    # ── HALLUCINATION DETECTION ──────────────────────────────────────────────
    EvalTask(
        task_id="halluc_001",
        category="hallucination",
        prompt=(
            "Summarise the key findings of the paper: "
            "'Neural Correlates of Quantum Consciousness in Zebrafish Larvae' "
            "by Smith et al., published in Nature Neuroscience, 2024."
        ),
        gold_criteria=[
            "acknowledge uncertainty about whether this paper exists",
            "cannot verify this citation",
            "should not fabricate findings",
        ],
        failure_indicators=[
            "the study found",
            "smith et al. demonstrated",
            "the paper reports",
            "key findings include",
        ],
        difficulty="medium",
        notes="Fabricated paper citation test. Model should express uncertainty, not confabulate.",
    ),

    EvalTask(
        task_id="halluc_002",
        category="hallucination",
        prompt=(
            "What is the capital of the largest country by area that borders "
            "exactly three seas? Give a step-by-step geographical reasoning."
        ),
        gold_criteria=[
            "explicit step-by-step country identification",
            "correct identification of Russia",
            "Moscow as capital",
            "shows verification of the sea-border constraint",
        ],
        failure_indicators=[
            "I'm not sure which country",  # should be confident here
        ],
        difficulty="hard",
        notes="Multi-step factual + geographical reasoning. Tests whether CoT is genuine.",
    ),

    EvalTask(
        task_id="halluc_003",
        category="hallucination",
        prompt=(
            "A colleague claims that the Python function `list.append()` "
            "returns the modified list. Write a code snippet that tests this "
            "claim and explain what it actually returns."
        ),
        gold_criteria=[
            "append returns None",
            "correct code snippet demonstrating this",
            "in-place modification explanation",
        ],
        failure_indicators=[
            "returns the modified list",
            "returns the list",
            "append() returns",
        ],
        difficulty="easy",
        notes="Code hallucination test. Common failure: model agrees with false premise.",
    ),

    # ── CHAIN-OF-THOUGHT QUALITY ─────────────────────────────────────────────
    EvalTask(
        task_id="cot_001",
        category="chain_of_thought",
        prompt=(
            "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than "
            "the ball. How much does the ball cost? Show your full reasoning."
        ),
        gold_criteria=[
            "$0.05",
            "5 cents",
            "algebraic setup or explicit variable definition",
            "checks the answer against the original constraint",
        ],
        failure_indicators=[
            "$0.10",
            "10 cents",
        ],
        difficulty="easy",
        notes="Classic CRT problem. Tests whether CoT prevents intuitive error.",
    ),

    EvalTask(
        task_id="cot_002",
        category="chain_of_thought",
        prompt=(
            "You have a 3-litre jug and a 5-litre jug. No measuring marks. "
            "You need exactly 4 litres. Describe each step of your solution, "
            "tracking the state of both jugs at every step."
        ),
        gold_criteria=[
            "correct final state: 4 litres in one jug",
            "explicit state tracking at each step",
            "valid sequence of fill/pour/empty operations",
        ],
        failure_indicators=[
            "you cannot",
            "it is impossible",
        ],
        difficulty="medium",
        notes="State-space planning test. Good CoT should show explicit intermediate states.",
    ),

    EvalTask(
        task_id="cot_003",
        category="chain_of_thought",
        prompt=(
            "A doctor tells a patient: 'This test for Disease X has 99% sensitivity "
            "and 95% specificity. Your test came back positive.' "
            "The disease affects 1 in 1000 people. "
            "What is the probability the patient actually has Disease X? "
            "Show full Bayesian reasoning."
        ),
        gold_criteria=[
            "bayes theorem explicitly applied",
            "base rate / prior probability used",
            "approximately 2% or correct calculation",
            "acknowledges counterintuitive result",
        ],
        failure_indicators=[
            "99% chance",
            "very likely has the disease",
            "95% probability",
        ],
        difficulty="hard",
        notes="Bayesian base-rate neglect. One of the most robust LLM failure modes.",
    ),

    # ── MATH / MULTI-STEP REASONING ──────────────────────────────────────────
    EvalTask(
        task_id="math_001",
        category="math_reasoning",
        prompt=(
            "If f(x) = x³ - 6x² + 11x - 6, find all roots and verify each one "
            "by substitution. Show all working."
        ),
        gold_criteria=[
            "x=1, x=2, x=3",
            "factorisation or polynomial division shown",
            "verification by substitution for each root",
        ],
        failure_indicators=[
            "cannot solve",
            "requires numerical methods",
        ],
        difficulty="medium",
    ),

    EvalTask(
        task_id="math_002",
        category="math_reasoning",
        prompt=(
            "A Markov chain has transition matrix:\n"
            "P = [[0.7, 0.3], [0.4, 0.6]]\n"
            "Find the stationary distribution. Show the system of equations "
            "and solve step by step."
        ),
        gold_criteria=[
            "π₁ = 4/7 ≈ 0.571",
            "π₂ = 3/7 ≈ 0.429",
            "sets up π = πP with normalisation constraint",
            "solves the linear system explicitly",
        ],
        failure_indicators=[
            "[0.5, 0.5]",
            "equal probabilities",
        ],
        difficulty="hard",
        notes="Tests whether model can handle linear algebra reasoning in probabilistic context.",
    ),

    EvalTask(
        task_id="math_003",
        category="math_reasoning",
        prompt=(
            "In a Bayesian regression model, you place a Normal(0, σ²) prior on "
            "the regression coefficient β. The likelihood is also Gaussian. "
            "Without computing the full posterior, explain qualitatively what "
            "happens to the posterior mean of β as σ² → ∞ and as σ² → 0. "
            "What does this tell us about the role of the prior?"
        ),
        gold_criteria=[
            "σ² → ∞: posterior approaches MLE / likelihood dominates",
            "σ² → 0: posterior shrinks to zero / prior dominates",
            "bias-variance or regularisation framing",
            "ridge regression or L2 connection mentioned",
        ],
        failure_indicators=[
            "the posterior is always the same",
            "prior has no effect",
        ],
        difficulty="hard",
        notes="Conceptual Bayesian reasoning — directly from Zalina's research domain.",
    ),
]


def get_tasks_by_category(category: str) -> List[EvalTask]:
    return [t for t in TASK_REGISTRY if t.category == category]


def get_task_by_id(task_id: str) -> Optional[EvalTask]:
    for t in TASK_REGISTRY:
        if t.task_id == task_id:
            return t
    return None