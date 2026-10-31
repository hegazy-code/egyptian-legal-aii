#!/usr/bin/env python3
"""
Create vector embeddings for article text using Gemini text-embedding-004.

Reads split-article JSON files produced by scripts/split_articles.py from
data/processed/, embeds them in batches via Gemini, and writes JSONL output
to data/embeddings/articles.jsonl (or a path you specify).

Prerequisites:
  1. GEMINI_API_KEY set in .env (already needed by the backend).
  2. scripts/split_articles.py must have been run first -- its output JSON
     files (one per law) must exist under data/processed/.

Embedding model: text-embedding-004
  - 768 dimensions, multilingual, good Arabic coverage.
  - Same provider as the RAG engine (Gemini) -- no second API key needed.
  - Task type: RETRIEVAL_DOCUMENT for the corpus, RETRIEVAL_QUERY at search
    time (see app/search/vector.py when that's implemented).

Usage:
    python scripts/create_embeddings.py
    python scripts/create_embeddings.py --input-dir data/processed/ --batch-size 20
    python scripts/create_embeddings.py --output data/embeddings/articles.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Iterator, List, Optional, Sequence, TypedDict

EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSIONS = 768
TASK_TYPE_DOCUMENT = "RETRIEVAL_DOCUMENT"
DEFAULT_BATCH_SIZE = 20  # Gemini embedding API limit is 100; keep lower for safety
RATE_LIMIT_SLEEP = 1.0   # seconds between batches to avoid 429s


class ArticleChunk(TypedDict):
    article_id: str
    law_id: str
    law_name: str
    article_number: str
    text: str


class EmbeddingRecord(TypedDict):
    article_id: str
    law_id: str
    law_name: str
    article_number: str
    text: str
    model: str
    dimensions: int
    vector: List[float]


def load_article_chunks(input_dir: Path) -> List[ArticleChunk]:
    """
    Load all article chunks from split_articles.py output JSON files.

    Expected file format (one JSON file per law, each containing a list):
      [
        {
          "article_id": "labor-law-2025-art-1",
          "law_id": "labor-law-2025",
          "law_name": "قانون العمل رقم 14 لسنة 2025",
          "article_number": "1",
          "text": "..."
        },
        ...
      ]
    """
    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {input_dir}\n"
            "Run scripts/split_articles.py first to produce article chunks."
        )

    chunks: List[ArticleChunk] = []
    json_files = list(input_dir.glob("*.json"))

    if not json_files:
        raise ValueError(
            f"No JSON files found in {input_dir}.\n"
            "Run scripts/split_articles.py first to produce article chunks."
        )

    for json_path in sorted(json_files):
        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"WARNING: skipping {json_path.name} -- JSON parse error: {exc}", file=sys.stderr)
            continue

        if not isinstance(raw, list):
            print(f"WARNING: skipping {json_path.name} -- expected a list, got {type(raw).__name__}", file=sys.stderr)
            continue

        for item in raw:
            if not isinstance(item, dict):
                continue
            # Require at minimum article_id and text
            if not item.get("article_id") or not item.get("text"):
                continue
            chunks.append(
                ArticleChunk(
                    article_id=str(item["article_id"]),
                    law_id=str(item.get("law_id", "")),
                    law_name=str(item.get("law_name", "")),
                    article_number=str(item.get("article_number", "")),
                    text=str(item["text"]),
                )
            )

    print(f"Loaded {len(chunks)} article chunk(s) from {len(json_files)} file(s).")
    return chunks


def _batched(items: List[ArticleChunk], size: int) -> Iterator[List[ArticleChunk]]:
    """Yield successive batches of `size` from `items`."""
    for i in range(0, len(items), size):
        yield items[i : i + size]


def embed_chunks(
    chunks: List[ArticleChunk],
    api_key: str,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> List[EmbeddingRecord]:
    """
    Embed all chunks via Gemini text-embedding-004.

    Batches the requests and sleeps between them to avoid rate limiting.
    On a 429 response, waits 10 seconds and retries once before failing.
    """
    try:
        from google import genai
        from google.genai import types as genai_types
        from google.genai import errors as genai_errors
    except ImportError:
        raise RuntimeError(
            "google-genai package is not installed. "
            "Run: pip install -r backend/requirements.txt"
        )

    client = genai.Client(api_key=api_key)
    records: List[EmbeddingRecord] = []
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for batch_idx, batch in enumerate(_batched(chunks, batch_size), start=1):
        texts = [chunk["text"] for chunk in batch]
        print(
            f"  Batch {batch_idx}/{total_batches}: embedding {len(batch)} chunk(s)...",
            end=" ",
            flush=True,
        )

        for attempt in range(2):
            try:
                response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=texts,
                    config=genai_types.EmbedContentConfig(
                        task_type=TASK_TYPE_DOCUMENT,
                    ),
                )
                break
            except genai_errors.APIError as exc:  # type: ignore[attr-defined]
                code = getattr(exc, "code", None)
                if code == 429 and attempt == 0:
                    print(f"rate limited, waiting 10s...", end=" ", flush=True)
                    time.sleep(10)
                    continue
                raise RuntimeError(f"Gemini embedding API error: {exc}") from exc

        embeddings = response.embeddings
        if len(embeddings) != len(batch):
            raise RuntimeError(
                f"Gemini returned {len(embeddings)} embeddings for {len(batch)} texts "
                f"in batch {batch_idx}. Cannot align -- aborting."
            )

        for chunk, embedding in zip(batch, embeddings):
            records.append(
                EmbeddingRecord(
                    article_id=chunk["article_id"],
                    law_id=chunk["law_id"],
                    law_name=chunk["law_name"],
                    article_number=chunk["article_number"],
                    text=chunk["text"],
                    model=EMBEDDING_MODEL,
                    dimensions=EMBEDDING_DIMENSIONS,
                    vector=list(embedding.values),
                )
            )

        print(f"done.")
        if batch_idx < total_batches:
            time.sleep(RATE_LIMIT_SLEEP)

    return records


def write_jsonl(records: List[EmbeddingRecord], output_path: Path) -> None:
    """Write embedding records as JSONL, one record per line."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(records)} embedding record(s) to {output_path}")


def create_embeddings(
    input_dir: Path,
    api_key: str,
    output_path: Path,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> Sequence[EmbeddingRecord]:
    """Full pipeline: load chunks → embed → write JSONL."""
    chunks = load_article_chunks(input_dir)
    if not chunks:
        raise ValueError("No article chunks found to embed.")

    print(f"\nEmbedding {len(chunks)} chunk(s) using {EMBEDDING_MODEL}...")
    records = embed_chunks(chunks, api_key=api_key, batch_size=batch_size)
    write_jsonl(records, output_path)
    return records


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create Gemini vector embeddings for article chunks produced by "
            "scripts/split_articles.py. Writes JSONL output to data/embeddings/."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory of split-article JSON files (default: data/processed/).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/embeddings/articles.jsonl"),
        help="Output JSONL path (default: data/embeddings/articles.jsonl).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Articles per Gemini API call (default: {DEFAULT_BATCH_SIZE}, max: 100).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Gemini API key. Defaults to GEMINI_API_KEY env var.",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print(
            "ERROR: GEMINI_API_KEY is not set. "
            "Set it in .env or pass --api-key.",
            file=sys.stderr,
        )
        return 1

    try:
        create_embeddings(
            input_dir=args.input_dir,
            api_key=api_key,
            output_path=args.output,
            batch_size=args.batch_size,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
