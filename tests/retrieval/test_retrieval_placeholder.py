"""
Placeholder for retrieval-quality tests (recall@k, precision@k, MRR, NDCG --
see docs/evaluation.md's Metrics section).

Per docs/evaluation.md, retrieval correctness is measured *before* answer
quality, against a hand-written, human-verified question/expected-article
set. That set does not exist yet -- writing a fake-passing test here would
be dishonest (it would assert against invented "correct" articles nobody
verified). This test documents the intent and stays skipped until the real
dataset lands.
"""
import pytest


@pytest.mark.skip(
    reason=(
        "needs data/evaluation/questions.jsonl with real, hand-reviewed "
        "question -> expected_articles pairs (~30-50 questions across the 4 "
        "flagship domains, per docs/evaluation.md step 1) -- that file does "
        "not exist yet, and no article-level law text has been ingested yet "
        "for the retrieval layer to search over (see README Roadmap step 1). "
        "Once it exists: load each question, run it through "
        "app.search.hybrid, and assert the expected article(s) appear in "
        "the top-k results (recall@k / precision@k / MRR per "
        "docs/evaluation.md's Metrics section)."
    )
)
def test_retrieval_recall_at_k_against_evaluation_set():
    raise AssertionError(
        "This test intentionally never runs its body -- see the skip reason above."
    )
