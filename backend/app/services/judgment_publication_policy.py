"""Publication policy for court judgments: fail closed, no side effects.

This module does NOT publish, write to a database, or change API routes.
It is intentionally independent of Gemini and user-uploaded private cases.
"""
from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class PublicationPolicy:
    auto_publish_enabled: bool = False
    minimum_independent_sources: int = 2
    require_human_approval: bool = True


@dataclass(frozen=True)
class PublicationDecision:
    eligible: bool
    blockers: tuple[str, ...]


REQUIRED_FIELDS = ("court", "case_number", "year", "judgment_date_literal")


def evaluate_publication(
    draft: Mapping,
    *,
    policy: PublicationPolicy = PublicationPolicy(),
    independent_verified_source_ids: Sequence[str] = (),
    human_approved: bool = False,
    source_authenticity_verified: bool = False,
    citation_spans_verified: bool = False,
    personal_data_cleared: bool = False,
    duplicate_in_database: bool = False,
) -> PublicationDecision:
    """Return a deterministic decision. Never trust LLM-provided eligibility."""
    blockers: list[str] = []
    evidence = draft.get("evidence") or {}
    for field in REQUIRED_FIELDS:
        if not evidence.get(field):
            blockers.append(f"missing_{field}")
    if draft.get("contradictions"):
        blockers.append("contradictory_sources")
    if "duplicate_judgment" in draft.get("blockers", ()) or duplicate_in_database:
        blockers.append("duplicate_judgment")
    if not source_authenticity_verified:
        blockers.append("source_authenticity_unverified")
    if not citation_spans_verified:
        blockers.append("citation_spans_unverified")
    if not personal_data_cleared:
        blockers.append("personal_data_not_cleared")
    if len(set(independent_verified_source_ids)) < policy.minimum_independent_sources:
        blockers.append("insufficient_independent_sources")
    if policy.require_human_approval and not human_approved:
        blockers.append("human_approval_required")
    if not policy.auto_publish_enabled:
        blockers.append("automatic_publication_disabled")
    return PublicationDecision(not blockers, tuple(blockers))
