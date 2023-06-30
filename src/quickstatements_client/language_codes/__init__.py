"""Utilities for ISO639 language codes.

Run this module as a script to download the list again.

.. seealso:: https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all.
"""

import json
from pathlib import Path

__all__ = [
    "LANGUAGE_CODES",
]

HERE = Path(__file__).parent.resolve()
PATH = HERE.joinpath("data.json")
LANGUAGE_CODES = json.loads(PATH.read_text())


def main():
    """Download the ISO code list and dump it in the JSON file."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
