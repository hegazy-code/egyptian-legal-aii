"""Remove duplicate law rows, keeping the version with the most articles."""
import sys
from collections import defaultdict
sys.path.insert(0, "backend")

from app.database import SessionLocal
from app.models.legal import Law, Article

db = SessionLocal()
groups = defaultdict(list)
for law in db.query(Law).all():
    n = db.query(Article).filter(Article.law_id == law.id).count()
    groups[(str(law.law_number), law.year)].append((n, law))

removed = 0
for key, rows in groups.items():
    if len(rows) < 2:
        continue
    rows.sort(key=lambda x: x[0], reverse=True)
    keep = rows[0]
    print(f"{keep[1].title[:45]:47s} keep {keep[0]:5d} articles")
    for n, law in rows[1:]:
        print(f"{'':47s} drop {n:5d} articles")
        db.query(Article).filter(Article.law_id == law.id).delete()
        db.delete(law)
        removed += n

db.commit()
print("\nremaining laws:", db.query(Law).count())
print("remaining articles:", db.query(Article).count())
print("deleted articles:", removed)
db.close()