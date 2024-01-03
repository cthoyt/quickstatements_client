"""A maintenance script for adding missing "follows" relations to preprint/postprints."""

import sys

import click

from quickstatements_client import EntityLine, QuickStatementsClient
from quickstatements_client.sources.utils import query_wikidata

#: A SPARQL query that identifies preprints that are annotated
#: with the "followed by" relationship to a postprint, but whose
#: postprint doesn't have the "follows" relationship pointing
#: backwards
SPARQL = """\
SELECT ?preprint ?postprint
WHERE {
  ?preprint wdt:P31 wd:Q580922 .
  ?preprint wdt:P156 ?postprint .
  FILTER NOT EXISTS {
    ?postprint wdt:P155 ?preprint .
  }
}
"""


@click.command()
@click.option("--non-interactive", is_flag=True)
def main(non_interactive: bool):
    """Add missing "follows" relationships to postprints."""
    lines = [
        EntityLine(
            subject=record["postprint"],
            predicate="P155",
            target=record["preprint"],
        )
        for record in query_wikidata(SPARQL)
    ]
    if not lines:
        click.secho("No 'follows' relations to add", fg="yellow")
        return sys.exit(0)
    client = QuickStatementsClient()
    if non_interactive:
        client.post(lines, batch_name="Preprint Maintenance")
    else:
        client.open_new_tab(lines)


if __name__ == "__main__":
    main()
