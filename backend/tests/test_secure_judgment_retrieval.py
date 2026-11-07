"""Offline SSRF and retrieval policy tests."""
import pytest
from app.services.secure_judgment_retrieval import _hostname, _public_addresses, fetch_verified_html


@pytest.mark.parametrize("url", [
    "http://court.example.org/", "https://127.0.0.1/",
    "https://localhost/", "https://court.example.org:8443/",
    "https://user:pass@court.example.org/", "https://court.example.org/#fragment",
])
def test_invalid_evidence_endpoints_fail(url):
    with pytest.raises(ValueError):
        _hostname(url)


def test_dns_rejects_private_or_mixed_addresses(monkeypatch):
    import socket
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
    ])
    with pytest.raises(ValueError):
        _public_addresses("court.example.org")


def test_host_allowlist_checked_before_dns(monkeypatch):
    import socket
    def never_resolve(*a, **k):
        raise AssertionError("DNS should not be called")
    monkeypatch.setattr(socket, "getaddrinfo", never_resolve)
    with pytest.raises(ValueError, match="allowlisted"):
        fetch_verified_html("https://untrusted.example.org/case", allowed_hosts=frozenset({"court.example.org"}))


def test_html_extractor_ignores_scripts_but_preserves_body():
    from app.services.secure_judgment_retrieval import _Text
    parser = _Text()
    parser.feed("<html><body>Before<script>ignore <b>this</b></script>After</body></html>")
    assert "Before" in "".join(parser.parts)
    assert "After" in "".join(parser.parts)
    assert "ignore" not in "".join(parser.parts)


def test_pinned_ip_https_fetch_and_hash(monkeypatch):
    import socket
    import urllib3
    from app.services import secure_judgment_retrieval as retrieval
    calls = {}
    class FakeResponse:
        status = 200
        headers = {"Content-Type": "text/html; charset=utf-8"}
        def read(self, count):
            return b"<html><body>Verified judgment text</body></html>"
        def release_conn(self):
            calls["released"] = True
    class FakePool:
        def __init__(self, host, **kwargs):
            calls["ip"] = host
            calls.update(kwargs)
        def urlopen(self, method, path, **kwargs):
            calls["path"] = path
            calls["request"] = kwargs
            return FakeResponse()
        def close(self):
            calls["closed"] = True
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))
    ])
    monkeypatch.setattr(urllib3, "HTTPSConnectionPool", FakePool)
    doc = retrieval.fetch_verified_html(
        "https://court.example.org/judgment?id=42",
        allowed_hosts=frozenset({"court.example.org"}),
    )
    assert calls["ip"] == "8.8.8.8"
    assert calls["server_hostname"] == "court.example.org"
    assert calls["assert_hostname"] == "court.example.org"
    assert calls["request"]["redirect"] is False
    assert calls["request"]["retries"] is False
    assert calls["request"]["headers"]["Host"] == "court.example.org"
    assert calls["path"] == "/judgment?id=42"
    assert doc.trusted_source
    assert "Verified judgment text" in doc.extracted_text
    assert calls["released"] and calls["closed"]
