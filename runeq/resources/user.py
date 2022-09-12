"""
V2 SDK functionality to support User operations.

"""

from typing import Optional

from .client import GraphClient, global_graph_client
from .common import ItemBase
from runeq import Config
from runeq.resources import client


def initialize(*args, **kwargs):
    """
    Initialize configuration options. Authenticate the user and globally
    initialize internal graph and stream clients.

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
    There are four valid ways to initialize the Rune V2 Client:

    >>> initialize()
    # Load from default file location (~/.rune/config)

    >>> initialize('./example_config.yaml')
    # Load from a specified YAML file

    >>> initialize(client_key_id='foo', client_access_key='bar')
    # Set values using keyword arguments

    >>> initialize(access_token_id='foo', access_token_secret='bar')
    # Set values using keyword arguments

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
        Initializes a User

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
    def normalize_id(id: str) -> str:
        """
        Strip resource prefix and suffix from User ID if they exist.

        """
        if id.startswith("user-"):
            id = id[5:]

        if id.endswith(",user"):
            id = id[:-5]

        return id


def get_user(client: Optional[GraphClient] = None) -> User:
    """
    Get current user information.

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
