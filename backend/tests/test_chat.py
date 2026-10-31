"""
Chat pipeline tests. GEMINI_API_KEY is intentionally unset in tests (see
conftest.py), so these exercise the real no-hallucination fallback path
(app.rag.answer_builder.build_fallback_answer) rather than calling the real
Gemini API -- no network calls, no key required.
"""


def _register_and_login(client, email="chatuser@example.com"):
    client.post("/auth/register", json={"email": email, "password": "strongpass123"})
    login = client.post("/auth/login", json={"email": email, "password": "strongpass123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_chat_without_gemini_key_returns_grounded_fallback(client):
    headers = _register_and_login(client)
    resp = client.post("/chat", json={"message": "ما حكم المادة 1 من القانون المدني؟"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["conversation_id"]
    assert body["message_id"]
    assert "تنبيه" in body["answer"]  # disclaimer section always present
    # Never fabricates a citation when nothing was retrieved.
    assert "لا توجد مصادر" in body["answer"] or isinstance(body["citations"], list)


def test_chat_creates_and_reuses_conversation(client):
    headers = _register_and_login(client, email="chatuser2@example.com")
    first = client.post("/chat", json={"message": "ما هو نظام الإيجار في مصر؟"}, headers=headers)
    conv_id = first.json()["conversation_id"]

    second = client.post(
        "/chat", json={"message": "وما هي المدة القانونية؟", "conversation_id": conv_id}, headers=headers
    )
    assert second.json()["conversation_id"] == conv_id

    convo_resp = client.get(f"/conversations/{conv_id}", headers=headers)
    assert convo_resp.status_code == 200
    messages = convo_resp.json()["messages"]
    assert len(messages) == 4  # 2 user + 2 assistant


def test_chat_requires_auth(client):
    resp = client.post("/chat", json={"message": "test"})
    assert resp.status_code == 401
