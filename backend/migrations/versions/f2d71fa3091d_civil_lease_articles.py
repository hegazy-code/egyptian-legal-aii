"""Add the reviewed full texts of Civil Code articles 598 to 600."""
from alembic import op
from sqlalchemy.orm import Session

from scripts.import_reviewed_legislation import import_records

revision = "f2d71fa3091d"
down_revision = "e1c60e702f0c"
branch_labels = None
depends_on = None

SOURCE = "https://www.eta.gov.eg/sites/default/files/2024-10/law-131-1948.pdf#page=48"
ARTICLES = {
    598: "ينتهي الإيجار بانتهاء المدة المعينة في العقد دون حاجة إلى تنبيه بالإخلاء.",
    599: (
        "(1) إذا انتهى عقد الإيجار وبقي المستأجر منتفعًا بالعين المؤجرة بعلم المؤجر ودون اعتراض منه، "
        "اعتبر الإيجار قد تجدد بشروطه الأولى ولكن لمدة غير معينة، وتسري على الإيجار إذا تجدد على هذا الوجه أحكام المادة 563.\n"
        "(2) ويعتبر هذا التجديد الضمني إيجارًا جديدًا لا مجرد امتداد للإيجار الأصلي، ومع ذلك تنتقل إلى الإيجار الجديد "
        "التأمينات العينية التي كان المستأجر قد قدمها في الإيجار القديم مع مراعاة قواعد الشهر العقاري، "
        "أما الكفالة شخصية كانت أو عينية فلا تنتقل إلى الإيجار الجديد إلا إذا رضي الكفيل بذلك."
    ),
    600: (
        "إذا نبه أحد الطرفين على الآخر بالإخلاء واستمر المستأجر مع ذلك منتفعًا بالعين بعد انتهاء الإيجار "
        "فلا يفترض أن الإيجار قد تجدد ما لم يقم الدليل على عكس ذلك."
    ),
}


def upgrade():
    records = tuple(
        (f"egypt-civil-131-1948-article-{number}",
         f"القانون المدني 131 لسنة 1948 — انتهاء الإيجار — المادة {number}",
         SOURCE, 48, 48, "legislation", text)
        for number, text in ARTICLES.items()
    )
    with Session(bind=op.get_bind(), join_transaction_mode="rollback_only") as db:
        import_records(db, records, extraction_method="reviewed_transcription")
        db.flush()


def downgrade():
    pass
