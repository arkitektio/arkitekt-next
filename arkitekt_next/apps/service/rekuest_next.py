from arkitekt_next_next.healthz import FaktsHealthz
from rath.contrib.fakts.links.aiohttp import FaktsAIOHttpLink
from rath.links.split import SplitLink
from rath.contrib.fakts.links.graphql_ws import FaktsGraphQLWSLink
from rath.contrib.herre.links.auth import HerreAuthLink
from rekuest_next.rath import RekuestNextLinkComposition, RekuestNextRath
from rekuest_next.rekuest import RekuestNext
from graphql import OperationType
from rekuest_next.contrib.arkitekt_next.websocket_agent_transport import (
    ArkitektNextWebsocketAgentTransport,
)

from rekuest_next.agents.base import BaseAgent
from fakts import Fakts
from herre import Herre
from rekuest_next.postmans.graphql import GraphQLPostman


class ArkitektNextRekuestNext(RekuestNext):
    rath: RekuestNextRath
    agent: BaseAgent
    healthz: FaktsHealthz


def build_arkitekt_next_rekuest_next(
    fakts: Fakts, herre: Herre, instance_id: str
) -> ArkitektNextRekuestNext:
    rath = RekuestNextRath(
        link=RekuestNextLinkComposition(
            auth=HerreAuthLink(herre=herre),
            split=SplitLink(
                left=FaktsAIOHttpLink(fakts_group="rekuest", fakts=fakts),
                right=FaktsGraphQLWSLink(fakts_group="rekuest", fakts=fakts),
                split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
            ),
        )
    )

    return ArkitektNextRekuestNext(
        rath=rath,
        agent=BaseAgent(
            transport=ArkitektNextWebsocketAgentTransport(
                fakts_group="rekuest.agent", fakts=fakts, herre=herre
            ),
            instance_id=instance_id,
            rath=rath,
        ),
        postman=GraphQLPostman(
            rath=rath,
            instance_id=instance_id,
        ),
        healthz=FaktsHealthz(fakts_group="rekuest", fakts=fakts),
    )
