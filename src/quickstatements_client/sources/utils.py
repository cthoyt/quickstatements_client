# -*- coding: utf-8 -*-

"""Utilities for Wikidata."""

from __future__ import annotations

from wikidata_client import get_entity_by_property as get_qid
from wikidata_client import get_image
from wikidata_client import query as query_wikidata

__all__ = [
    "query_wikidata",
    "get_qid",
    "get_image",
]
