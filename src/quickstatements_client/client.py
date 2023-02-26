"""A client to the QuickStatements API.

1. Get a token from
"""

import webbrowser
from typing import Optional, Sequence

import pystow
import requests
from pydantic import BaseModel, Field
from typing_extensions import Literal

from quickstatements_client.model import Line, lines_to_url, render_lines

__all__ = [
    "QuickStatementsClient",
    "Post",
    "Response",
]


class Response(BaseModel):
    """A data model for the response returned by the QuickStatements API."""

    status: str
    batch_id: Optional[str] = None

    @property
    def batch_url(self) -> str:
        """Get the URL for the batch."""
        return f"https://quickstatements.toolforge.org/#/batch/{self.batch_id}"


class QuickStatementsClient:
    """A client to the QuickStatements API."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
    ):
        """Initialize the QuickStatements API client.

        :param base_url: The base URL of the QuickStatements instance
        :param token: The token for the QuickStatements API.
            Get one from https://tools.wmflabs.org/quickstatements/#/user.
            Loads from :func:`pystow.get_config`.
        :param username: The username associated with the token for the
            QuickStatements API. Loads from :func:`pystow.get_config`.
        """
        self.base_url = (base_url or "https://quickstatements.toolforge.org").rstrip("/")
        self.endpoint = f"{self.base_url}/api.php"
        self.token = pystow.get_config("quickstatements", "token", passthrough=token)
        self.username = pystow.get_config("quickstatements", "username", passthrough=username)

    def post(self, lines: Sequence[Line], batch_name: Optional[str] = None) -> Response:
        """Post a batch of QuickStatements with an optional name."""
        params = Post(
            username=self.username,
            token=self.token,
            data=render_lines(lines),
            batchname=batch_name,
        )
        res = requests.post(self.endpoint, data=params.dict())
        return Response.parse_obj(res.json())

    @staticmethod
    def open_new_tab(lines: Sequence[Line]):
        """Open a web browser on the host system."""
        return webbrowser.open_new_tab(lines_to_url(lines))


class Post(BaseModel):
    """A data model representing the parameters sent to begin a batch in the QuickStatements API."""

    username: str = Field(...)
    token: str = Field(...)
    data: str = Field(...)
    batchname: Optional[str] = Field()
    compress: int = Field(
        0, description="[optional; deactivates compression of CREATE and following LAST commands]"
    )
    action: str = Field("import")
    submit: int = Field(1)
    site: str = Field("wikidata")
    format: Literal["v1", "csv"] = "v1"
