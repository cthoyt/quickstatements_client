# -*- coding: utf-8 -*-

"""Create QuickStatements from the Python Package Index (PyPI)."""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

import requests

from quickstatements_client.model import (
    CreateLine,
    EntityLine,
    EntityQualifier,
    Line,
    TextLine,
    TextQualifier,
    lines_to_new_tab,
)
from quickstatements_client.sources.utils import query_wikidata, removeprefix

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent.resolve()
LICENSES = HERE.joinpath("licenses.json")
PACKAGES = HERE.joinpath("packages.json")
USERS = HERE.joinpath("users.json")


@lru_cache(maxsize=1)
def load_licenses() -> Mapping[str, str]:
    """Load mapping of license short name to license Wikidata QID.

    :return: A mapping from normalized name to license QID.

    This dictionary was generated with the following SPARQL:

    .. code-block:: sparql

        SELECT DISTINCT ?name ?item
        WHERE
        {
          ?item wdt:P31+ / wdt:P279* wd:Q207621 .
          ?item wdt:P1813 ?name
          FILTER(LANG(?name) = 'en')
        }
    """
    return {
        _norm(r["name"]): removeprefix(r["item"], "http://www.wikidata.org/entity/")
        for r in json.loads(LICENSES.read_text())
    }


PACKAGES_SPARQL = """\
SELECT ?item ?name
WHERE {
  ?item wdt:P5568 ?name
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""


@lru_cache(maxsize=1)
def load_packages() -> Mapping[str, str]:
    """Load mapping of PyPI package name to package Wikidata QID.

    :returns: A mapping from PyPI package name to Wikidata QID.

    .. warning::

        The Wikidata SPARQL endpoint does not update immediately
        after creating new entries, therefore this query could lag
        behind by 10-15 minutes.
    """
    return {_norm(record["name"]): record["item"] for record in query_wikidata(PACKAGES_SPARQL)}


def get_license_qid(name: str) -> Optional[str]:
    """Get a license QID from a name."""
    return load_licenses().get(_norm(name))


def get_package_qid(name: str) -> Optional[str]:
    """Get a Python package QID from a name."""
    return load_packages().get(_norm(name))


git_qualifier = EntityQualifier(
    predicate="P8423", target="Q186055"  # version control system  # git
)
github_qualifier = EntityQualifier(
    predicate="P10627", target="Q364"  # web interface software  # GitHub
)


def iter_pypi_lines(pypi_project: str, create: bool = True) -> Iterable[Line]:
    """Yield QuickStatements lines about a Python package in PyPI.

    :param pypi_project: The name of the project on PyPI (i.e.,
        ``pystow`` for https://pypi.org/pypi/pystow
    :param create:
        In the case when there is not already a P5568 property linking
        a Wikidata entry to the given PyPI project, this has two effects:

        - if true, will create a new entry.
        - if false, will not yield any QuickStatements lines

        .. warning::

            Use this with care, as not all entries on Wikidata are
            fully annotated, and this could lead to duplicate entries
    :yields: QuickStatements lines
    """
    pypi_project = pypi_project.replace("_", "-")
    metadata = requests.get(f"https://pypi.org/pypi/{pypi_project}/json").json()["info"]

    package_qid = get_package_qid(pypi_project)
    if not package_qid:
        if not create:
            return
        yield CreateLine()
        package_qid = "LAST"
        name = metadata["name"]
        yield TextLine(subject=package_qid, predicate="Len", target=name)
        yield TextLine(subject=package_qid, predicate="Den", target="Python software package")

    pypi_qualifier = TextQualifier(
        predicate="S854",  # reference URL
        target=f"https://pypi.org/project/{pypi_project}",
    )

    yield EntityLine(
        subject=package_qid,
        predicate="P31",  # instance of
        target="Q29642950",  # Python library
        qualifiers=[pypi_qualifier],
    )
    yield EntityLine(
        subject=package_qid,
        predicate="P31",  # instance of
        target="Q7397",  # software
        qualifiers=[pypi_qualifier],
    )
    yield EntityLine(
        subject=package_qid,
        predicate="P277",  # programmed in
        target="Q28865",  # Python
        qualifiers=[pypi_qualifier],
    )
    yield TextLine(
        subject=package_qid,
        predicate="P5568",  # PyPI Project
        target=pypi_project,
        qualifiers=[pypi_qualifier],
    )

    license_qid = get_license_qid(metadata.get("license") or "")
    if license_qid:
        yield EntityLine(
            subject=package_qid,
            predicate="P6216",  # copyright status
            target="Q50423863",  # copyrighted
            qualifiers=[pypi_qualifier],
        )
        yield EntityLine(
            subject=package_qid,
            predicate="P275",  # copyright license
            target=license_qid,
            qualifiers=[pypi_qualifier],
        )

    docs_url = metadata.get("docs_url")
    if docs_url:
        yield TextLine(
            subject=package_qid,
            predicate="P2078",  # user manual URL
            target=docs_url.rstrip("/"),
            qualifiers=[pypi_qualifier],
        )

    project_urls = metadata.get("project_urls") or {}
    for predicate, keys in [
        ("P856", ["homepage"]),  # official website
        ("P1401", ["tracker", "bug tracker"]),  # issue tracker URL
    ]:
        target_url = _dict_get(project_urls, keys)
        if not target_url:
            continue
        yield TextLine(
            subject=package_qid,
            predicate=predicate,
            target=target_url.rstrip("/"),
            qualifiers=[pypi_qualifier],
        )

    for url in [
        _dict_get(project_urls, ["homepage"]),
        _dict_get(project_urls, ["source", "source code"]),
        metadata.get("home_page", ""),
    ]:
        if url and url.startswith("https://github.com/"):
            yield TextLine(
                subject=package_qid,
                predicate="P1324",  # source code repository
                target=url.rstrip("/"),
                qualifiers=[
                    pypi_qualifier,
                    git_qualifier,
                    github_qualifier,
                ],
            )
            break

    for requirement in metadata.get("requires_dist") or []:
        # TODO reuse existing parser
        # TODO decide if extras should count
        parts = requirement.split(" ", 1)
        if len(parts) > 1 and any("extra" in part for part in parts[1:]):
            continue
        requirement_qid = get_package_qid(parts[0])
        if not requirement_qid:
            logger.warning(f"[pypi:{pypi_project}] could not look up requirement: {parts[0]}")
            continue
        yield EntityLine(
            subject=package_qid,
            predicate="P1547",  # depends on software
            target=requirement_qid,
            qualifiers=[pypi_qualifier],
        )


def _norm(s: Optional[str]) -> str:
    if not s:
        return ""
    return s.lower().replace(" ", "").replace("-", "")


def _dict_get(data: Mapping[str, str], keys: Sequence[str]) -> Optional[str]:
    data = {_norm(k): v for k, v in data.items()}
    keys = [_norm(k) for k in keys]
    for key in keys:
        if key in data:
            return data[key]
    return None


if __name__ == "__main__":
    lines_to_new_tab(iter_pypi_lines("y0"))
