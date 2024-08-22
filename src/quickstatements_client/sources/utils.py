# -*- coding: utf-8 -*-

"""Utilities for Wikidata."""

from __future__ import annotations

import re
from typing import Any, List, Mapping, Optional

import requests

from ..constants import TimeoutHint
from ..version import get_version

__all__ = [
    "WIKIDATA_ENDPOINT",
    "query_wikidata",
    "removeprefix",
    "get_qid",
    "get_image",
]

WIKIDATA_ITEM_REGEX = re.compile(r"^Q[1-9]\d+$")
WIKIDATA_PROP_REGEX = re.compile(r"^P[1-9]\d+$")


#: Wikidata SPARQL endpoint. See https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service#Interfacing
WIKIDATA_ENDPOINT = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"


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
    if not WIKIDATA_PROP_REGEX.match(prop):
        raise ValueError(f"Wikidata property '{prop}' is not valid.")

    query = f'SELECT ?item WHERE {{ ?item wdt:{prop} "{value}" . }} LIMIT 1'
    records = query_wikidata(query, timeout=timeout)
    if not records:
        return None
    return records[0]["item"]


def get_image(item: str, timeout: TimeoutHint = None) -> Optional[str]:
    """Get a URL for an image for the Wikidata item, if it exists.

    :param item: The Wikidata identifier
    :param timeout: The number of seconds before timeout. Defaults to 10 seconds.
    :return:
        The URL for an image for the item, if it exists. If multiple images exist, arbitrarily return the first.
    :raises ValueError: If the item does not match the Wikidata item regular expression.

    >>> get_image("Q47475003")
    'http://commons.wikimedia.org/wiki/Special:FilePath/Charles%20Tapley%20Hoyt%202019.jpg'

    >>> assert get_image("Q109302693") is None
    """
    if not WIKIDATA_ITEM_REGEX.match(item):
        raise ValueError(f"Wikidata item '{item}' is not valid under {WIKIDATA_ITEM_REGEX}.")

    query = f"""\
    SELECT ?imageLabel WHERE {{
      wd:{item} wdt:P18 ?image.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 1
    """
    records = query_wikidata(query, timeout=timeout)
    if not records:
        return None
    return records[0]["imageLabel"]
