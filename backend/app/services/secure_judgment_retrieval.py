"""Pinned-IP HTTPS retrieval for reviewed court evidence.

Never follows redirects or uses ambient proxy configuration. DNS is resolved
once, all addresses must be globally routable, and the socket connects to the
validated IP while TLS verifies the original hostname. HTML only, max 2 MB.
"""
import ipaddress
import re
import socket
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit
import urllib3

from app.services.independent_judgment_verification import RetrievedDocument

MAX_BYTES = 2_000_000


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def _hostname(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("HTTPS hostname without credentials required")
    if parsed.port not in (None, 443) or parsed.fragment:
        raise ValueError("Custom ports and fragments forbidden")
    host = parsed.hostname.lower().rstrip(".")
    labels = host.split(".")
    if len(labels) < 2 or not all(
        label and len(label) <= 63 and label[0].isalnum() and label[-1].isalnum()
        and all(c.isascii() and (c.isalnum() or c == "-") for c in label)
        for label in labels
    ):
        raise ValueError("Invalid DNS hostname")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return host
    raise ValueError("IP literal forbidden")


def _public_addresses(host: str) -> list[str]:
    infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    addresses = sorted({item[4][0] for item in infos})
    if not addresses or not all(ipaddress.ip_address(ip).is_global for ip in addresses):
        raise ValueError("DNS must resolve exclusively to public IP addresses")
    return addresses


def fetch_verified_html(url: str, *, allowed_hosts: frozenset[str]) -> RetrievedDocument:
    host = _hostname(url)
    if host not in allowed_hosts:
        raise ValueError("Host is not explicitly allowlisted")
    if len(url) > 1000:
        raise ValueError("Evidence URL too long")
    addresses = _public_addresses(host)
    parsed = urlsplit(url)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    # Connect to validated address, but authenticate TLS certificate for DNS host.
    ip = addresses[0]
    pool = urllib3.HTTPSConnectionPool(
        host=ip, port=443, server_hostname=host, assert_hostname=host,
        cert_reqs="CERT_REQUIRED", timeout=urllib3.Timeout(connect=5, read=10),
        maxsize=1, block=True,
    )
    response = None
    try:
        response = pool.urlopen(
            "GET", path, headers={"Host": host, "Accept": "text/html"},
            redirect=False, retries=False, preload_content=False,
        )
        if response.status != 200:
            raise ValueError("Source must return HTTP 200 without redirects")
        if response.headers.get("Content-Type", "").lower().split(";", 1)[0].strip() != "text/html":
            raise ValueError("Only HTML evidence supported")
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Source document too large")
        parser = _Text()
        parser.feed(raw.decode("utf-8", errors="replace"))
        text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
        if not text:
            raise ValueError("Empty source document")
        return RetrievedDocument(url, raw, text, datetime.now(timezone.utc), trusted_source=True)
    finally:
        if response is not None:
            response.release_conn()
        pool.close()
