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
