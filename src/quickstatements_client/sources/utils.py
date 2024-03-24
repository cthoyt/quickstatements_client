# -*- coding: utf-8 -*-

"""Utilities for Wikidata."""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Tuple, Union

import requests
from typing_extensions import TypeAlias

from ..version import get_version

__all__ = [
    "WIKIDATA_ENDPOINT",
    "TimeoutHint",
    "query_wikidata",
    "removeprefix",
    "get_qid",
]

#: Wikidata SPARQL endpoint. See https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service#Interfacing
WIKIDATA_ENDPOINT = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"

#: A type hint for the timeout in :func:`requests.get`
TimeoutHint: TypeAlias = Union[None, int, float, Tuple[Union[float, int], Union[float, int]]]


def query_wikidata(sparql: str, timeout: TimeoutHint = None) -> List[Mapping[str, Any]]:
    """Query Wikidata's sparql service.

    :param sparql: A SPARQL query string
    :param timeout: Number of seconds before timeout. Defaults to 10 seconds.
    :return: A list of bindings
    """
    headers = {
        "User-Agent": f"quickstatements_client v{get_version()}",
    }
    if timeout is None:
        timeout = 10
    res = requests.get(
        WIKIDATA_ENDPOINT,
        params={"query": sparql, "format": "json"},
        headers=headers,
        timeout=timeout,
    )
    res.raise_for_status()
    res_json = res.json()
    return [
        {key: _clean_value(value["value"]) for key, value in record.items()}
        for record in res_json["results"]["bindings"]
    ]


def removeprefix(s: str, prefix: str) -> str:
    """Remove a prefix."""
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


def _clean_value(value: str) -> str:
    value = removeprefix(value, "http://www.wikidata.org/entity/")
    return value


def get_qid(prop: str, value: str, timeout: TimeoutHint = None) -> Optional[str]:
    """Get the Wikidata item's QID based on the given property and value."""
    query = f'SELECT ?item WHERE {{ ?item wdt:{prop} "{value}" . }} LIMIT 1'
    records = query_wikidata(query, timeout=timeout)
    if not records:
        return None
    return records[0]["item"]
