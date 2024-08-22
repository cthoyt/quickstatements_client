# -*- coding: utf-8 -*-

"""A data model and client for Wikidata QuickStatements."""

from .client import QuickStatementsClient
from .model import (
    CreateLine,
    DateLine,
    DateQualifier,
    EntityLine,
    EntityQualifier,
    Line,
    Qualifier,
    TextLine,
    TextQualifier,
    lines_to_new_tab,
    lines_to_url,
    render_lines,
)

__all__ = [
    # Client
    "QuickStatementsClient",
    # Data model
    "EntityQualifier",
    "DateQualifier",
    "TextQualifier",
    "Qualifier",
    "CreateLine",
    "TextLine",
    "EntityLine",
    "DateLine",
    "Line",
    # Line renderers
    "render_lines",
    "lines_to_url",
    "lines_to_new_tab",
]
