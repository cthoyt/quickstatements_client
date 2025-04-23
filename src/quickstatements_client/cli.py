# -*- coding: utf-8 -*-

"""Command line interface for :mod:`quickstatements_client`.

Why does this file exist, and why not put this in ``__main__``? You might be tempted to import things from ``__main__``
later, but that will cause problems--the code will get executed twice:

- When you run ``python3 -m quickstatements_client`` python will execute``__main__.py`` as a script.
  That means there won't be any ``quickstatements_client.__main__`` in ``sys.modules``.
- When you import __main__ it will get executed again (as a module) because
  there's no ``quickstatements_client.__main__`` in ``sys.modules``.

.. seealso:: https://click.palletsprojects.com/en/8.1.x/setuptools/#setuptools-integration
"""

import logging

import click

from quickstatements_client.sources import orcid, pypi

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def main():
    """CLI for quickstatements_client."""


main.add_command(orcid.main)
main.add_command(pypi.main)


@main.command()
@click.pass_context
def maintain(ctx: click.Context) -> None:
    """Run maitenance queries."""
    from .maintenance import annotate_missing_followed_by, annotate_missing_follows

    ctx.invoke(annotate_missing_follows.main)
    ctx.invoke(annotate_missing_followed_by.main)


if __name__ == "__main__":
    main()
