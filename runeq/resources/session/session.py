from runeq.config import BaseConfig
from runeq.resources.client import GraphClient, StreamClient, StriveClient
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
