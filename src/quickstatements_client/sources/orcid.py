# -*- coding: utf-8 -*-

"""Create QuickStatements from the ORCID API.

.. seealso:: More detailed functionality is implemented in https://github.com/lubianat/pyorcidator
"""

import click
import logging
import re
import requests
from quickstatements_client.constants import TimeoutHint
from quickstatements_client.model import (
    CreateLine,
    DateQualifier,
    EntityLine,
    Line,
    TextLine,
    TextQualifier,
)
from quickstatements_client.sources.utils import get_qid
from typing import Dict, Iterable, Optional

__all__ = [
    "get_orcid_data",
    "get_orcid_name",
    "get_orcid_qid",
    "iter_orcid_lines",
]

logger = logging.getLogger(__name__)

ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}(\d|X)$")


def _raise_on_invalid_orcid(orcid: str) -> None:
    if not ORCID_RE.match(orcid):
        raise ValueError


def get_orcid_name(orcid: str, *, timeout: TimeoutHint = None) -> Optional[str]:
    """Get a person's name from their ORCID."""
    dd = get_orcid_data(orcid=orcid, timeout=timeout)
    if dd is None:
        return None
    return dd["name"]


def get_orcid_data(orcid: str, *, timeout: TimeoutHint = None) -> Optional[Dict[str, str]]:
    """Get data from the ORCID API."""
    _raise_on_invalid_orcid(orcid)
    if timeout is not None:
        timeout = 10.0
    res = requests.get(
        f"https://orcid.org/{orcid}", headers={"Accept": "application/json"}, timeout=timeout
    ).json()
    person = res.get("person")
    if not person:
        logger.warning("%s got no data: %s", orcid, res)
        return None
    name_dict = person.get("name")
    if not name_dict:
        logger.warning("%s missing name dict: %s", orcid, person)
        return None

    given_names = name_dict.get("given-names")
    family_names = name_dict.get("family-name")
    if not given_names or not family_names:
        logger.warning("%s missing name: %s", orcid, person)
        return None

    name = given_names["value"] + " " + family_names["value"]
    rv = {
        "name": name,
    }
    return rv


def get_orcid_qid(orcid: str) -> Optional[str]:
    """Get the QID for an ORCID."""
    _raise_on_invalid_orcid(orcid)
    return get_qid("P496", orcid)


def iter_orcid_lines(orcid: str, create: bool = True, append: bool = False) -> Iterable[Line]:
    """Yield QuickStatements lines about a person from ORCID.

    :param orcid: The target ORCID identifier
    :param create: Should a new QID be created if none can be found? Defaults to true.
    :param append: Should lines be added to an existing QID? Defaults to false.
        If set to true, could make duplicate statements on an existing QID.
    :yields: QuickStatements lines
    """
    _raise_on_invalid_orcid(orcid)
    data = get_orcid_data(orcid)
    orcid_qid = get_orcid_qid(orcid)
    if not orcid_qid:
        if not create:
            return
        if not data:
            return
        yield CreateLine()
        orcid_qid = "LAST"
        name = data["name"]
        yield TextLine(subject=orcid_qid, predicate="Len", target=name)
        yield TextLine(subject=orcid_qid, predicate="Den", target=f"Researcher ORCID={orcid}")
    elif not append:
        return

    pypi_qualifier = TextQualifier(
        predicate="S854",  # reference URL
        target=f"https://orcid.org/{orcid}",
    )
    retrieved_qualifier = DateQualifier.retrieved(namespace="S")
    qualifiers = [pypi_qualifier, retrieved_qualifier]

    yield EntityLine(
        subject=orcid_qid,
        predicate="P31",  # instance of
        target="Q5",  # human
        qualifiers=qualifiers,
    )
    yield EntityLine(
        subject=orcid_qid,
        predicate="P106",  # occupation
        target="Q1650915",  # researcher
        qualifiers=qualifiers,
    )
    yield TextLine(
        subject=orcid_qid,
        predicate="P496",  # ORCID
        target=orcid,
        qualifiers=qualifiers,
    )


@click.command(name="orcid")
@click.argument("orcid")
def main(orcid: str):
    """Add an ORCID to Wikidata."""
    from quickstatements_client.model import lines_to_new_tab

    lines_to_new_tab(iter_orcid_lines(orcid))


if __name__ == "__main__":
    main("0000-0001-6677-8489")
