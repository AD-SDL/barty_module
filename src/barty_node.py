"""A Node implementation to use in automated tests."""

from typing import Annotated, List

from madsci.common.ownership import get_current_ownership_info
from madsci.common.types.action_types import ActionSucceeded
from madsci.common.types.node_types import RestNodeConfig
from madsci.common.types.resource_types import ContinuousConsumable
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
    simulate: bool = False
    """Whether to simulate the Barty interface."""


class BartyNode(RestNode):
    """A node for Barty the bartender robot."""

    barty_interface: BartyInterface = None
    config_model = BartyNodeConfig
    config: BartyNodeConfig = BartyNodeConfig()

    source_reservoir_ids: list[str] = []
    target_reservoir_ids: list[str] = []

    def resource_template_init(self) -> None:
        """Handle template creation for Barty"""

        self.resource_client.init_template(
            resource=ContinuousConsumable(
                resource_name="Barty Supply Reservoir Template",
                resource_class="BartySupplyReservoir",
                quantity=250,
                capacity=250,  # *We're using 250ml beakers in the RPL
                unit="mL",
            ),
            template_name="barty_supply_reservoir",
            description="Template for Barty supply reservoirs",
            required_overrides=["resource_name", "quantity"],
            tags=["barty", "supply_reservoir"],
            created_by=get_current_ownership_info().node_id,
            version="1.0.0",
        )
        self.resource_client.init_template(
            resource=ContinuousConsumable(
                resource_name="Barty Target Reservoir Template",
                resource_class="BartyTargetReservoir",
                quantity=0,
                capacity=150,  # *We're using 150ml deep reservoirs in the RPL
                unit="mL",
            ),
            template_name="barty_target_reservoir",
            description="Template for Barty target reservoirs",
            required_overrides=["resource_name", "quantity"],
            tags=["barty", "target_reservoir"],
            created_by=get_current_ownership_info().node_id,
            version="1.0.0",
        )

    def resource_init(self) -> None:
        """Handle resource initialization for Barty"""

        self.source_reservoir_ids = []
        self.target_reservoir_ids = []
        for material_name in self.config.consumable_name_map:
            source_resource = self.resource_client.create_resource_from_template(
                template_name="barty_supply_reservoir",
                resource_name=f"{self.node_definition.node_name} {material_name} Supply Reservoir",
                overrides={
                    "resource_description": f"Supply reservoir for {material_name} used by {self.node_definition.node_name}",
                },
            )
            self.source_reservoir_ids.append(source_resource.resource_id)
            self.logger.log_debug(
                f" Source Reservoir '{material_name}' ID: {source_resource.resource_id}"
            )
            target_resource = self.resource_client.create_resource_from_template(
                template_name="barty_target_reservoir",
                resource_name=f"{self.node_definition.node_name} {material_name} Target Reservoir",
                overrides={
                    "resource_description": f"Target reservoir for {material_name} used by {self.node_definition.node_name}",
                },
            )
            self.target_reservoir_ids.append(target_resource.resource_id)
            self.logger.log_debug(
                f"Target Reservoir '{material_name}' ID: {target_resource.resource_id}"
            )

    def startup_handler(self) -> None:
        """Initialize or reinitialize Barty."""
        self.logger.log("Barty initializing...")
        self.barty_interface = BartyInterface(
            logger=self.logger, simulate=self.config.simulate
        )
        self.resource_template_init()
        self.resource_init()

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
