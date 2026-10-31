# Architecture

## Current state (v1 skeleton)

```
USER
  │
  ▼
Next.js frontend (frontend/)  ──►  FastAPI backend (backend/app/)
                                       │
                                       ├── api/          request handlers
                                       ├── services/      business logic (chat_service orchestrates the pipeline below)
                                       ├── rag/
                                       │     ├── analyzer.py       question understanding (Gemini, JSON out)
                                       │     ├── engine.py         assembles retrieved sources + calls Gemini w/ no-hallucination system prompt
                                       │     └── answer_builder.py  8-section Arabic answer, or honest fallback if context is thin
                                       ├── search/
                                       │     ├── exact_reference.py  regex-detects "المادة 341" style refs, prioritizes exact lookup
                                       │     ├── keyword.py          LIKE/full-text search over articles/laws
                                       │     ├── hybrid.py           merges keyword + exact-ref (+ vector, later)
                                       │     └── vector.py           STUB -- pgvector once the corpus is large enough to need it
                                       ├── models/        SQLAlchemy ORM (26 tables, see docs/data-policy.md)
                                       └── repositories/  DB access layer
                                       │
                                       ▼
                              SQLite (dev) / Postgres+pgvector (prod, via DATABASE_URL)
```

## Why SQLite now, Postgres+pgvector later

The full spec calls for Postgres+pgvector from day one. That's right for when there's a real corpus to search semantically -- but with 4 flagship laws and no article-level text yet, a vector index has nothing meaningful to index. Using SQLite for now means the whole stack runs with zero external services, which matters while the actual bottleneck (verified legal data) is being worked on. `DATABASE_URL` is the only thing that changes to move to Postgres; see `docker-compose.yml` for the pgvector-enabled setup, ready when needed.

## The 8-section answer format

Every answer that isn't a clarifying question or an "outside scope" response follows this shape (Arabic headers, per the original spec section 22):

1. فهم سؤالك (understanding of the question)
2. المجال القانوني (legal domain)
3. النصوص القانونية ذات الصلة (relevant articles)
4. الشرح (explanation)
5. تطبيق مبدئي على الوقائع (preliminary application to the facts)
6. معلومات ناقصة (missing information)
7. الإجراءات المحتملة (possible procedures)
8. مصادر الإجابة (sources) + تنبيه (disclaimer)

`app/rag/answer_builder.py` and `frontend/components/ChatMessage.tsx` both implement this shape independently right now (backend returns JSON, frontend renders it) -- once real usage starts, watch for drift between the two and consider generating frontend types from the backend's Pydantic schema (e.g. via `openapi-typescript`) to keep them locked together.

## No-hallucination enforcement (two layers, not one)

Layer 1 (LLM instruction): `app/rag/engine.py`'s system prompt explicitly forbids inventing articles/judgments/citations and requires saying "insufficient information" when the retrieved context doesn't cover the question.

Layer 2 (code, not trusting the model): when Gemini isn't configured or the retrieved context is empty, `answer_builder.build_fallback_answer()` returns the honest "outside scope, consult a lawyer" response directly -- the model is never given the chance to guess. This mirrors the programmatic-check pattern from an earlier project this team built (a Supervisor agent that hard-rejects before any LLM call), and should be extended the same way once article-level citation matching exists: verify a citation is real (exists in the DB, or was a literal substring of a fetched trusted page) *before* trusting the model's self-report.

## What's deliberately not built yet

Auth exists (JWT + bcrypt, real) but nothing gates on it yet in the UI -- dashboard/cases/documents/admin are placeholder pages. OCR, embeddings, and the judgment database are TODO-stubbed because they need real source documents/infrastructure that don't exist yet, not because they're hard to scaffold. See the README's Roadmap section for the actual next-step order.
