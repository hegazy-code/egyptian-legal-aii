"""Small pagination helper for list endpoints."""
from typing import Tuple


def clamp_pagination(skip: int = 0, limit: int = 20, max_limit: int = 100) -> Tuple[int, int]:
    skip = max(skip, 0)
    limit = max(1, min(limit, max_limit))
    return skip, limit
