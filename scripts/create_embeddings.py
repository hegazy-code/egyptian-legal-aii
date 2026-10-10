#!/usr/bin/env python3
"""
Create vector embeddings for article text -- NOT YET IMPLEMENTED.

This is a deliberate TODO stub, not a missing feature to apologize for.
Two real prerequisites are missing, and faking either would be worse than
waiting:

  1. An embedding model/API decision. Candidates not yet evaluated against
     each other for this project: Gemini's embedding endpoint (would keep
     the stack on the single LLM provider already used in
     backend/app/rag/engine.py), a local sentence-transformers model
     (multilingual, e.g. paraphrase-multilingual-mpnet-base-v2 -- free but
     needs to be benchmarked on Arabic legal text specifically, which is a
     different register from the general multilingual web text most of
     these models are trained on), or a dedicated Arabic-tuned embedding
     model if one with a usable license turns up. None of this has been
     benchmarked yet.

  2. A real corpus to embed. See docs/architecture.md's "Why SQLite now,
     Postgres+pgvector later" section: "with 4 flagship laws and no
     article-level text yet, a vector index has nothing meaningful to
     index." Embedding is the step *after* scripts/split_articles.py has
     produced real article rows from a real ingested corpus -- there is
     currently zero article-level text in this repo to embed (see README's
     "Actually working" list).

Both blockers are tracked in docs/architecture.md and the README's Roadmap
(steps 3-4 happen before this becomes worth building for real).

Intended flow once unblocked (see function signature below):
    1. Read Article rows (via backend/app/repositories, or directly from
       whatever data/processed/ JSON scripts/split_articles.py produced).
    2. Batch them through the chosen embedding model/API.
    3. Store the resulting vectors -- either in Postgres+pgvector's `vector`
       column (see docker-compose.yml's pgvector service and
       app/models/system.py's stubbed embedding column) once the corpus is
       large enough to justify moving off SQLite, or as a flat .npy/.jsonl
       sidecar file for smaller-scale experimentation before that migration.
    4. Record model name + dimensionality + created_at alongside each vector
       so a later re-embed (new model, or corpus grown) is a traceable,
       reproducible operation, not a silent overwrite.

Usage (once implemented):
    python scripts/create_embeddings.py --input-dir data/processed/ \\
        --model <TBD> --output data/embeddings/articles.jsonl

Running this script today always raises NotImplementedError -- that's
intentional, see above.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence, TypedDict


class EmbeddingRecord(TypedDict):
    """Intended output shape: one record per embedded article/chunk."""

    article_id: str
    law_id: str
    text: str
    model: str
    dimensions: int
    vector: List[float]


def create_embeddings(
    input_dir: Path,
    model: str,
    output_path: Path,
    batch_size: int = 32,
) -> Sequence[EmbeddingRecord]:
    """
    Intended signature for the real implementation.

    Would read split-article JSON files under `input_dir` (the output of
    scripts/split_articles.py), embed their text in batches of `batch_size`
    via `model`, and write EmbeddingRecord-shaped rows to `output_path`
    (JSONL). Returns the records written.

    NOT IMPLEMENTED: raises NotImplementedError unconditionally. See the
    module docstring for exactly what's blocking this (no model decision
    made yet, no real article corpus to embed yet).
    """
    raise NotImplementedError(
        "create_embeddings() is not implemented yet. It needs (1) a real "
        "embedding model/API decision -- not yet made, see this script's "
        "module docstring and docs/architecture.md's pgvector-later "
        "reasoning -- and (2) a real article-level corpus produced by "
        "scripts/split_articles.py, which does not exist yet (see README's "
        "'Actually working' section: only 4 rows of registry metadata exist "
        "so far, no article text). Implement this only after both are true."
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "TODO STUB: create vector embeddings for article text. Not implemented -- "
            "blocked on an embedding model decision and a real article corpus. "
            "Always exits with an informative error. See module docstring."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="Directory of split-article JSON (scripts/split_articles.py output).",
    )
    parser.add_argument(
        "--model",
        help="Embedding model/API identifier (no default -- not yet decided, see docstring).",
    )
    parser.add_argument("--output", type=Path, help="Output JSONL path for embedding records.")
    parser.add_argument("--batch-size", type=int, default=32)
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        create_embeddings(
            input_dir=args.input_dir or Path("data/processed"),
            model=args.model or "<undecided>",
            output_path=args.output or Path("data/embeddings/articles.jsonl"),
            batch_size=args.batch_size,
        )
    except NotImplementedError as exc:
        print(f"NOT IMPLEMENTED: {exc}", file=sys.stderr)
        return 1

    return 0  # unreachable today -- create_embeddings() always raises


if __name__ == "__main__":
    sys.exit(main())
