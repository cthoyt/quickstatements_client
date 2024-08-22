"""A client to the QuickStatements API."""

from __future__ import annotations

import webbrowser
from typing import Any, Iterable, Optional, Union

import pystow
import requests
from pydantic import BaseModel, Field
from typing_extensions import Literal

from quickstatements_client.constants import TimeoutHint
from quickstatements_client.model import Line, lines_to_url, render_lines

__all__ = [
    "QuickStatementsClient",
    "Post",
    "Response",
]


class Response(BaseModel):
    """A data model for the response returned by the QuickStatements API."""

    status: str
    batch_id: Union[str, int, None] = None

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

    def post(
        self, lines: Iterable[Line], batch_name: Optional[str] = None, timeout: TimeoutHint = None
    ) -> Response:
        """Post a batch of QuickStatements with an optional name."""
        if timeout is None:
            timeout = 300
        params = Post(
            username=self.username,
            token=self.token,
            data=render_lines(lines),
            batchname=batch_name,
        )
        res = requests.post(
            self.endpoint,
            data=params.dict(),
            timeout=timeout,
        )
        return Response.parse_obj(res.json())

    def get_batch_info(self, batch_id: int, *, timeout: TimeoutHint = None) -> BatchInfo:
        """Get information about a QuickStatements batch.

        :param batch_id: The QuickStatements batch ID.
        :param timeout: Number of seconds before timeout. Defaults to 10 seconds.
        :return: An object containing information about the batch

        For example, see https://quickstatements.toolforge.org/api.php?action=get_batch_info&batch=235284.
        Identifiers for recent batches can be found at https://quickstatements.toolforge.org/#/batches.
        """
        if timeout is None:
            timeout = 10

        params: dict[str, Any] = {"action": "get_batch_info", "batch": batch_id}
        res = requests.get(self.endpoint, params=params, timeout=timeout)
        res.raise_for_status()
        js = res.json()
        data = js["data"][str(batch_id)]  # might raise a key error

        commands = data["commands"]
        batch_data = data["batch"]
        return BatchInfo(
            done=commands.get("DONE", 0),
            run=commands.get("RUN", 0),
            error=commands.get("ERROR", 0),
            init=commands.get("INIT", 0),
            last_item=batch_data["last_item"] or None,
            message=batch_data["message"] or None,
            name=batch_data["name"] or None,
            status=batch_data["status"].lower(),
            username=batch_data["user_name"],
            user=batch_data["user"],
        )

    @staticmethod
    def open_new_tab(lines: Iterable[Line]):
        """Open a web browser on the host system."""
        return webbrowser.open_new_tab(lines_to_url(lines))


class Post(BaseModel):
    """A data model representing the parameters sent to begin a batch in the QuickStatements API."""

    username: str = Field(...)
    token: str = Field(...)
    data: str = Field(...)
    batchname: Optional[str] = Field(default=None)
    compress: int = Field(
        default=0,
        description="[optional; deactivates compression of CREATE and following LAST commands]",
    )
    action: str = Field(default="import")
    submit: int = Field(default=1)
    site: str = Field(default="wikidata")
    format: Literal["v1", "csv"] = "v1"


class BatchInfo(BaseModel):
    """Holds batch information."""

    done: int = Field(default=0, description="The number of statements that were successfully run")
    run: int = Field(default=0, description="The number of statements being run right now")
    error: int = Field(default=0, description="The number of statements that failed")
    init: int = Field(default=0, description="The number of statements left to run")
    name: Optional[str] = None
    message: Optional[str] = None
    last_item: Optional[str] = None
    status: Literal["done", "run", "stop"]
    username: str
    user: int
