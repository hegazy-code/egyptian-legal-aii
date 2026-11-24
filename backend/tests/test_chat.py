"""Regression tests for the current public /chat API contract.

POST /chat accepts question/conversationId and is intentionally available to guests.
Authenticated conversation-history endpoints remain private.
"""


def test_chat_without_gemini_key_returns_grounded_fallback(client):
    resp = client.post("/chat", json={"question": "ما حكم المادة 1 من القانون المدني؟"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["conversationId"]
    assert isinstance(body["answer"], dict)
    assert body["answer"]["disclaimer"]


def test_chat_creates_and_reuses_guest_conversation(client):
    first = client.post("/chat", json={"question": "ما هو نظام الإيجار في مصر؟"})
    assert first.status_code == 200, first.text
    conv_id = first.json()["conversationId"]
    assert conv_id

    second = client.post(
        "/chat",
        json={"question": "وما هي المدة القانونية؟", "conversationId": conv_id},
    )
    assert second.status_code == 200, second.text
    assert second.json()["conversationId"] == conv_id


def test_chat_rejects_missing_question(client):
    resp = client.post("/chat", json={"message": "test"})
    assert resp.status_code == 422


def test_conversation_history_requires_auth(client):
    resp = client.get("/conversations")
    assert resp.status_code == 401


def test_chat_includes_reviewed_library_source_in_fallback(client):
    from app.database import SessionLocal
    from app.models.library_catalog import LibraryAsset, LibraryTextChunk

    with SessionLocal.begin() as db:
        asset = LibraryAsset(
            provider="google_drive",
            external_file_id="chat-citation-example",
            title="قانون العمل رقم ١٤ لسنة ٢٠٢٥",
            source_url="https://example.org/gazette.pdf",
            category="legislation",
            review_status="verified",
            rights_status="cleared",
        )
        db.add(asset)
        db.flush()
        db.add(LibraryTextChunk(
            asset_id=asset.id,
            chunk_index=0,
            page_start=5,
            text="مقتطف تجريبي عن تاريخ تطبيق قانون العمل",
            verified=True,
        ))
    resp = client.post("/chat", json={"question": "متى بدأ تطبيق قانون العمل رقم 14 لسنة 2025؟"})
    assert resp.status_code == 200, resp.text
    sources = resp.json()["answer"]["answerSources"]
    source = next(s for s in sources if s["sourceUrl"] == "https://example.org/gazette.pdf")
    assert source["status"] == "verified"
    assert source["lawName"].endswith("(ص. 5)")
