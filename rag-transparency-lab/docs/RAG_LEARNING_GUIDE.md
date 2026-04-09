# RAG Learning Guide

## What this app helps you inspect

Most people see only the final answer from a RAG system. This app helps you inspect whether the answer quality comes from strong reasoning, strong evidence selection, or both.

---

## Stage 1: Chunking

Chunking means splitting a document into smaller units that can be embedded, retrieved, ranked, and passed to the model.

Why it matters:

- if a chunk is too small, context gets fragmented,
- if a chunk is too large, retrieval becomes noisy,
- if a sentence or argument is split at the wrong place, the model may receive incomplete evidence.

In this app you can compare:

- fixed-size chunking,
- overlapping chunking,
- semantic sentence grouping.

If the retrieved chunks look cut off or partial, the problem may already start here.

---

## Stage 2: Retrieval

### Dense retrieval
Dense retrieval uses embeddings. It finds text that is semantically similar, even if the exact words differ.

### Sparse retrieval
Sparse retrieval uses lexical matching, here with BM25. It is useful when the exact term matters.

### Hybrid retrieval
Hybrid retrieval combines the two.

In this app each result gets three scores:

- **Dense**: semantic match
- **Sparse**: keyword match
- **Hybrid**: weighted fusion

How to interpret them:

- **High dense, low sparse**: conceptually related, but not using the same wording.
- **High sparse, low dense**: keyword overlap, but not always truly relevant.
- **High hybrid**: usually the strongest candidates overall.

---

## Stage 3: Reranking and filtering

Initial retrieval is useful for recall, but it is noisy.

Reranking applies a more selective decision rule to the candidates. Filtering removes:

- chunks below a relevance threshold,
- near-duplicate chunks,
- extra chunks outside the top set.

In this app the reranker is lightweight and heuristic. That makes the logic easier to inspect.

If irrelevant or repetitive chunks survive, answer quality usually drops. If useful chunks are removed, the answer may become incomplete.

---

## Stage 4: Grounded generation

Grounding means the model should answer from the retrieved evidence rather than from broad prior knowledge.

In this app the final answer is generated only from the surviving chunks. The interface also shows:

- the source excerpts,
- the exact prompt used.

That makes it easier to inspect whether the model was under-informed, over-constrained, or given noisy evidence.

---

## Practical debugging order

When the answer looks wrong, inspect these in order:

1. Were the chunks sensible?
2. Did retrieval surface the right candidates?
3. Did reranking keep the right ones?
4. Did the final prompt contain enough evidence?

This order matters because answer problems often start upstream of generation.
