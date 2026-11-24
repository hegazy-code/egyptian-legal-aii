"""Add the three reviewed official sources to the existing library."""
from alembic import op
from sqlalchemy.orm import Session

from scripts.import_reviewed_legislation import import_records

revision = "c8da12ea019b"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None


def upgrade():
    with Session(bind=op.get_bind(), join_transaction_mode="rollback_only") as db:
        import_records(db)
        db.flush()


def downgrade():
    # Reviewed source records are preserved on rollback.
    pass
