# Evaluation

## Test retrieval before testing the AI

This is the most important methodological rule in the original spec, and it's worth restating here: if an answer is wrong, you need to know whether the *database/search* failed to find the right article, or the *LLM* found it but explained it badly. Conflating the two makes every bug report ambiguous. `tests/retrieval/` and `tests/legal_qa/` are separate directories for exactly this reason -- retrieval correctness (recall@k, precision@k against a known-answer set) gets measured before generation quality.

## Current state: no evaluation dataset exists yet

The spec's target is 500, then 2,000+, eventually 10,000+ questions, each reviewed by a licensed Egyptian legal professional. That's real, ongoing work by qualified people -- not something to fabricate placeholder questions for and call "done." Building it honestly, in order:

1. Once the 4 flagship laws have real article-level text (Roadmap step 1), write ~30-50 hand-written questions across the 4 domains, with the actually-correct expected article(s) attached -- small enough that a human (you, or whoever reviews) can verify every single one is right, not just plausible-sounding.
2. Measure retrieval recall@k against that set before worrying about answer quality at all.
3. Only then evaluate the generated answers: citation correctness, hallucination rate (does every citation actually exist and get used correctly), missing-fact detection, relevance.
4. Grow the set gradually, ideally with input from someone with real Egyptian legal training reviewing disagreements -- this is the step that most needs a human, not more AI.

## Format (once it exists)

`data/evaluation/questions.jsonl`, one JSON object per line:
```json
{"question": "...", "area": "criminal", "expected_sources": [], "expected_articles": [], "required_answer_points": [], "difficulty": "medium"}
```

## Metrics

Retrieval: Recall@K, Precision@K, MRR, NDCG. Generation: citation correctness/completeness, article/version correctness, hallucination rate, answer relevance, missing-fact detection -- see spec sections 32-33 for full definitions; not duplicated here since the source doc already states them well.

## Human review loop

Once real legal professionals review real AI answers: capture `{question, ai_answer, reviewer_decision, incorrect_claims, missing_sources, corrections}` and feed corrections back into the evaluation set, not just into prompt tweaks -- a wrong answer that gets fixed by prompt-tuning once and never becomes a regression test will likely come back.
