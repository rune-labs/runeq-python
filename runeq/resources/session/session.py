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

    def __init__(
        self,
        config: BaseConfig,
    ):
        graph_client = GraphClient(config)
        stream_client = StreamClient(config)
        strive_client = StriveClient(config)

        self.org = OrgNamespace(graph_client)
        self.event = EventNamespace(graph_client)
        self.patient = PatientNamespace(graph_client)
        self.project = ProjectNamespace(graph_client)
        self.sleep = SleepNamespace(strive_client)
        self.stream_metadata = StreamMetadataNamespace(graph_client)
        self.stream = StreamNamespace(stream_client)
