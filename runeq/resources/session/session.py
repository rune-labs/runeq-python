import warnings

from runeq.config import BaseConfig
from runeq.resources.client import (
    INITIALIZATION_ERROR,
    GraphClient,
    StreamClient,
    StriveClient,
    global_graph_client,
    global_stream_client,
    global_strive_client,
)
from runeq.resources.session.namespaces import (
    EventNamespace,
    OrgNamespace,
    PatientNamespace,
    ProjectNamespace,
    SleepNamespace,
    StreamMetadataNamespace,
    StreamNamespace,
    UserNamespace,
)


class Session:
    """
    Session object to access Rune APIs.
    """

    org: OrgNamespace
    event: EventNamespace
    patient: PatientNamespace
    project: ProjectNamespace
    sleep: SleepNamespace
    stream_metadata: StreamMetadataNamespace
    stream: StreamNamespace
    user: UserNamespace

    graph_client: GraphClient
    stream_client: StreamClient
    strive_client: StriveClient

    def __init__(
        self,
        config: BaseConfig,
    ):
        self._check_initialized()

        self.graph_client = GraphClient(config)
        self.stream_client = StreamClient(config)
        self.strive_client = StriveClient(config)

        self.org = OrgNamespace(self.graph_client)
        self.event = EventNamespace(self.graph_client)
        self.patient = PatientNamespace(self.graph_client)
        self.project = ProjectNamespace(self.graph_client)
        self.sleep = SleepNamespace(self.strive_client)
        self.stream_metadata = StreamMetadataNamespace(
            self.graph_client, self.stream_client
        )
        self.stream = StreamNamespace(self.stream_client)
        self.user = UserNamespace(self.graph_client)

    def _check_initialized(self):
        """
        Check if runeq has been globally initialized.
        """
        try:
            global_graph_client()
            global_stream_client()
            global_strive_client()
        except INITIALIZATION_ERROR:
            pass
        else:
            warnings.warn(
                "runeq has been globally initialized, and you are using a session-based client. You probably want to use one or the other.",
                stacklevel=2,
            )
