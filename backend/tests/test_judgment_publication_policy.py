"""Offline tests for publication gate; never call production."""
from app.services.judgment_publication_policy import PublicationPolicy, evaluate_publication


def complete_draft():
    return {
        "evidence": {
            "court": "محكمة النقض",
            "case_number": "123",
            "year": "90",
            "judgment_date_literal": "01/02/2020",
        },
        "contradictions": [],
        "blockers": [],
    }


def test_default_policy_blocks_even_fully_verified():
    result = evaluate_publication(
        complete_draft(),
        independent_verified_source_ids=["court", "gazette"],
        human_approved=True,
        source_authenticity_verified=True,
        citation_spans_verified=True,
        personal_data_cleared=True,
    )
    assert not result.eligible
    assert "automatic_publication_disabled" in result.blockers


def test_enabled_policy_still_requires_every_check():
    result = evaluate_publication(complete_draft(), policy=PublicationPolicy(auto_publish_enabled=True))
    assert not result.eligible
    assert "source_authenticity_unverified" in result.blockers


def test_duplicate_source_ids_do_not_count_as_independent():
    result = evaluate_publication(
        complete_draft(), policy=PublicationPolicy(auto_publish_enabled=True),
        independent_verified_source_ids=["same", "same"],
        human_approved=True, source_authenticity_verified=True,
        citation_spans_verified=True, personal_data_cleared=True,
    )
    assert not result.eligible
    assert "insufficient_independent_sources" in result.blockers


def test_all_approved_conditions_required():
    result = evaluate_publication(
        complete_draft(), policy=PublicationPolicy(auto_publish_enabled=True),
        independent_verified_source_ids=["court", "gazette"],
        human_approved=True, source_authenticity_verified=True,
        citation_spans_verified=True, personal_data_cleared=True,
    )
    assert result.eligible
    assert result.blockers == ()


def test_contradiction_blocks_even_when_other_checks_pass():
    draft = complete_draft()
    draft["contradictions"] = ["judgment_date_literal"]
    result = evaluate_publication(
        draft, policy=PublicationPolicy(auto_publish_enabled=True),
        independent_verified_source_ids=["court", "gazette"],
        human_approved=True, source_authenticity_verified=True,
        citation_spans_verified=True, personal_data_cleared=True,
    )
    assert not result.eligible
    assert "contradictory_sources" in result.blockers
