# Legal library catalog — import staging

This branch is **not** a production database deployment. The seven `data/inventory/drive_batch_*.json` files contain direct children of the 84 top-level Drive folders only. Nested folders and provider-capped listings are incomplete. They contain metadata, not document text. Every record defaults to `unclassified` and `unverified`.

## Before applying anything
1. Back up the existing database and verify its current Alembic revision and deployment configuration.
2. Apply migration `b7c8d9e0f1a2` **only to a test database first**.
3. Run tests: `cd backend && pytest tests/test_library_inventory.py`.
4. Validate each batch without writing: `cd backend && python -m scripts.import_library_inventory ../data/inventory/drive_batch_01.json --dry-run`.
5. After staging verification, import each batch with `--apply`. Re-running is idempotent by provider + external file ID; existing entries and human reviews are left untouched.
6. Expand the manifest recursively, resolve capped folders, extract text with page-level traceability, and verify legal status and rights before enabling retrieval.

## Data separation
- `library_assets`: source file metadata, extraction/review/rights status.
- `library_text_chunks`: text fragments with page references; `verified=False` initially.
- `legal_commentaries`: secondary scholarship linked to law articles or judgments.
- `appeal_records`: appeals, cassation, and petitions for reconsideration.
- `legal_templates`: pleadings, contracts, notices, and procedural examples.

**Do not feed unverified chunks or secondary commentary to the answer engine as binding Egyptian law.** The existing `/admin/reindex` endpoint is not implemented. No search functionality is activated by these schema changes.

The migration downgrade intentionally blocks destructive drops. No existing legal content is deleted by the upgrade.
