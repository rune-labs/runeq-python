"""
Configuration for API access

"""
import os
import yaml

AUTH_METHOD_CLIENT_KEYS = 'client_keys'
"""
Auth method to use a Client Key pair for authentication.

"""

AUTH_METHOD_JWT = 'jwt'
"""
Auth method to use a JWT for authentication.

"""

AUTH_METHOD_ACCESS_TOKEN = 'access_token'
"""
Auth method to use a user access token for authentication.

"""

DEFAULT_CONFIG_YAML = '~/.rune/config'
"""
Default path for the config file (yaml formatted)

"""


class Config:
    """
    Config holds configuration (e.g. auth credentials, URLs, etc)

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

            >>> cfg = Config(client_key_id='foo', client_access_key='bar')
            # Set values using keyword arguments

        """
        self.stream_url = 'https://stream.runelabs.io'
        self.auth_method = None
        self._access_token_id = None
        self._access_token_secret = None
        self._client_access_key = None
        self._client_key_id = None
        self._jwt = None

        if args and kwargs:
            raise TypeError(
                '__init__() cannot accept both positional arguments and '
                'keyword arguments'
            )
        elif args:
            if len(args) > 1:
                raise TypeError(
                    '__init__() takes at most 1 positional argument but '
                    f'{len(args)} were given')

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

    def set_values(self,
                   auth_method=None,
                   access_token_id=None,
                   access_token_secret=None,
                   client_key_id=None,
                   client_access_key=None,
                   jwt=None,
                   stream_url=None,
                   **kwargs):
        """
        Set configuration values.

        Args:
            auth_method: One of 'access_token' or 'client_keys' or 'jwt'.
            If falsy, the auth
            method is inferred based on which kwargs are specified.
            access_token_id: User access token ID
            access_token_secret: User access token secret
            client_key_id: Client key ID
            client_access_key: Client access key
            jwt: JWT
            stream_url: base URL to use for the stream API

        """
        if stream_url is not None:
            self.stream_url = stream_url

        if auth_method is None:
            num_auth_methods_set = sum([
                bool(access_token_id or access_token_secret),
                bool(client_access_key or client_key_id),
                bool(jwt)
            ])

            if num_auth_methods_set > 1:
                raise ValueError(
                    'Cannot infer auth method: multiple credentials were '
                    'provided. Specify auth_method kwarg to disambiguate.'
                )
            elif access_token_id and access_token_secret:
                auth_method = AUTH_METHOD_ACCESS_TOKEN
            elif client_key_id and client_access_key:
                auth_method = AUTH_METHOD_CLIENT_KEYS
            elif jwt:
                auth_method = AUTH_METHOD_JWT

            else:
                raise ValueError(
                    'Cannot infer auth method: a complete set of credentials '
                    'was not provided.'
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

        # access auth headers to ensure they're valid
        _ = self.auth_headers

    @property
    def client_auth_headers(self):
        """
        Authentication headers for HTTP requests, using client key pair.

        """
        if not self._client_access_key:
            raise ValueError('Client access key is not set')
        if not self._client_key_id:
            raise ValueError('Client key id is not set')

        return {
            'X-Rune-Client-Key-ID': self._client_key_id,
            'X-Rune-Client-Access-Key': self._client_access_key,
        }

    @property
    def jwt_auth_headers(self):
        """
        Authentication headers for HTTP requests, using a JWT.

        """
        if not self._jwt:
            raise ValueError('JWT is not set')

        return {
            'X-Rune-User-Access-Token': self._jwt,
        }

    @property
    def access_token_auth_headers(self):
        """
        Authentication headers for HTTP requests, using a User access token.

        """
        if not self._access_token_id:
            raise ValueError('Access token id is not set')

        if not self._access_token_secret:
            raise ValueError('Access token secret is not set')

        return {
            'X-Rune-User-Access-Token-Id': self._access_token_id,
            'X-Rune-User-Access-Token-Secret': self._access_token_secret
        }

    @property
    def auth_headers(self):
        """
        Authentication headers for HTTP requests.

        """
        if self.auth_method == AUTH_METHOD_ACCESS_TOKEN:
            return self.access_token_auth_headers
        elif self.auth_method == AUTH_METHOD_CLIENT_KEYS:
            return self.client_auth_headers
        elif self.auth_method == AUTH_METHOD_JWT:
            return self.jwt_auth_headers
        else:
            raise ValueError(
                f'Invalid auth_method "{self.auth_method}": expected one of '
                f'({AUTH_METHOD_CLIENT_KEYS}, {AUTH_METHOD_JWT})'
            )
