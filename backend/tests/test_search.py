from app.search.exact_reference import extract_article_references


def test_search_endpoint_returns_empty_results_on_empty_corpus(client):
    resp = client.post("/search", json={"query": "الايجار", "limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "الايجار"
    assert isinstance(body["results"], list)


def test_exact_article_reference_detection():
    refs = extract_article_references("ما حكم المادة 341 من قانون العقوبات؟")
    assert len(refs) == 1
    assert refs[0].article_number == "341"
    assert "العقوبات" in (refs[0].law_name or "")


def test_list_laws_endpoint(client):
    resp = client.get("/laws")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_missing_article_returns_404(client):
    resp = client.get("/articles/does-not-exist")
    assert resp.status_code == 404
