# RAG Transparency Lab

An education-first Gradio app that lets people inspect a Retrieval-Augmented Generation pipeline step by step on a user-uploaded scientific PDF.

Instead of showing only the final answer, this project exposes the full retrieval path:

1. **Chunking**: how the document is split into retrieval units
2. **Hybrid retrieval**: dense similarity + BM25 keyword match
3. **Reranking and filtering**: which chunks survive, which are dropped, and why
4. **Grounded generation**: the final answer plus the exact prompt and source excerpts used

This is the core idea behind the project: when RAG fails, the problem is often not “the model is dumb”, but “the evidence pipeline is noisy”.

---

## Why this project is useful

Most RAG demos hide the mechanics. That makes them good for demos and bad for understanding.

RAG Transparency Lab is built as a **debugging and teaching interface**. It helps people see:

- why chunk boundaries matter,
- why semantic retrieval and keyword retrieval capture different things,
- why reranking and filtering often matter more than prompt tweaks,
- and how grounded generation depends on context quality upstream.

This makes it useful for three audiences at once:

- **learners**, who want to understand how RAG works,
- **practitioners**, who need a way to inspect retrieval failures,
- **recruiters and hiring managers**, who want to see applied AI engineering judgment rather than vague buzzwords.

---

## What the app actually does

### Step 1: Upload and chunk
The app extracts text from a scientific PDF and splits it using three strategies:

- fixed-size chunks,
- overlapping fixed-size chunks,
- semantic sentence-group chunks.

The point is not just to chunk the document, but to make the consequences visible. Bad chunking breaks evidence apart. Better chunking preserves reasoning units.

### Step 2: Hybrid retrieval explorer
Each chunk receives:

- a **dense score** from MiniLM embeddings,
- a **sparse score** from BM25,
- a **hybrid score** from weighted fusion.

The user can change the dense/sparse balance and see rankings shift in real time.

### Step 3: Rerank and filter
The retrieved candidates are rescored using a lightweight reranking heuristic and then filtered:

- low-scoring chunks are removed,
- near-duplicates are dropped,
- only the top ranked context survives.

This stage is intentionally visible because it is where many RAG pipelines quietly succeed or fail.

### Step 4: Final grounded answer
The generator receives only the surviving excerpts.

The app then shows:

- the final answer,
- the exact source excerpts used,
- the exact prompt sent to the model.

That transparency matters. If the answer is weak, you can inspect whether the problem started in chunking, retrieval, reranking, or prompting.

---

## Architecture

![RAG Transparency Lab architecture](assets/rag_transparency_architecture.svg)

---

## Technical stack

- **Interface**: Gradio
- **PDF parsing**: pypdf
- **Dense retrieval**: sentence-transformers, `all-MiniLM-L6-v2`
- **Sparse retrieval**: BM25 via `rank-bm25`
- **Generation**: Anthropic API
- **Data handling**: pandas, numpy

---

## What this demonstrates technically

This project signals several things beyond “I can build a demo”:

- ability to design an **interpretable AI workflow**, not just a black-box app,
- ability to connect **retrieval quality** to **generation quality**,
- ability to make technical systems understandable to non-specialists,
- ability to make trade-offs explicit rather than hiding them behind marketing language.

It also shows pragmatic engineering judgment. For example, the reranking layer is intentionally lightweight and CPU-friendly, which makes the app easier to run in a public Space while still illustrating the role reranking plays in a real pipeline.

---

## Honest limitations

This is an educational transparency tool, not a production-grade enterprise RAG stack.

Current limitations include:

- in-memory session state,
- a lightweight heuristic reranker rather than a full cross-encoder,
- PDF text extraction quality depends on document formatting,
- generation quality still depends on the selected model and retrieved evidence.

That is not a weakness. It is the point: the app is honest about where simplifications exist.

---

## Repo structure

```text
rag-transparency-lab/
├── app.py
├── requirements.txt
├── rag_pipeline/
│   ├── __init__.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── retriever.py
│   ├── reranker.py
│   └── generator.py
├── docs/
│   ├── SOCIAL_POSTS.md
│   ├── RAG_LEARNING_GUIDE.md
│   └── RECRUITER_ANGLE.md
└── assets/
    ├── rag_transparency_poster.png
    └── rag_transparency_architecture.svg
```

---

## Recruiter-facing summary

I built this to show that I do not treat LLM systems as magic boxes. I work at the level where system quality depends on retrieval design, evaluation logic, ranking decisions, and grounded evidence.

This project sits at the intersection of:

- AI evaluation,
- retrieval engineering,
- explainable interfaces,
- and technical communication.

That is the real skill being demonstrated here.
