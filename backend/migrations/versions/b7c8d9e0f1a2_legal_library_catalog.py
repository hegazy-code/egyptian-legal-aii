"""Additive legal library tables. No existing records are modified."""
from alembic import op
import sqlalchemy as sa

revision = "b7c8d9e0f1a2"
down_revision = "a0b1c2d3e4f5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("library_assets",
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("external_file_id", sa.String(255), nullable=False),
        sa.Column("parent_external_id", sa.String(255), nullable=True),
        sa.Column("original_path", sa.Text(), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source_url", sa.String(1200), nullable=True),
        sa.Column("mime_type", sa.String(150), nullable=True),
        sa.Column("byte_size", sa.Integer(), nullable=True),
        sa.Column("sha256", sa.String(64), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("extraction_status", sa.String(30), nullable=False),
        sa.Column("review_status", sa.String(30), nullable=False),
        sa.Column("rights_status", sa.String(30), nullable=False),
        sa.Column("source_document_id", sa.String(36), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_library_assets_id", "library_assets", ["id"])
    op.create_table("library_text_chunks",
        sa.Column("asset_id", sa.String(36), sa.ForeignKey("library_assets.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("extraction_method", sa.String(40), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_library_text_chunks_id", "library_text_chunks", ["id"])
    op.create_table("legal_commentaries",
        sa.Column("asset_id", sa.String(36), sa.ForeignKey("library_assets.id"), nullable=False),
        sa.Column("article_id", sa.String(36), sa.ForeignKey("articles.id"), nullable=True),
        sa.Column("judgment_id", sa.String(36), sa.ForeignKey("judgments.id"), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("page_reference", sa.String(100), nullable=True),
        sa.Column("review_status", sa.String(30), nullable=False),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_legal_commentaries_id", "legal_commentaries", ["id"])
    op.create_table("appeal_records",
        sa.Column("judgment_id", sa.String(36), sa.ForeignKey("judgments.id"), nullable=True),
        sa.Column("asset_id", sa.String(36), sa.ForeignKey("library_assets.id"), nullable=True),
        sa.Column("procedure_type", sa.String(40), nullable=False),
        sa.Column("filing_number", sa.String(100), nullable=True),
        sa.Column("filing_year", sa.Integer(), nullable=True),
        sa.Column("filing_date", sa.Date(), nullable=True),
        sa.Column("outcome", sa.String(100), nullable=True),
        sa.Column("grounds", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(30), nullable=False),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_appeal_records_id", "appeal_records", ["id"])
    op.create_table("legal_templates",
        sa.Column("asset_id", sa.String(36), sa.ForeignKey("library_assets.id"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("template_type", sa.String(60), nullable=False),
        sa.Column("jurisdiction", sa.String(80), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("required_fields_json", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(30), nullable=False),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_legal_templates_id", "legal_templates", ["id"])
    op.create_unique_constraint("uq_library_asset_provider_file", "library_assets", ["provider", "external_file_id"])
    op.create_index("ix_library_asset_category_status", "library_assets", ["category", "review_status"])
    op.create_unique_constraint("uq_library_chunk_index", "library_text_chunks", ["asset_id", "chunk_index"])


def downgrade():
    raise RuntimeError("Downgrade is intentionally blocked to prevent deleting imported legal library records")
