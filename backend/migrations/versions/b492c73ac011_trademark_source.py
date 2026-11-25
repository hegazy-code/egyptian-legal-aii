"""Add the reviewed trademark infringement source."""
from alembic import op
from sqlalchemy.orm import Session

from scripts.import_reviewed_legislation import import_records

revision = "b492c73ac011"
down_revision = "a38d11ea930c"
branch_labels = None
depends_on = None

RECORD = (
    "egypt-ip-82-2002-article-113",
    "قانون حماية حقوق الملكية الفكرية 82 لسنة 2002 — تقليد العلامات التجارية وبيع المنتجات — المادة 113",
    "https://www.wipo.int/wipolex/ar/legislation/details/22066",
    None, None, "legislation",
    "وفق المادة 113، تشمل صور التعدي تزوير علامة مسجلة أو تقليدها على نحو يضلل الجمهور، "
    "واستعمال العلامة المزورة أو المقلدة بسوء قصد، ووضع علامة الغير على المنتجات بسوء قصد. "
    "وتشمل كذلك بيع المنتجات التي تحمل علامة مزورة أو مقلدة أو موضوعة بغير حق أو عرضها "
    "أو حيازتها للبيع أو التداول مع العلم بذلك. يلزم التحقق من تسجيل العلامة وطريقة استخدامها "
    "وإثبات الواقعة قبل تحديد الإجراء المنطبق.",
)


def upgrade():
    with Session(bind=op.get_bind(), join_transaction_mode="rollback_only") as db:
        import_records(db, (RECORD,))
        db.flush()


def downgrade():
    pass
