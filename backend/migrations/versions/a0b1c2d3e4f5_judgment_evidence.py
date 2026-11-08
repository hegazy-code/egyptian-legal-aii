"""Add private review evidence table.

Revision ID: a0b1c2d3e4f5
Revises: 9f1a2b3c4d5e
"""
from alembic import op
import sqlalchemy as sa

revision = "a0b1c2d3e4f5"
down_revision = "9f1a2b3c4d5e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "judgment_evidence",
        sa.Column("judgment_id", sa.String(36), sa.ForeignKey("judgments.id"), nullable=False),
        sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source_url", sa.String(1000), nullable=False),
        sa.Column("independent_url", sa.String(1000), nullable=False),
        sa.Column("text_sha256", sa.String(64), nullable=False),
        sa.Column("source_excerpt", sa.Text(), nullable=False),
        sa.Column("independent_excerpt", sa.Text(), nullable=False),
        sa.Column("review_reason", sa.Text(), nullable=False),
        sa.Column("primary_sha256", sa.String(64), nullable=False),
        sa.Column("independent_sha256", sa.String(64), nullable=False),
        sa.Column("primary_fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("independent_fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verification_outcome", sa.String(30), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_judgment_evidence_id", "judgment_evidence", ["id"])
    op.create_index("ix_judgment_evidence_judgment_id", "judgment_evidence", ["judgment_id"])


def downgrade():
    op.drop_index("ix_judgment_evidence_judgment_id", table_name="judgment_evidence")
    op.drop_index("ix_judgment_evidence_id", table_name="judgment_evidence")
    op.drop_table("judgment_evidence")
