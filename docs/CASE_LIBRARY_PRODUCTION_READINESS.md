# Phase 1 — production readiness gate (2026-11-07)

**Status: NOT CLEARED FOR PRODUCTION.** Do not merge, deploy, enable auto-publication, or publish any judgment on the strength of the test suite alone.

## Verified technical baseline

- GitHub Actions run 42379646464: 60 tests passed, fresh SQLite migrations through a0b1c2d3e4f5 succeeded, Python compile and offline source inspection passed.
- Later changes require a new successful CI run.
- Admin staging and approval are not publication: public keyword search requires status `published`, and no publish endpoint is authorized.
- Trusted HTTPS evidence hosts require explicit allowlisting (`JUDGMENT_VERIFIED_EVIDENCE_HOSTS`).
- Each host must map to a **distinct independently verified publisher operator** using `JUDGMENT_EVIDENCE_PUBLISHER_IDS` JSON. Example for TESTS ONLY: `{"court.example.org":"court-operator","publisher.example.org":"independent-publisher"}`. An absent, malformed, or shared identity fails closed. Domain-name differences alone do not prove independent ownership.

## Mandatory release blockers

1. **Provenance:** identify genuine primary Egyptian judicial publishers, verify domain control and court authenticity, confirm independent secondary operators and legal rights to retrieve, store and republish texts. Record provenance evidence and source permissions. Never invent case records.
2. **Legal/privacy:** obtain Egyptian legal review of personal-data handling, anonymization/redaction, publication permissions, takedown procedures, and retention. A checkbox alone is not a privacy audit.
3. **Security:** independent threat-model and penetration review of SSRF/DNS/TLS, administrator authorization, audit logs, malicious HTML, and evidence storage. Ensure archived raw evidence is securely retained if audit reproducibility is required.
4. **Database:** backed-up PostgreSQL staging migration and rollback rehearsal with representative existing records; resolve duplicates manually before applying the unique index.
5. **E2E:** authenticated HTTP tests for admin/non-admin access, stage/approve/unpublish, search exclusion and failure behavior, including concurrency and source outages.
6. **Acceptance:** a legally cleared sample of authentic Egyptian judgments with reproducible citations and review evidence; human sign-off from responsible legal reviewer and project owner.
7. **Release:** green CI on final SHA, documented deployment and rollback plan, owner authorization. Explicitly opt in to any future public publishing mechanism; default remains disabled.

**No production changes are authorized by this document.**
