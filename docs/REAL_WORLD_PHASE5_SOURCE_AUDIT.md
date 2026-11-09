# Phase 5 — primary-source audit (2026-11-09)

## Scope
Independent `/real-world` story section (10 records). Do **not** confuse it with the judicial judgment library `/cases`.

## Evidence obtained
- Official Court of Cassation search portal: https://cc.gov.eg/judgments_search/ — verified as a genuine primary-source discovery route. No exact full-text judgment matching one of the ten stories was retrieved and authenticated in this audit.
- Official Supreme Constitutional Court: https://www.sccourt.gov.eg/newportal/ — genuine source, but constitutional decisions are **not substitutes** for the criminal judgments behind these documentary stories.
- Al-Ahram report dated 2025-11-02: https://gate.ahram.org.eg/News/5316336.aspx — reports Cassation dismissal of the 10-year appeal in the linked case, gives docket 5464/95 and **attributes** counsel's procedural objections to the defense.
- Al-Shorouk report dated 2024-05-04: https://www.shorouknews.com/news/view.aspx?cdate=04052024&id=23a64418-5eb3-4f81-b893-7cb4120ddfe1 — reproduces prosecutor statement, trial outcome, defense requests in Arish case. It documents **privacy/blackmail charges**, not a murder conviction against the students.

## Audit result
- 10/10 records: primary full-judgment match **NOT VERIFIED**.
- 2/10 records: direct reading of accessible reporting for selected claims in this phase (IDs 9, 10).
- 1 substantive correction: Arish story must not be framed as adjudicated murder.
- The remaining press links were not individually confirmed reachable in this phase. Prior status `press_cross_checked` reflects earlier editorial work, **not** official judicial verification.
- Render frontend deploy of commit `14fe41185b0fc581f7f16fa25cac269e1cdb2025` was `live` at 2026-11-09T20:49:33Z, per Render deploy API. This proves deployment status, **not** successful page rendering or browser interaction. Web fetch of `/real-world` returned an internal access error; browser UI testing remains unverified.

## Release gate for each story
1. Locate exact court/docket/judicial year/date and original published decision from official or authorized court database.
2. Match parties (where publicly reported), offense, procedural history, dispositive holding, and appeal outcome to primary text.
3. Attribute prosecution and defense claims to their source; don't turn allegations into findings.
4. Preserve source URL, source type, publication date, retrieved date, quotation/paraphrase evidence and any discrepancies.
5. Check every public URL for live destination and topical match.
6. If original decision is unavailable, display `press-sourced; official judgment unverified` and never label as fully judicially verified.
7. Run actual frontend build and live UI navigation tests before claiming end-to-end QA.

## Next source leads
Search https://cc.gov.eg/judgments_search/ for known docket references including Naira Ashraf 15991/92 and Um Shahd 5464/95. Treat those numbers as **press-reported leads**, not court-verified identifiers until matched.
