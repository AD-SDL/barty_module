"""A Node implementation to use in automated tests."""

from typing import Annotated, List

from madsci.client.resource_client import ResourceClient
from madsci.common.types.action_types import ActionSucceeded
from madsci.common.types.node_types import RestNodeConfig
from madsci.common.types.resource_types.definitions import (
    ContinuousConsumableResourceDefinition,
)
from madsci.node_module.helpers import action
from madsci.node_module.rest_node_module import RestNode

from barty_interface import BartyInterface


class BartyNodeConfig(RestNodeConfig):
    """Configuration for Barty the bartender robot."""

    consumable_name_map: List[str] = [
        "Red Ink",
        "Blue Ink",
        "Yellow Ink",
        "Black Ink",
    ]
    """A list of consumable names to be used by Barty. The order of the names should match the order of the pumps."""
    supply_definitions: List[ContinuousConsumableResourceDefinition] = [
        ContinuousConsumableResourceDefinition(
            resource_name=f"{name} Supply Reservoir",
            resource_description=f"Consumable resource {name} for Barty",
            quantity=250,
            capacity=250,  # *We're using 250ml beakers in the RPL
            unit="mL",
        )
        for name in consumable_name_map
    ]
    """A list of consumable definitions to be used by Barty. The order of the definitions should match the order of the pumps."""
    target_definitions: List[ContinuousConsumableResourceDefinition] = [
        ContinuousConsumableResourceDefinition(
            resource_name=f"{name} Target Reservoir",
            capacity=150,  # *We're using 150ml deep reso in the RPL
            unit="mL",
        )
        for name in consumable_name_map
    ]
    """A list of target resource IDs to be used by Barty. The order of the IDs should match the order of the pumps.
    These are the resource IDs of the pools that we're filling using barty, not Barty's own resources."""
    simulate: bool = False
    """Whether to simulate the Barty interface."""


class BartyNode(RestNode):
    """A node for Barty the bartender robot."""

    barty_interface: BartyInterface = None
    config_model = BartyNodeConfig
    config: BartyNodeConfig

    source_reservoir_ids: list[str] = []
    target_reservoir_ids: list[str] = []

    def startup_handler(self) -> None:
        """Initialize or reinitialize Barty."""
        self.logger.log("Barty initializing...")
        if self.config.simulate:
            self.barty_interface = BartyInterface(logger=self.logger, simulate=True)
        else:
            self.barty_interface = BartyInterface(logger=self.logger, simulate=False)
        self.resource_client = (
            ResourceClient(self.config.resource_server_url)
            if self.config.resource_server_url
            else None
        )
        self.source_reservoir_ids = []
        self.target_reservoir_ids = []
        if self.resource_client is not None:
            for i in range(4):
                resource = self.resource_client.init_resource(
                    self.config.supply_definitions[i]
                )
                self.source_reservoir_ids.append(resource.resource_id)
                self.logger.log_debug(
                    f" Source Reservoir {i} ID: {resource.resource_id}"
                )
                resource = self.resource_client.init_resource(
                    self.config.target_definitions[i]
                )
                self.target_reservoir_ids.append(resource.resource_id)
                self.logger.log_debug(
                    f"Target Reservoir {i} ID: {resource.resource_id}"
                )

        self.logger.log("Barty initialized!")

    def shutdown_handler(self) -> None:
        """Shutdown Barty Node. Close connection and release resources"""
        self.logger.log("Barty shutting down...")
        if self.barty_interface:
            del self.barty_interface
            self.barty_interface = None
        self.logger.log("Shutdown complete.")

    def transfer(self, source, target, amount):
        """Transfer liquid from source to target"""
        source_resource = self.resource_client.get_resource(source)
        target_resource = self.resource_client.get_resource(target)
        available = source_resource.quantity
        self.resource_client.decrease_quantity(source_resource, amount)
        self.resource_client.increase_quantity(target_resource, min(amount, available))

    ### ACTIONS ###
    @action
    def fill_all(
        self, amount: Annotated[float, "Amount of liquid to fill, in milliliters"] = 10
    ):
        """Refills the specified amount of liquid from all motors"""

        self.barty_interface.fill_all(int(amount))
        if self.resource_client:
            for i in range(4):
                self.transfer(
                    self.source_reservoir_ids[i], self.target_reservoir_ids[i], amount
                )
        return ActionSucceeded()

    @action
    def drain_all(
        self,
        amount: Annotated[float, "Amount of liquid to drain, in milliliters"] = 10,
    ):
        """Drains specified amount of liquid from all motors"""

        self.barty_interface.drain_all(int(amount))
        if self.resource_client:
            for i in range(4):
                self.transfer(
                    self.target_reservoir_ids[i], self.source_reservoir_ids[i], amount
                )
        return ActionSucceeded()

    @action
    def fill(
        self,
        pumps: Annotated[List[int], "Pumps to refill with"],
        amount: Annotated[float, "Amount of ink to fill, in milliliters"] = 5,
    ):
        """Refills the specified amount of liquid on target pumps"""

        self.barty_interface.fill(pumps, amount)
        for pump in pumps:
            self.transfer(
                self.source_reservoir_ids[pump], self.target_reservoir_ids[pump], amount
            )
        return ActionSucceeded()

    @action
    def drain(
        self,
        pumps: Annotated[List[int], "Pumps to drain from"],
        amount: Annotated[float, "Amount of ink to drain, in milliliters"] = 5,
    ):
        """Drains the specified amount of liquid from target pumps"""

        self.barty_interface.drain(pumps, amount)
        for pump in pumps:
            self.transfer(
                self.target_reservoir_ids[pump], self.source_reservoir_ids[pump], amount
            )
        return ActionSucceeded()


if __name__ == "__main__":
    barty_node = BartyNode()
    barty_node.start_node()
