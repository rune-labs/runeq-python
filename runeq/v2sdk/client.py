"""
Version 2 client for Rune's query APIs.

"""
from time import time
from typing import Optional, Union

from runeq import Config
from .devices import DeviceQuery
from .graph.client import GraphAPIClient
from .patients import PatientsQuery, Patient, PatientSet
from .users import User


class ClientSession:
    """
    Version 2 client for interacting with data on the Rune platform.

    """

    _caching: bool
    """
    Whether caching is enabled for this session.

    """

    _config: Config
    """
    The SDK configuration.

    """

    _graph: GraphAPIClient
    """
    Graph API client.

    """

    _me: Optional[Union[User, Patient]] = None
    """
    Cached caller identity.

    """

    _now: Optional[float] = None
    """
    Timestamp to use to limit query results instead of actual current time.

    """

    _patient_cache: PatientSet
    """
    Cached patient set.

    """


    def __init__(self, config: Config, caching=True):
        """
        Initialize the client.

        """
        self._caching = caching
        self._config = config
        self._graph = GraphAPIClient(config=config)
        self._patient_cache = PatientSet()


    @property
    def devices(self):
        """
        Begin a new query over devices across all patients.

        """
        return DeviceQuery(session=self)


    def freeze_time(self, at: Optional[float] = None):
        """
        Limit all queries to data available at the time of this call, and not
        after. This acts like an implicit end time for all your queries.

        Use this at the beginning of a multi-step analysis to prevent the
        possibility of new incoming data becoming available between subsequent
        queries. This can also increase performance in certain cases.

        For example, if you freeze at time T, you will consistently get the
        list of the same patients throughout your notebook, no matter how long
        it takes to run all the cells, and even if a new patient is registered
        at time T+1.

        at
            UNIX timestamp of time to limit results to. Default is now.

        """
        self._now = time() if at is None else at


    @property
    def graph(self) -> GraphAPIClient:
        """
        Reference to the graph client.

        """
        return self._graph


    @property
    def me(self) -> Union[User, Patient]:
        """
        Return information about the user identity whose credentials are
        configured.

        Information is loaded directly from the Rune API, and thus makes this
        a good utility for verifying your local configuration and API
        credentials.

        """
        if self._me is None:
            ident = self.graph.whoami()

            if 'patient' in ident:
                self._me = Patient(ident['patient'], session=self)
            else:
                self._me = User(ident['user'], session=self)

        return self._me


    @property
    def patients(self):
        """
        Begin a new query over patients accessible to this client.

        """
        return PatientsQuery(session=self)


    def unfreeze_time(self):
        """
        Remove the implicit time bound on results.

        """
        self._patient_cache = PatientSet()
        self._now = None

