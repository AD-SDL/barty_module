"""A Node implementation to use in automated tests."""

from typing import Annotated, List, Optional

from madsci.client.event_client import EventClient
from madsci.client.resource_client import ResourceClient
from madsci.common.types.node_types import RestNodeConfig
from madsci.common.types.resource_types import ContinuousConsumable, ResourceTypeEnum
from madsci.node_module.helpers import action
from madsci.node_module.rest_node_module import RestNode
from pydantic.networks import AnyUrl

from barty_interface import BartyInterface


class BartyNodeConfig(RestNodeConfig):
    """Configuration for Barty the bartender robot."""

    consumable_name_map: List[str] = [
        "Red Ink",
        "Blue Ink",
        "Yellow Ink",
        "Black Ink",
    ]
    resource_server_url: Optional[AnyUrl] = None


class BartyNode(RestNode):
    """A node for Barty the bartender robot."""

    barty_interface: BartyInterface = None
    config_model = BartyNodeConfig
    config: BartyNodeConfig

    consumables: list[ContinuousConsumable] = []

    def startup_handler(self) -> None:
        """Initialize or reinitialize Barty."""
        self.logger.log("Barty initializing...")
        # self.barty_interface = BartyInterface(logger=self.logger)
        self.resource_client = (
            ResourceClient(self.config.resource_server_url)
            if self.config.resource_server_url
            else None
        )
        self.event_client = EventClient(self.config.event_client_config)
        self.consumables = []
        for i in range(4):
            consumable_name = self.config.consumable_name_map[i]
            if self.resource_client is not None:
                candidates = self.resource_client.query_resource(
                    resource_name=consumable_name,
                    base_type=ResourceTypeEnum.continuous_consumable,
                    multiple=True,
                    unique=False,
                )
                for candidate in candidates:
                    if candidate.owner.node_id == self.node_definition.node_id:
                        self.consumables.append(candidate)
                        break
                else:
                    self.consumables.append(
                        ContinuousConsumable(
                            resource_name=consumable_name,
                            owner=self.node_definition.node_id,
                        )
                    )
                    self.resource_client.add_resource(self.consumables[i])
            else:
                self.consumables.append(
                    ContinuousConsumable(
                        resource_name=consumable_name,
                        owner=self.node_definition.node_id,
                        quantity=0,
                    )
                )

        self.logger.log("Barty initialized!")

    def shutdown_handler(self) -> None:
        """Shutdown Barty Node. Close connection and release resources"""
        self.logger.log("Barty shutting down...")
        if self.barty_interface:
            del self.barty_interface
            self.barty_interface = None
        self.logger.log("Shutdown complete.")

    def state_handler(self) -> None:
        """Periodically called to update the current state of the node."""
        self.node_state = {
            "consumables": [
                consumable.model_dump(mode="json") for consumable in self.consumables
            ],
        }

    ### ACTIONS ###
    @action
    def drain_all(
        self,
        amount: Annotated[float, "Amount of liquid to drain, in milliliters"] = 10,
    ):
        """Drains specified amount of liquid from all motors"""

        self.barty_interface.drain_all(int(amount))

    @action
    def fill_all(
        self, amount: Annotated[float, "Amount of liquid to fill, in milliliters"] = 10
    ):
        """Refills the specified amount of liquid from all motors"""

        self.barty_interface.fill_all(int(amount))

    @action
    def fill(
        self,
        pumps: Annotated[List[int], "Pumps to refill with"],
        amount: Annotated[float, "Amount of ink to fill, in milliliters"] = 5,
    ):
        """Refills the specified amount of liquid on target pumps"""

        self.barty_interface.fill(pumps, amount)

    @action
    def drain(
        self,
        pumps: Annotated[List[int], "Pumps to drain from"],
        amount: Annotated[float, "Amount of ink to drain, in milliliters"] = 5,
    ):
        """Drains the specified amount of liquid from target pumps"""

        self.barty_interface.drain(pumps, amount)


if __name__ == "__main__":
    barty_node = BartyNode()
    barty_node.start_node()
