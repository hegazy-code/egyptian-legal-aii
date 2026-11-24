"""Add reviewed Civil Code guidance on ending a fixed-term lease."""
from alembic import op
from sqlalchemy.orm import Session

from scripts.import_reviewed_legislation import import_records

revision = "e1c60e702f0c"
down_revision = "c8da12ea019b"
branch_labels = None
depends_on = None

LEASE = (
    "egypt-civil-fixed-term-lease-147-598",
    "القانون المدني 131 لسنة 1948 — الإيجار محدد المدة والإخلاء (المادتان 147 و598)",
    "https://www.eta.gov.eg/sites/default/files/2024-10/law-131-1948.pdf",
    None,
    None,
    "legislation",
    "إذا كانت الشقة مؤجرة بعقد إيجار محدد المدة يخضع للقانون المدني، فالأصل أن العقد يلزم الطرفين (المادة 147) وينتهي بانقضاء المدة المتفق عليها (المادة 598). مجرد طلب صاحب الشقة الإخلاء أو الطرد قبل أن يخلص العقد لا يكفي لإنهائه. قد تختلف النتيجة إذا وُجد اتفاق على الإنهاء أو سبب قانوني للفسخ أو شرط ينطبق على الواقعة. يلزم مراجعة تاريخ انتهاء العقد وسبب طلب الإخلاء وأي إخلال بالالتزامات، والتأكد من النظام القانوني الذي يخضع له الإيجار.",
)


def upgrade():
    with Session(bind=op.get_bind(), join_transaction_mode="rollback_only") as db:
        import_records(db, (LEASE,))
        db.flush()


def downgrade():
    pass
