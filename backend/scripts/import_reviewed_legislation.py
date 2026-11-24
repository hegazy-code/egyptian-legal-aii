"""Import source-checked gazette summaries without changing existing records."""
import argparse

from sqlalchemy import select

from app.database import SessionLocal
from app.models.library_catalog import LibraryAsset, LibraryTextChunk


RECORDS = (
    (
        "gazette-18-supplement-2025-05-03-law-14",
        "قانون العمل رقم 14 لسنة 2025 — المادتان الثانية عشرة والثالثة عشرة من مواد الإصدار",
        "https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf#page=5",
        5,
        5,
        "legislation",
        "ألغت المادة الثانية عشرة قانون العمل رقم 12 لسنة 2003. وبموجب المادة الثالثة عشرة، بدأ سريان قانون العمل رقم 14 لسنة 2025 في 1 سبتمبر 2025، وبدأ تطبيق الأحكام الخاصة بالمحاكم العمالية المتخصصة في 1 أكتوبر 2025.",
    ),
    (
        "gazette-39-b-2026-09-30-160",
        "قانون 160 لسنة 2026 — تعديل المادة السادسة من مواد إصدار قانون الإجراءات الجنائية 174 لسنة 2025",
        "https://www.alamiria.com/Sec/TashTxt?id=Aalg37zxdcU%3D",
        None,
        None,
        "legislation",
        "حددت المادة الأولى من القانون 160 لسنة 2026 تاريخ بدء العمل بقانون الإجراءات الجنائية 174 لسنة 2025 في 1 أكتوبر 2027. أما القانون المعدِّل 160 لسنة 2026 نفسه، فبدأ العمل به في 1 أكتوبر 2026، في اليوم التالي لنشره في الجريدة الرسمية وفق المادة الثانية.",
    ),
    (
        "cassation-17064-88-2021-10-24",
        "محكمة النقض الجنائية — الطعن 17064 لسنة 88 قضائية، جلسة 24 أكتوبر 2021، تقدير شهادة شاهد الإثبات",
        "https://register.cc.gov.eg/publications/152/download#page=188",
        188,
        189,
        "judgment",
        "في المحاكمة الجنائية، الخصومة السابقة مع شاهد الإثبات أو تأخر الشاهد في الإبلاغ لا يمنعان محكمة الموضوع من الاعتماد على شهادته إذا اطمأنت إليها. ويظل تقدير وزن الشهادة من سلطة محكمة الموضوع متى كان استخلاصها سائغاً وله أصل في الأوراق.",
    ),
)


def import_records(db, records=RECORDS) -> int:
    inserted = 0
    for external_id, title, url, page, page_end, category, summary in records:
        existing = db.scalar(select(LibraryAsset.id).filter_by(
            provider="official", external_file_id=external_id,
        ))
        if existing:
            continue
        asset = LibraryAsset(
            provider="official",
            external_file_id=external_id,
            title=title,
            source_url=url,
            category=category,
            review_status="verified",
            rights_status="cleared",
            extraction_status="extracted_unverified",
        )
        db.add(asset)
        db.flush()
        db.add(LibraryTextChunk(
            asset_id=asset.id,
            chunk_index=0,
            page_start=page,
            page_end=page_end,
            text=summary,
            extraction_method="reviewed_summary",
            verified=True,
        ))
        inserted += 1
    return inserted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        for external_id, title, url, *_ in RECORDS:
            print(f"{external_id}: {title} — {url}")
        return
    with SessionLocal.begin() as db:
        inserted = import_records(db)
    print(f"Inserted {inserted} reviewed official summaries")


if __name__ == "__main__":
    main()
