# Data Policy

## Versioning philosophy

A law's text changes over time via amendment. The schema (see `backend/app/models/legal.py`) separates `laws`/`law_versions` and `articles`/`article_versions` specifically so a question like "what did this article say in 2015?" can be answered correctly instead of silently returning today's text. Every `article_versions` row has `effective_from`/`effective_to`/`status`/`amending_law_id` -- **not yet populated with real history** for any of the 4 registered laws (that requires the article-level extraction work in the Roadmap), but the schema is ready for it now rather than needing a migration later.

## Provenance -- every fact needs an audit trail

For any legal text to be used in an answer, the system should be able to answer: where did it come from, when did we get it, who issued it, which document/page/article/version. This is why `article_versions.source_document_id` is a foreign key, not a free-text field, and why raw source documents (once collected) get a `sha256` hash recorded alongside their metadata -- so a later re-check can confirm the stored text still matches what was actually published, not a rewritten copy.

## What never gets committed to git

Per `.gitignore`: `data/raw/`, `data/processed/`, `data/ocr/`, `data/validated/` are excluded (kept only as empty dirs via `.gitkeep`). Large legal corpora and any user-uploaded documents don't belong in version control -- they belong in object storage (S3-compatible, TBD) once there's real volume, and locally on disk for now. `data/inventory/` (the source *registry*, not the documents themselves) is small and text-based, so it stays in git.

## Retention (user data, once accounts exist)

Not yet relevant -- no real user accounts are in production use. Before that changes: a documented retention period for conversations/uploaded documents, a real account-deletion path that actually removes (not just soft-hides) personal data, and a privacy policy reviewed under Egyptian law (see `docs/security.md`). Tracked as a pre-launch blocker, not solved by this skeleton.

## Data quality levels

See `docs/legal-source-policy.md#data-quality-levels` -- lives there since it's really about source trust, not storage mechanics.
