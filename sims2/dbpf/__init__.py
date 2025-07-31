"""Utilities for reading The Sims 2 dbpf (.package) files."""

from .utils import (
    LIMIT_FOR_CONFLICT,
    Resource,
    ResourceHeader,
    get_headers,
)

__all__ = [
    "LIMIT_FOR_CONFLICT",
    "Resource",
    "ResourceHeader",
    "get_headers",
]
