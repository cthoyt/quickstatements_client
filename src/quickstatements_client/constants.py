"""Constants for QuickStatements Client."""

from __future__ import annotations

from typing import Tuple, Union

from typing_extensions import TypeAlias

__all__ = [
    "TimeoutHint",
]

#: A type hint for the timeout in :func:`requests.get`
TimeoutHint: TypeAlias = Union[None, int, float, Tuple[Union[float, int], Union[float, int]]]
