"""Tests for data model."""

import datetime
import json
import unittest
from pathlib import Path
from typing import Tuple, Union

from quickstatements_client.model import (
    DateQualifier,
    EntityLine,
    EntityQualifier,
    TextLine,
    TextQualifier,
    prepare_date,
)

HERE = Path(__file__).parent.resolve()
SAMPLE_ORCID_PATH = HERE.joinpath("sample_orcid.json")


class TestQuickStatements(unittest.TestCase):
    """Tests for quickstatements."""

    def test_prepare_date(self):
        """Test the date cleaning function."""
        sample_orcid_data = json.loads(SAMPLE_ORCID_PATH.read_text())
        education_data = sample_orcid_data["activities-summary"]["educations"]["education-summary"]

        test_start_date, start_date_precision = _get_date(education_data[1])
        test_end_date, end_date_precision = _get_date(education_data[1], start_or_end="end")

        self.assertEqual(
            "+2015-08-00T00:00:00Z/10",
            prepare_date(test_start_date, precision=start_date_precision),
        )
        self.assertEqual(
            "+2017-10-27T00:00:00Z/11", prepare_date(test_end_date, precision=end_date_precision)
        )

    def test_quickstatements(self):
        """Test quick statements."""
        subject_qid = "Q47475003"  # Charles Tapley Hoyt
        # subject_orcid = "0000-0003-4423-4370"
        reference_url_qualifier = TextQualifier(
            predicate="S854", target="https://orcid.org/0000-0003-4423-4370"
        )
        start_date = datetime.datetime(year=2021, day=15, month=2)
        start_date_qualifier = DateQualifier.start_time(start_date)
        position_held_qualifier = EntityQualifier(predicate="P39", target="Q1706722")
        employment_line = EntityLine(
            subject=subject_qid,
            predicate="P108",  # employer
            target="Q49121",  # Harvard medical school
            qualifiers=[reference_url_qualifier, start_date_qualifier, position_held_qualifier],
        )
        self.assertEqual(
            'Q47475003|P108|Q49121|S854|"https://orcid.org/0000-0003-4423-4370"|'
            "P580|+2021-02-15T00:00:00Z/11|P39|Q1706722",
            employment_line.get_line(),
        )

        # Try with different date precision
        start_date_month = datetime.datetime(year=2021, month=2, day=1)
        # 10 = month precision
        start_date_month_qualifier = DateQualifier.start_time(start_date_month, precision=10)
        employment_line_less_precise = EntityLine(
            subject=subject_qid,
            predicate="P108",  # employer
            target="Q49121",  # Harvard medical school
            qualifiers=[
                reference_url_qualifier,
                start_date_month_qualifier,
                position_held_qualifier,
            ],
        )
        self.assertEqual(
            'Q47475003|P108|Q49121|S854|"https://orcid.org/0000-0003-4423-4370"|P580|'
            "+2021-02-00T00:00:00Z/10|P39|Q1706722",
            employment_line_less_precise.get_line(),
        )

        nickname_line = TextLine(
            subject=subject_qid,
            predicate="P1449",
            target="Charlie",
        )
        self.assertEqual('Q47475003|P1449|"Charlie"', nickname_line.get_line())


def _get_date(
    entry, start_or_end="start"
) -> Union[Tuple[datetime.datetime, int], Tuple[None, None]]:
    """Get a date out of part of an ORCID record."""
    date = entry.get(f"{start_or_end}-date")
    if date is None:
        return None, None
    year = int(date.get("year", {}).get("value", 0))
    if not year:
        return None, None
    month = int(date["month"]["value"]) if date["month"] else 1
    day = date["day"] and int(date["day"]["value"])
    if day:
        # precision of 11 means day is known
        return datetime.datetime(year=year, month=month, day=day), 11
    elif month:
        # precision of 10 means up to the month is known
        return datetime.datetime(year=year, month=month, day=1), 10
    else:
        # precision of 9 means up to the year is known
        return datetime.datetime(year=year, month=1, day=1), 9
