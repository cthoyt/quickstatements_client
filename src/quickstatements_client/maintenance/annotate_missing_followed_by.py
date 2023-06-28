"""A maintenance script for adding missing "followed by" relations to preprint/postprints."""

import click

from quickstatements_client import EntityLine, QuickStatementsClient
from quickstatements_client.sources.utils import query_wikidata

#: A SPARQL query that identifies postprints that are annotated
#: with the "follows" relationship, but whose preprint doesn't
#: have the "followed by" relationship pointing backwards
SPARQL = """\
SELECT ?preprint ?postprint
WHERE {
  ?preprint wdt:P31 wd:Q580922 .
  ?postprint wdt:P155 ?preprint .
  FILTER NOT EXISTS {
    ?preprint wdt:P156 ?postprint .
  }
}
"""


@click.command()
@click.option("--non-interactive", is_flag=True)
def main(non_interactive: bool):
    """Add missing "followed by" relationships to preprints."""
    lines = [
        EntityLine(
            subject=record["preprint"],
            predicate="P156",
            target=record["postprint"],
        )
        for record in query_wikidata(SPARQL)
    ]
    client = QuickStatementsClient()
    if non_interactive:
        client.post(lines, batch_name="Postprint Maintenance")
    else:
        client.open_new_tab(lines)


if __name__ == "__main__":
    main()
