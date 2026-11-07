# Egyptian Legal AI — Court Judgment Library Release Checklist

**Owner:** project maintainer. **Branch:** `feature/case-library-ingestion-m1`. **Last review:** 2026-11-07.
**Goal:** A trustworthy Egyptian judgment library that discovers real judgments, preserves provenance, verifies identity and legal citations, supports admin review, and publishes only authorized, approved records. Existing user cases, legal Q&A and production must continue working.

## Status key
- [x] Implemented in development branch (NOT proof of passing tests).
- [ ] Not completed or not independently verified.
- **BLOCKED** means an external prerequisite exists. Never substitute fabricated evidence.

## 0 — Release safety (mandatory)
- [x] Work isolated on feature branch; no main merge or production deployment.
- [x] New judgment records default to `draft`.
- [x] Public keyword judgment search restricts results to `published`.
- [ ] Audit *every* public read path (search, hybrid search, chat/RAG, documents, admin APIs, direct IDs) for unpublished-judgment leaks.
- [ ] Verify database backup/restore and migration rollback on a staging database.
- [ ] Require explicit owner authorization before merging, deploying, enabling a scheduler or publishing any judgment.

## 1 — Backend correctness and security
- [x] HTTPS source allowlist and bounded HTML fetch; redirects rejected.
- [x] Hash evidence; extract literal case identifiers; flag duplicate batches and contradictory fields.
- [x] Admin-only draft, approve, list and unpublish endpoints; audit entries written in same transaction.
- [x] Judicial-year values below 1800 supported; Arabic/Persian digits normalized during extraction.
- [x] Harden evidence URLs against credentials, IP literals, malformed hosts and custom ports.
- [x] Require registered court identity on new drafts and scope application-level duplicate checks by court, case number and year. Judgment date remains pending.
- [x] Require judgment date and add database unique index plus Alembic migration (not executed yet).
- [ ] Test both migrations on a backed-up staging database; resolve any pre-existing duplicates before applying.
- [x] Record staged and approved judgment text SHA-256 fingerprints in existing admin audit logs.
- [x] Add private persistent reviewer evidence model and migration; approval saves two reviewer-supplied excerpts, URLs, reviewer and judgment text fingerprint in one transaction.
- [ ] Independently retrieve and authenticate source content, preserve immutable source hashes/retrieval timestamps and precise citation spans; reviewer assertions alone are insufficient.
- [ ] Require independent *content* verification, not just distinct hostnames and reviewer-supplied Boolean flags.
- [ ] Make database-level deduplication concurrency-safe, with migration.
- [ ] Add DNS resolution/IP-range and outbound egress controls before networked ingestion in production.
- [ ] Review rate limits, admin permissions, audit access and safe error handling.
- [ ] Review failure/retry behavior and transaction rollback for each API transition.

## 2 — Verified Egyptian legal sources (BLOCKED on source/rights checks)
- [x] Candidate registry exists; all candidates disabled by default.
- [ ] Verify authoritative court endpoints and their current accessibility.
- [ ] Review terms, permissions and robots restrictions before automated retrieval/republication.
- [ ] Collect **10 real** judgments with original URLs, retrieval time, raw evidence, hashes and independent corroboration; no guessed URLs counted.
- [ ] Manually verify court, case number, judicial year, decision date, operative text and citation against original source.
- [ ] Quarantine incomplete, contradictory, duplicate or rights-restricted records.

## 3 — Ingestion pipeline
- [x] Opt-in HTML discovery/retrieval and draft preparation are implemented.
- [ ] Support official PDF judgments and multi-page results where authorized.
- [ ] Add document format detection and safe extraction; OCR only when essential and quality-checked.
- [ ] Build persistent ingestion queue with retries, backoff, deduplication and idempotency.
- [ ] Persist source failures and verification exceptions; do not silently skip.
- [ ] Keep AI-generated summaries separate from source text, clearly labeled and human-reviewed.

## 4 — Admin workflow and publishing controls
- [x] Admin can stage, approve and unpublish; approval alone does not publish.
- [ ] Admin dashboard displays source documents, provenance, conflicts, citation evidence and audit history.
- [ ] Add explicit, authenticated, audited publish transition with strict persisted prerequisites.
- [ ] Feature flag defaults OFF; publishing cannot occur through draft ingestion or review alone.
- [ ] Test emergency unpublish removes judgment from every public search/cache/RAG path.
- [ ] Define re-review and re-publication rules after source changes or legal corrections.

## 5 — Tests and release quality
- [x] Offline unit/regression tests (including evidence/uniqueness) and GitHub Actions workflow committed; not yet executed successfully.
- [ ] **Run** backend tests in a working CI/local environment and capture a green result; clone attempt on 2026-11-07 failed due to DNS resolution of github.com.
- [ ] Run formatting/static analysis, dependency/security checks and database migration tests.
- [ ] Test admin/non-admin authorization, malicious URLs, concurrent duplicates, malformed documents and API failures.
- [ ] Test public search/chat for all statuses: draft, approved, unpublished, published.
- [ ] End-to-end test frontend → API → database → admin approval → controlled publish → public search → unpublish.
- [ ] Verify no regression to existing legal Q&A, private cases, authentication and document uploads.
- [ ] Validate production-like staging logs, performance, backups and rollback.

## 6 — Release gate
- [ ] Ten authentic verified judgments with documented publication rights.
- [ ] All critical/high security defects resolved; tests and E2E passing.
- [ ] Admin sign-off on content, source rights and citation accuracy.
- [ ] Owner explicitly authorizes production release and publication switch.
- [ ] Deploy with rollback available, observe health/error metrics and perform smoke tests.

## Current release verdict: **NOT READY**
Reasons: tests not confirmed passing; no ten verified real judgments; evidence/verification and publishing workflow incomplete; no staging E2E. This checklist is a work plan, not a claim of completion.

## Execution order
1. Close backend/public visibility/security gaps and execute CI.
2. Verify official sources and rights; collect ten authentic records.
3. Complete durable ingestion, verification storage and admin review.
4. Complete explicit publication control, UI and end-to-end tests.
5. Obtain owner sign-off; only then release.
