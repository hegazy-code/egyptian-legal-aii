# Automated Case Library — Milestone 1 (development only)

Branch: `feature/case-library-ingestion-m1`. **No production deployment or database changes.**

## Scope and integration boundary

- `cases` is a user's private legal matter. NEVER import court judgments into this table.
- `judgments` is the existing public-corpus model. Its current default status is `published`; every new automated record MUST explicitly use `draft` and publication queries must exclude drafts.
- `documents` and `sources` support legal corpus provenance.
- Existing admin endpoints currently appear imported but not mounted in `app/main.py`. Admin approval integration remains pending.

## Implemented foundation

`app/services/judgment_discovery.py` provides explicit opt-in HTTPS host allowlists, HTML link discovery and retrieval, content hash, literal-field extraction with source URL and excerpt, duplicate detection, contradiction flags, draft payloads, and fail-closed eligibility. No network operation runs unless an enabled source is supplied. No database writes, AI calls, scheduler, or publication endpoint are implemented.

## Known limitations / blockers

1. **No verified source catalog or 10 real court judgments ingested yet.** Offline fixtures are synthetic and must not be reported as real judgment results.
2. HTML-only retrieval; PDFs, scanned rulings, OCR, pagination, Arabic-Indic digit conversion and judicial metadata variants remain unsupported.
3. Source host allowlists are not a complete SSRF defense: use outbound network restrictions and DNS/IP validation before deploying a worker.
4. Source comparison currently flags mismatched values but cannot independently authenticate legal content.
5. Full Arabic case summaries are intentionally absent rather than invented; require grounded extraction and legal review.
6. Deduplication is in-memory per batch only; database uniqueness and concurrency protection require a migration.
7. Existing Judgment schema lacks citation spans, verification status, review decisions, and an immutable publication audit. Add migrations after approval.
8. No administrator-controlled publishing switch or immediate unpublish endpoint yet. Publishing remains impossible from this module.
9. Render has two free web services (Next.js and FastAPI) on `main`, both with auto-deploy enabled. Development branch commits do not trigger their main-branch deployment. No dedicated background worker identified.
10. Render API build command runs Alembic migrations on deployment. Review migrations and database backups before any production rollout.

## Acceptance criteria for next phase

- Identify and license/permission-check authoritative public Egyptian judgment sources.
- Fetch 10 real judgments into a quarantined, local-only test dataset; preserve URLs, timestamps, content hashes and raw evidence.
- Review extraction accuracy, duplicate clusters, contradictory fields, and missing citations per judgment.
- Build isolated judgment draft storage and admin approval UI/API with role checks, explicit state transitions, append-only audit and unpublish.
- Implement feature flag default OFF; independent approval of deterministic publication policy and integration tests before enabling.
- Use a scheduled worker only after confirming Render resource limits and outbound-network safeguards.

## Running offline tests

From `backend/`, install project dependencies plus pytest, then run:

```sh
python -m pytest tests/test_judgment_discovery.py -q
```

Tests have been added to the branch but have **not been executed by the connected GitHub tool**. No claim of 10 real judgments tested is made.
