# -*- coding: utf-8 -*-

"""Utilities for Wikidata."""

from typing import Any, List, Mapping

import requests

__all__ = [
    "WIKIDATA_ENDPOINT",
    "query_wikidata",
    "removeprefix",
]

#: Wikidata SPARQL endpoint. See https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service#Interfacing
WIKIDATA_ENDPOINT = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"


def query_wikidata(sparql: str) -> List[Mapping[str, Any]]:
    """Query Wikidata's sparql service.

    :param sparql: A SPARQL query string
    :return: A list of bindings
    """
    res = requests.get(WIKIDATA_ENDPOINT, params={"query": sparql, "format": "json"})
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
