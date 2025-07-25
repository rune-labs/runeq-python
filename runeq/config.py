"""
Configuration for accessing Rune APIs.

"""

import os
from logging import getLogger

import boto3
import yaml

log = getLogger(__name__)


AUTH_METHOD_CLIENT_KEYS = "client_keys"
"""
Auth method to use a Client Key pair for authentication.

"""

AUTH_METHOD_JWT = "jwt"
"""
Auth method to use a JWT for authentication.

"""

AUTH_METHOD_COGNITO_REFRESH = "cognito_refresh"
"""
Auth method to use a Cognito refresh token for authentication.

"""

AUTH_METHOD_ACCESS_TOKEN = "access_token"
"""
Auth method to use a user access token for authentication.

"""

AUTH_METHOD_CUSTOM = "custom"
"""
Auth method to use custom authentication headers.

"""

DEFAULT_CONFIG_YAML = "~/.rune/config"
"""
Default path for the config file (yaml formatted)

"""


class BaseConfig:
    """Base class to hold configuration for accessing Rune APIs."""

    graph_url: str
    stream_url: str
    strive_url: str

    def refresh_auth(self) -> bool:
        """
        Refresh authentication credentials if possible, returning a bool
        indicating if the refresh occurred.

        This is specific to the authentication style: e.g. it may
        be implemented to refresh a JWT. By default, it is a no-op.

        The API clients contain logic to catch possible authentication
        errors, invoke this method, and retry the request (if credentials
        are successfully refreshed).

        """
        return False

    @property
    def auth_headers(self) -> dict:
        """
        Authentication headers for HTTP requests to Rune APIs.

        """
        raise NotImplementedError("auth_headers must be implemented by a subclass")


class Config(BaseConfig):
    """
    Holds configuration for Rune API usage (e.g. auth credentials, URLs, etc)

    """

    def __init__(self, *args, **kwargs):
        """
        Initialize configuration options.

        Args:
            *args: Accepts at most 1; a filename. If provided, values will be
                loaded from the file, using `load_yaml()`. It is invalid to
                provide both a filename **and** keyword arguments.
            **kwargs: Passed to set_values().

        Examples:
            There are three valid ways to create a config:

            >>> cfg = Config()
            # Load from default file location (~/.rune/config)

            >>> cfg = Config('./example_config.yaml')
            # Load from a specified YAML file

            >>> cfg = Config(access_token_id='foo', access_token_secret='bar')
            # Set values using keyword arguments. This can be used with any
            # valid combination of config options; the example above sets a
            # user access token.

        """
        self.graph_url = "https://graph.runelabs.io"
        self.stream_url = "https://stream.runelabs.io"
        self.strive_url = "https://strivepd.runelabs.io"
        self.auth_method = None

        self._access_token_id = None
        self._access_token_secret = None
        self._client_access_key = None
        self._client_key_id = None
        self._jwt = None
        self._cognito_client_id = None
        self._cognito_refresh_token = None
        self._custom_auth_headers = None

        if args and kwargs:
            raise TypeError(
                "__init__() cannot accept both positional arguments and "
                "keyword arguments"
            )
        elif args:
            if len(args) > 1:
                raise TypeError(
                    "__init__() takes at most 1 positional argument but "
                    f"{len(args)} were given"
                )

            self.load_yaml(args[0])
        elif not kwargs:
            self.load_yaml()
        else:
            self.set_values(**kwargs)

    def load_yaml(self, filename=DEFAULT_CONFIG_YAML):
        """
        Set values from a YAML file. Keys from the file are passed directly to
        set_values(), as kwargs.

        Args:
            filename: File path for a YAML-formatted config file

        """
        with open(os.path.expanduser(filename)) as f:
            params = yaml.safe_load(f)
        return self.set_values(**params)

    def set_values(
        self,
        auth_method=None,
        access_token_id=None,
        access_token_secret=None,
        client_key_id=None,
        client_access_key=None,
        jwt=None,
        cognito_client_id=None,
        cognito_refresh_token=None,
        cognito_region_name="us-west-2",
        stream_url=None,
        graph_url=None,
        strive_url=None,
        custom_auth_headers=None,
        **kwargs,
    ):
        """
        Set configuration values.

        Args:
            auth_method: What type of authentication credentials to use. Must
                be one of 'access_token', 'client_keys', or 'jwt'. If not set,
                the auth method is inferred based on which credentials are
                specified (as long as it's unambiguous).
            access_token_id: User access token ID
            access_token_secret: User access token secret
            client_key_id: Client key ID
            client_access_key: Client access key
            jwt: JWT
            stream_url: base URL to use for the stream API
            graph_url: base URL to use for the graph API
            strive_url: base URL to use for the strive API
            custom_auth_headers: custom authentication headers to use for the request
            **kwargs: Arbitrary values may be provided, but they are ignored.

        """
        if stream_url is not None:
            self.stream_url = stream_url

        if graph_url is not None:
            self.graph_url = graph_url

        if strive_url is not None:
            self.strive_url = strive_url

        if auth_method is None:
            num_auth_methods_set = sum(
                [
                    bool(access_token_id or access_token_secret),
                    bool(client_access_key or client_key_id),
                    bool(jwt),
                    bool(cognito_refresh_token and cognito_client_id),
                    bool(custom_auth_headers),
                ]
            )

            if num_auth_methods_set > 1:
                raise ValueError(
                    "Cannot infer auth method: multiple credentials were "
                    "provided. Specify auth_method kwarg to disambiguate."
                )
            elif access_token_id and access_token_secret:
                auth_method = AUTH_METHOD_ACCESS_TOKEN
            elif client_key_id and client_access_key:
                auth_method = AUTH_METHOD_CLIENT_KEYS
            elif jwt:
                auth_method = AUTH_METHOD_JWT
            elif cognito_refresh_token and cognito_client_id:
                auth_method = AUTH_METHOD_COGNITO_REFRESH
            elif custom_auth_headers:
                auth_method = AUTH_METHOD_CUSTOM
            else:
                raise ValueError(
                    "Cannot infer auth method: a complete set of credentials "
                    "was not provided."
                )

        self.auth_method = auth_method

        if access_token_id is not None:
            self._access_token_id = access_token_id

        if access_token_secret is not None:
            self._access_token_secret = access_token_secret

        if client_key_id is not None:
            self._client_key_id = client_key_id

        if client_access_key is not None:
            self._client_access_key = client_access_key

        if jwt is not None:
            self._jwt = jwt

        if cognito_client_id is not None:
            self._cognito_client_id = cognito_client_id

        if cognito_refresh_token is not None:
            self._cognito_refresh_token = cognito_refresh_token

        if custom_auth_headers is not None:
            self._custom_auth_headers = custom_auth_headers

        self._cognito_client = boto3.client(
            "cognito-idp",
            region_name=cognito_region_name,
        )

        # access auth headers to ensure they're valid
        _ = self.auth_headers

    @property
    def client_auth_headers(self):
        """
        Authentication headers for HTTP requests, using client key pair.

        """
        if not self._client_access_key:
            raise ValueError("Client access key is not set")
        if not self._client_key_id:
            raise ValueError("Client key id is not set")

        return {
            "X-Rune-Client-Key-ID": self._client_key_id,
            "X-Rune-Client-Access-Key": self._client_access_key,
        }

    @property
    def jwt_auth_headers(self):
        """
        Authentication headers for HTTP requests, using a JWT.

        """
        if not self._jwt:
            if not self.refresh_auth():
                raise ValueError("JWT is not set")

        return {
            "X-Rune-User-Access-Token": self._jwt,
        }

    def refresh_auth(self) -> bool:
        """
        Use the refresh token to get a new JWT.

        Returns:
             Bool indicating if JWT was refreshed.

        Raises:
            Exception if the refresh token request fails

        """
        if not self._cognito_refresh_token:
            return False

        log.debug("refreshing cognito JWT")
        response = self._cognito_client.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": self._cognito_refresh_token,
            },
            ClientId=self._cognito_client_id,
        )
        self._jwt = response["AuthenticationResult"]["AccessToken"]
        return True

    @property
    def access_token_auth_headers(self):
        """
        Authentication headers for HTTP requests, using a User access token.

        """
        if not self._access_token_id:
            raise ValueError("Access token id is not set")

        if not self._access_token_secret:
            raise ValueError("Access token secret is not set")

        return {
            "X-Rune-User-Access-Token-Id": self._access_token_id,
            "X-Rune-User-Access-Token-Secret": self._access_token_secret,
        }

    @property
    def custom_auth_headers(self):
        """
        Authentication headers for HTTP requests, using custom authentication headers.
        """
        if not self._custom_auth_headers:
            raise ValueError("Custom authentication headers are not set")

        return self._custom_auth_headers

    @property
    def auth_headers(self):
        """
        Authentication headers for HTTP requests to Rune APIs.

        """
        if self.auth_method == AUTH_METHOD_ACCESS_TOKEN:
            return self.access_token_auth_headers
        elif self.auth_method == AUTH_METHOD_CLIENT_KEYS:
            return self.client_auth_headers
        elif self.auth_method == AUTH_METHOD_JWT:
            return self.jwt_auth_headers
        elif self.auth_method == AUTH_METHOD_COGNITO_REFRESH:
            return self.jwt_auth_headers
        elif self.auth_method == AUTH_METHOD_CUSTOM:
            return self.custom_auth_headers
        else:
            raise ValueError(
                f'Invalid auth_method "{self.auth_method}": expected one of '
                f"({AUTH_METHOD_ACCESS_TOKEN}, "
                f"{AUTH_METHOD_CLIENT_KEYS}, "
                f"{AUTH_METHOD_JWT}, "
                f"{AUTH_METHOD_COGNITO_REFRESH}, "
                f"{AUTH_METHOD_CUSTOM})"
            )
