"""Quarantined SCC candidate runner. Explicit opt-in; never writes DB or publishes.

Usage (from backend/):
  python scripts/inspect_scc_candidates.py --offline
  python scripts/inspect_scc_candidates.py --fetch --output /tmp/scc-review.json

Network access must be authorized by operator after rights and access review.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx

from app.services.judgment_discovery import Evidence, SourceConfig, prepare_draft, retrieve, run_batch

CANDIDATES = ROOT / "data" / "scc_ten_judgment_candidates.json"


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline", action="store_true")
    mode.add_argument("--fetch", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    if args.offline:
        print(json.dumps({"count": len(manifest["documents"]), "status": "candidate_only", "downloaded": 0, "published": 0}, ensure_ascii=False))
        return

    if not args.output:
        parser.error("--output is required for --fetch")
    source = SourceConfig(
        name="المحكمة الدستورية العليا",
        index_url="https://www.sccourt.gov.eg/",
        allowed_hosts=("www.sccourt.gov.eg",),
        enabled=True,
    )
    results = []
    with httpx.Client(headers={"User-Agent": "EgyptianLegalAI-Research/0.1 (manual review)"}) as client:
        for candidate in manifest["documents"]:
            try:
                evidence = retrieve(candidate["url"], source, client)
                draft = prepare_draft(evidence)
                results.append({"candidate_id": candidate["id"], "status": "retrieved", "text_length": len(evidence.text), "result": draft})
            except (httpx.HTTPError, ValueError, UnicodeError) as exc:
                results.append({"candidate_id": candidate["id"], "status": "retrieval_failed", "error_type": type(exc).__name__, "http_status": exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None, "reason": str(exc)[:300]})
    # No DB integration. Output remains a review artifact, not a publication queue.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"published": 0, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {"checked": len(results), "retrieved": sum("result" in r for r in results), "published": 0, "failure_types": dict(Counter(r.get("error_type", "none") for r in results if r["status"] == "retrieval_failed"))}
    print(json.dumps(summary, ensure_ascii=False))
    if summary["retrieved"] == 0:
        raise SystemExit("No official documents retrieved; see quarantined review report")


if __name__ == "__main__":
    main()
