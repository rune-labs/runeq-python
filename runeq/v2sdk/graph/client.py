"""
Rune graph API client.

"""
import ast
from typing import Dict, Iterator, Optional

from gql import Client as GQLClient, gql
from gql.transport.requests import RequestsHTTPTransport

from runeq.config import AUTH_METHOD_CLIENT_KEYS, Config

from .model import GraphID


class RuneGraphAPIError(Exception):
    """
    Error from the Graph API.

    """


class RuneGraphNotFoundError(RuneGraphAPIError):
    """
    Graph API error indicating requested resource was not found.

    """


class GraphAPIClient:
    """
    Version 2 client for the Rune GraphQL API.

    """

    _config: Config
    """
    Reference to the SDK client configuration.

    """

    _gqlclient: GQLClient
    """
    The GraphQL client.

    """


    def __init__(self, config: Config):
        """
        Initialize the Graph API client.

        """
        self._config = config
        self._gqlclient = GQLClient(
            transport=RequestsHTTPTransport(
                retries=10,
                url=f"{config.graph_url}/graphql",
                use_json=True,
                headers={
                    'Content-Type': "application/json",
                    **config.auth_headers
                }
            ),
            fetch_schema_from_transport=True,
        )


    def fetch_patient(self, patient_id: GraphID) -> Optional[Dict]:
        """
        Attempt to retrieve a single patient by ID.

        """
        response = self.query(
            '''
            query($patientId: ID!) {
                patient(id: $patientId) {
                    id
                    codeName
                    createdAt
                }
            }
            ''',
            patientId=str(patient_id)
        )

        return response['patient']


    def list_patient_devices(self, patient_id: GraphID) -> Iterator[Dict]:
        """
        List all devices for a patient.

        """
        cursor = None

        while True:
            response = self.query(
                '''
                query(
                    $patientId: ID!,
                    $withDisabled: Boolean!,
                    $cursor: Cursor
                ) {
                    patient(id: $patientId) {
                        deviceList(
                            withDisabled: $withDisabled,
                            cursor: $cursor
                        ) {
                            devices {
                                id
                                alias
                                createdAt
                                deviceType {
                                    id
                                    displayName
                                }
                            }
                            pageInfo {
                                endCursor
                            }
                        }
                    }
                }
                ''',
                cursor=cursor,
                patientId=str(patient_id),
                withDisabled=False
            )
            result = response['patient']['deviceList']

            for device in result['devices']:
                device['patientId'] = patient_id.unqualified
                yield device

            cursor = result['pageInfo'].get('endCursor')

            if not cursor:
                break


    def list_patients(self) -> Iterator[Dict]:
        """
        List all patients this user has access to.

        """
        cursor = None

        while True:
            response = self.query(
                '''
                query($cursor: Cursor) {
                    org {
                        patientAccessList(cursor: $cursor) {
                            pageInfo {
                                endCursor
                            }
                            patientAccess {
                                patient {
                                    id
                                    codeName
                                    createdAt
                                }
                            }
                        }
                    }
                }
                ''',
                cursor=cursor
            )
            result = response['org']['patientAccessList']

            for patient_access in result['patientAccess']:
                yield patient_access['patient']

            cursor = result['pageInfo'].get('endCursor')

            if not cursor:
                break


    def query(self, statement: str, **variables) -> Dict:
        """
        Execute a GraphQL query against the API.

        """
        try:
            return self._gqlclient.execute(
                gql(statement),
                variable_values=variables
            )
        except Exception as error:
            #
            # Hack around GQL 2.0's lousy error reporting. Looks like there
            # may be a better client in the works.
            #
            try:
                detail = ast.literal_eval(error.args[0])
            except ValueError:
                raise RuneGraphAPIError(*error.args) from None

            if detail['extensions']['code'] == 'NotFoundError':
                raise RuneGraphNotFoundError() from None
            else:
                raise RuneGraphAPIError(detail['message']) from None


    def whoami(self) -> Dict:
        """
        Query the identity of either the patient or user whose credentials are
        configured.

        """
        if self._config.auth_method == AUTH_METHOD_CLIENT_KEYS:
            return self.query(
                '''
                query {
                    patient {
                        id
                        codeName
                        createdAt
                    }
                }
                '''
            )
        else:
            return self.query(
                '''
                query {
                    user {
                        id
                        created
                        defaultMembership {
                            id
                            created
                            org {
                                id
                                created
                                displayName
                            }
                        }
                        displayName
                        email
                        username
                    }
                }
                '''
            )
