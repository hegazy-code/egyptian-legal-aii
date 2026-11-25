"""Add the reviewed first paragraph on disciplinary dismissal."""
from alembic import op
from sqlalchemy.orm import Session

from scripts.import_reviewed_legislation import import_records

revision = "a38d11ea930c"
down_revision = "f2d71fa3091d"
branch_labels = None
depends_on = None

RECORD = (
    "egypt-labor-14-2025-article-148",
    "قانون العمل رقم 14 لسنة 2025 — جزاء الفصل من العمل — المادة 148 (الفقرة الأولى)",
    "https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf#page=63",
    63, 63, "legislation",
    "يكون الاختصاص بتوقيع جزاء الفصل من العمل للمحكمة العمالية المختصة، "
    "ويكون توقيع باقي الجزاءات التأديبية لصاحب العمل، أو من يفوضه لذلك، "
    "ويكون لمدير المنشأة توقيع جزائي الإنذار الكتابي، والخصم من الأجر لمدة لا تجاوز ثلاثة أيام.",
)


def upgrade():
    with Session(bind=op.get_bind(), join_transaction_mode="rollback_only") as db:
        import_records(db, (RECORD,), extraction_method="reviewed_transcription")
        db.flush()


def downgrade():
    pass
