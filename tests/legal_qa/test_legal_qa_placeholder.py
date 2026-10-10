"""
Placeholder for answer-quality tests (citation correctness/completeness,
article/version correctness, hallucination rate, answer relevance,
missing-fact detection -- see docs/evaluation.md's Metrics section).

Per docs/evaluation.md, generation quality is only evaluated *after*
retrieval quality is measured against a real evaluation set, and that set
does not exist yet (docs/evaluation.md: "Current state: no evaluation
dataset exists yet"). Faking a passing legal-QA test here -- asserting the
model produces some invented "correct" answer -- would be exactly the kind
of dishonest, unreviewed placeholder docs/evaluation.md warns against. This
test documents the intent and stays skipped until real, lawyer-reviewed
question/answer pairs exist.
"""
import pytest


@pytest.mark.skip(
    reason=(
        "needs data/evaluation/questions.jsonl with real, licensed-Egyptian-"
        "lawyer-reviewed Q&A pairs (question, area, expected_sources, "
        "expected_articles, required_answer_points, difficulty) -- see "
        "docs/evaluation.md's Format section. That file does not exist yet, "
        "and per docs/evaluation.md this step only starts once retrieval "
        "recall@k has already been measured against the same set (step 2 "
        "before step 3). Once it exists: run each question through "
        "app.services.chat_service end-to-end, and score the answer against "
        "required_answer_points for citation correctness, hallucination "
        "rate, and missing-fact detection."
    )
)
def test_legal_qa_answer_quality_against_evaluation_set():
    raise AssertionError(
        "This test intentionally never runs its body -- see the skip reason above."
    )
