# -*- coding: utf-8 -*-

"""Create QuickStatements from the ORCID API.

.. seealso:: More detailed functionality is implemented in https://github.com/lubianat/pyorcidator
"""

import re
from typing import Iterable, Optional

import requests

from quickstatements_client.model import (
    CreateLine,
    DateQualifier,
    EntityLine,
    Line,
    TextLine,
    TextQualifier,
)
from quickstatements_client.sources.utils import get_qid

__all__ = ["get_orcid_data", "get_orcid_qid", "iter_orcid_lines"]


ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}(\d|X)$")


def _raise_on_invalid_orcid(orcid: str) -> None:
    if not ORCID_RE.match(orcid):
        raise ValueError


def get_orcid_data(orcid: str):
    """Get data from the ORCID API."""
    _raise_on_invalid_orcid(orcid)
    res = requests.get(
        f"https://orcid.org/{orcid}", headers={"Accept": "application/json"}, timeout=10
    ).json()
    name_dict = res["person"]["name"]
    name = name_dict["given-names"]["value"] + " " + name_dict["family-name"]["value"]
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


if __name__ == "__main__":
    from quickstatements_client.model import lines_to_new_tab

    lines_to_new_tab(iter_orcid_lines("0000-0001-6677-8489"))
