"""Enforce unique court/case/year identities for identifiable judgments.

Preflight checks existing duplicates. Resolve them manually before migration;
never silently delete or merge judicial records.
"""
from alembic import op
import sqlalchemy as sa

revision = "9f1a2b3c4d5e"
down_revision = "8d08516be53d"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    duplicates = conn.execute(sa.text("""
        SELECT court_id, case_number, year, COUNT(*) AS total
        FROM judgments
        WHERE court_id IS NOT NULL AND case_number IS NOT NULL AND year IS NOT NULL
        GROUP BY court_id, case_number, year
        HAVING COUNT(*) > 1
        LIMIT 1
    """)).first()
    if duplicates:
        raise RuntimeError(
            "Existing duplicate court/case/year judgments; resolve and back up before migrating"
        )
    op.create_index(
        "uq_judgment_court_case_year",
        "judgments",
        ["court_id", "case_number", "year"],
        unique=True,
    )


def downgrade():
    op.drop_index("uq_judgment_court_case_year", table_name="judgments")
