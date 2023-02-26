"""A data model for quickstatements."""

import datetime
import webbrowser
from typing import Iterable, List, Optional, Sequence, Type, Union
from urllib.parse import quote

from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, get_args

__all__ = [
    # Data model
    "EntityQualifier",
    "DateQualifier",
    "TextQualifier",
    "Qualifier",
    "CreateLine",
    "TextLine",
    "EntityLine",
    "Line",
    # Line renderers
    "render_lines",
    "lines_to_url",
    "lines_to_new_tab",
]


class EntityQualifier(BaseModel):
    """A qualifier that points to Wikidata entity."""

    type: Literal["Entity"] = "Entity"
    predicate: str = Field(regex=r"^[PQS]\d+$")
    target: str = Field(regex=r"^[PQS]\d+$")

    def get_target(self) -> str:
        """Get the target wikidata identifier."""
        return self.target


class DateQualifier(BaseModel):
    """A qualifier that points to a date string."""

    type: Literal["Date"] = "Date"
    predicate: str = Field(regex=r"^[PQS]\d+$")
    target: str

    def get_target(self) -> str:
        """Get the target date, serialized."""
        return self.target

    @classmethod
    def start_time(
        cls, target: Union[str, datetime.datetime], *, precision: Optional[int] = None
    ) -> "DateQualifier":
        """Get a qualifier for a start time."""
        return cls(predicate="P580", target=prepare_date(target, precision=precision))

    @classmethod
    def end_time(
        cls, target: Union[str, datetime.datetime], *, precision: Optional[int] = None
    ) -> "DateQualifier":
        """Get a qualifier for an end time."""
        return cls(predicate="P582", target=prepare_date(target, precision=precision))


def format_date(
    *,
    precision: int,
    year: int,
    month: int = 0,
    day: int = 0,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> str:
    """Format the date in a way appropriate for quickstatements."""
    return f"+{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}Z/{precision}"


def prepare_date(target: Union[str, datetime.datetime], *, precision: Optional[int] = None) -> str:
    """Prepare a date for quickstatements."""
    if isinstance(target, str):
        return target
    if not isinstance(target, datetime.datetime):
        raise TypeError
    if precision is None:
        precision = 11
    # See section on precision in https://www.wikidata.org/wiki/Help:Dates#Precision
    if precision == 11:  # day precision
        return format_date(
            precision=precision, year=target.year, month=target.month, day=target.day
        )
    elif precision == 10:  # month precision
        return format_date(precision=precision, year=target.year, month=target.month)
    elif precision == 9:  # year precision
        return format_date(precision=precision, year=target.year)
    elif precision == 12:  # hour precision
        return format_date(
            precision=precision,
            year=target.year,
            month=target.month,
            day=target.day,
            hour=target.hour,
        )
    elif precision == 13:  # minute precision
        return format_date(
            precision=precision,
            year=target.year,
            month=target.month,
            day=target.day,
            hour=target.hour,
            minute=target.minute,
        )
    elif precision == 14:  # second precision
        return format_date(
            precision=precision,
            year=target.year,
            month=target.month,
            day=target.day,
            hour=target.hour,
            minute=target.minute,
            second=target.second,
        )
    else:
        raise ValueError(f"Invalid precision: {precision}")
    # No precision case:
    # return f"+{target.isoformat()}Z"


class TextQualifier(BaseModel):
    """A qualifier that points to a string literal."""

    type: Literal["Text"] = "Text"
    predicate: str = Field(regex=r"^[PQS]\d+$")
    target: str

    def get_target(self) -> str:
        """Get the target text literal."""
        return f'"{self.target}"'


#: A union of the qualifier types
Qualifier = Annotated[
    Union[EntityQualifier, DateQualifier, TextQualifier], Field(discriminator="type")
]


class CreateLine(BaseModel):
    """A trivial model representing the CREATE line."""

    type: Literal["Create"] = "Create"

    def get_line(self, sep: str = "|") -> str:
        """Get the CREATE line."""
        return "CREATE"


class BaseLine(BaseModel):
    """A shared model for entity and text lines."""

    subject: str = Field(regex=r"^(LAST)|(Q\d+)$")
    predicate: str = Field(
        regex=r"^(P\d+)|(Len)|(Den)$",
        description="Either a predicate, `Len` (label), or `Den` (description)",
    )
    qualifiers: List[Qualifier] = Field(default_factory=list)

    def get_target(self) -> str:
        """Get the target of the line."""
        return self.target

    def get_line(self, sep: str = "|") -> str:
        """Get the QuickStatement line as a string."""
        parts = [self.subject, self.predicate, self.get_target()]
        for qualifier in self.qualifiers:
            parts.append(qualifier.predicate)
            parts.append(qualifier.get_target())
        return sep.join(parts)


class EntityLine(BaseLine):
    """A line whose target is a string literal."""

    type: Literal["Entity"] = "Entity"
    target: str = Field(regex=r"^Q\d+$")


class TextLine(BaseLine):
    """A line whose target is a Wikidata entity."""

    type: Literal["Text"] = "Text"
    target: str

    def get_target(self) -> str:
        """Get the text literal line."""
        return f'"{self.target}"'


#: A union of the line types
Line = Annotated[Union[CreateLine, EntityLine, TextLine], Field(discriminator="type")]


def render_lines(lines: Iterable[Line], sep: str = "|", newline: str = "||") -> str:
    """Prepare QuickStatements line objects for sending to the API."""
    return newline.join(line.get_line(sep=sep) for line in lines)


def lines_to_url(lines: Iterable[Line]) -> str:
    """Prepare a URL for V1 of QuickStatements."""
    quoted_qs = quote(render_lines(lines), safe="")
    return f"https://quickstatements.toolforge.org/#/v1={quoted_qs}"


def lines_to_new_tab(lines: Iterable[Line]):
    """Open a web browser on the host system."""
    return webbrowser.open_new_tab(lines_to_url(lines))


def _unpack_annotated(t) -> Sequence[Type]:
    return get_args(get_args(t)[0])


def write_json_schema():
    """Write a JSON schema."""
    import json

    import pydantic.schema

    schema = pydantic.schema.schema(
        [
            *_unpack_annotated(Qualifier),
            *_unpack_annotated(Line),
        ],
        title="QuickStatements",
        description="A data model representing lines in Quickstatements",
    )
    with open("schema.json", "w") as file:
        json.dump(schema, file, indent=2)


if __name__ == "__main__":
    write_json_schema()
