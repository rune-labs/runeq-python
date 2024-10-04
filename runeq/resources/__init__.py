"""
Fetch data from Rune APIs.

By default, globally-initialized clients are used for all API requests (see
:class:`~runeq.resources.client.initialize`). Functions that make API requests
also accept optional client(s), which can be used in lieu of the global
initialization.

Metadata is fetched from Rune's GraphQL API
(https://graph.runelabs.io/graphql), using a
:class:`~runeq.resources.client.GraphClient`. Timeseries data is fetched
from the `V2 Stream API <https://docs.runelabs.io/stream/v2/index.html>`_,
using a :class:`~runeq.resources.client.StreamClient`.

"""

from . import client, common, event, org, patient, stream, stream_metadata, user

__all__ = [
    "client",
    "common",
    "event",
    "org",
    "patient",
    "stream_metadata",
    "stream",
    "user",
]
