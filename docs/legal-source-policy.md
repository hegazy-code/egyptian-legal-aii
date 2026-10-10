# Legal Source Policy

## The trust hierarchy

Every source registered in `data/inventory/legal_sources.xlsx` gets a tier. This determines how it can be used in an answer.

- **Tier 1 -- Primary authoritative.** Official legislation text, Official Gazette (الجريدة الرسمية) material, official government/court publications.
- **Tier 2.** Official executive regulations, ministerial decisions, official circulars/instructions.
- **Tier 3.** Authenticated judicial decisions and court-stated principles.
- **Tier 4.** Academic commentary, legal books, articles.
- **Tier 5.** General websites, blogs, forums.

**Hard rule: the system must never present Tier 4/5 commentary as if it were law.** If the only material available is Tier 4/5, the answer must say so explicitly ("لم يتم التحقق من هذا المصدر كنص قانوني رسمي") rather than citing it as an article.

## Registered sources so far (v1 seed)

Four flagship laws, one per initial domain, verified at the *registry* level (law number, year, official Gazette issue/date, cross-checked against at least two independent sources) as of this write-up. **Article-level text has not been extracted yet** -- that's the explicit next step (see README Roadmap), done the same careful way as an earlier project on this account: fetch the actual page, extract text by direct slicing/parsing (never retype from memory), and store byte-identical.

| Domain | Law | Number/Year | Official Gazette | Primary source checked |
|---|---|---|---|---|
| Criminal | قانون العقوبات (Penal Code) | 58/1937 | الوقائع المصرية, Issue 71, 05/08/1937 | eastlaws.com |
| Civil | القانون المدني (Civil Code) | 131/1948 | الوقائع المصرية, Issue 108 مكرر, 29/07/1948 | eastlaws.com |
| Companies | قانون الشركات (Companies Law) | 159/1981 | -- (cross-checked across manshurat.org, laweg.net, draminlotfyoffice.com) | multiple, not yet eastlaws-confirmed |
| Consumer Protection | قانون حماية المستهلك | 181/2018 | -- (cross-checked across manshurat.org, laweg.net, lawhub.info) | multiple, not yet eastlaws-confirmed |

Full detail (source URLs, verification date) is in `data/inventory/legal_sources.xlsx`. The Companies and Consumer Protection rows still need an eastlaws.com (or equally authoritative) Gazette-level confirmation before being called fully Tier-1-verified the way the first two are -- flagged explicitly in the `Notes` column rather than glossed over.

## Trusted domain allowlist (for future live search)

Once live search is wired in (see README Roadmap -- currently deferred, no search provider is connected yet), it should be restricted to an allowlist, not open search:

- eastlaws.com -- official Gazette-text database
- manshurat.org -- legal publications
- WIPO Lex (wipo.int) -- for IP-adjacent commercial law
- draminlotfyoffice.com, lawyeregypt.net -- established Egyptian legal-practice publications, useful for cross-checking but Tier 4 unless they cite/mirror an official text
- Official government/ministry/court domains as identified (Court of Cassation's platform, moj.gov.eg, etc.) -- always Tier 1 when directly sourced

This list must stay small and vetted, not grow automatically. See the code-level allowlist file once search is implemented for the enforcement mechanism (a search provider's own domain restriction, if it has one, should never be the *only* enforcement -- verify server-side too, since not every provider's restriction is reliable).

## Data quality levels (applies to every document, once ingested)

`VERIFIED` / `PARTIALLY_VERIFIED` / `OCR_REVIEW_REQUIRED` / `UNVERIFIED` / `OUTDATED`. Only `VERIFIED` material should back an authoritative answer. This exact enum doesn't exist yet: `documents` has a `status` column today (`pending`/`processed`/`failed`, tracking ingestion state, not verification level) and `sources` has `reliability_score`/`source_type` but no dedicated verification-level field (see `backend/app/models/legal.py`). Adding a real `verification_status` column/enum to both, and gating retrieval on it, should happen before any real corpus goes live -- tracked as a TODO, not yet implemented.
