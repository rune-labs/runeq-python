"""
Fetch metadata about Rune platform users.

"""

from typing import Optional

from .client import GraphClient, global_graph_client
from .common import ItemBase
from runeq import Config
from runeq.resources import client


def initialize(*args, **kwargs):
    """
    Initialize the library with specified configuration options. Sets global
    clients for the Stream and GraphQL APIs.

    Note that the global Stream API client is only used for V2 endpoints.

    Parameters
    ----------
    *args
        Accepts at most 1; a filename. If provided, values will be
        loaded from the file. It is invalid to provide both a filename
        **and** keyword arguments.
    **kwargs
        Initialize client with keyword arguments.
        If using client keys, specify the client_key_id & client_access_key.
        If using access tokens, specify access_token_id & access_token_secret.

    Examples
    --------
    There are several valid ways to use this function:

    >>> initialize()
    # Load the default config file (~/.rune/config)

    >>> initialize('./example_config.yaml')
    # Load values from a YAML file at a specified path

    >>> initialize(access_token_id='foo', access_token_secret='bar')
    >>> initialize(client_key_id='foo', client_access_key='bar')
    # Set configuration values using keyword arguments (instead
    # of a file). This can be used with any valid combination of
    # config options (e.g. with an access token OR a client key).

    """
    config = Config(*args, **kwargs)
    client._graph_client = client.GraphClient(config)
    client._stream_client = client.StreamClient(config)


class User(ItemBase):
    """
    A user of the Rune platform.

    """

    def __init__(
        self,
        id: str,
        display_name: str,
        created_at: float,
        active_org_id: str,
        active_org_display_name: str,
        **attributes
    ):
        """
        Initialize with metadata.

        Args:
            id: User ID
            display_name: Human-readable display name for the user
            created_at: When the user was created (unix timestamp)
            active_org_id: ID of the user's currently active organization
            active_org_display_name: Display name of the user's currently
                active organization

        """
        norm_id = id
        self.display_name = display_name
        self.created_at = created_at
        self.active_org_id = active_org_id
        self.active_org_display_name = active_org_display_name

        super().__init__(
            id=norm_id,
            display_name=display_name,
            created_at=created_at,
            active_org_id=active_org_id,
            active_org_display_name=active_org_display_name,
            **attributes,
        )

    @staticmethod
    def normalize_id(user_id: str) -> str:
        """
        Strip resource prefix and suffix from the user ID (if they exist).

        Args:
            user_id: User ID

        """
        if user_id.startswith("user-"):
            user_id = user_id[5:]

        if user_id.endswith(",user"):
            user_id = user_id[:-5]

        return user_id


def get_current_user(client: Optional[GraphClient] = None) -> User:
    """
    Get information about the current user (based on the API credentials).

    Args:
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.
    """
    client = client or global_graph_client()
    query = '''
        query getUser {
            user {
                id
                created_at: created
                display_name: displayName
                defaultMembership {
                    org {
                        id
                        display_name: displayName
                    }
                }
                email
            }
        }
    '''

    result = client.execute(statement=query)

    user_attrs = result["user"]

    org = user_attrs.get("defaultMembership", {}).get("org")

    return User(
        id=user_attrs["id"],
        display_name=user_attrs.get("display_name"),
        created_at=user_attrs.get("created_at"),
        active_org_id=org.get("id"),
        active_org_display_name=org.get("display_name"),
        email=user_attrs.get("email")
    )
