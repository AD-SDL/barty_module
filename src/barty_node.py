"""A Node implementation to use in automated tests."""

from typing import Annotated, ClassVar, List

from madsci.common.ownership import get_current_ownership_info
from madsci.common.types.action_types import ActionFailed, ActionSucceeded
from madsci.common.types.node_types import RestNodeConfig
from madsci.common.types.resource_types import ContinuousConsumable
from madsci.node_module.helpers import action
from madsci.node_module.rest_node_module import RestNode
from pydantic import Field

from barty_interface import BartyInterface


class BartyNodeConfig(RestNodeConfig):
    """Configuration for Barty the bartender robot."""

    consumable_name_map: List[str] = Field(
        default_factory=lambda: [
            "Red Ink",
            "Blue Ink",
            "Yellow Ink",
            "Black Ink",
        ]
    )
    """A list of consumable names to be used by Barty. The order of the names should match the order of the pumps."""
    simulate: bool = False
    """Whether to simulate the Barty interface."""


class BartyNode(RestNode):
    """A node for Barty the bartender robot."""

    barty_interface: BartyInterface = None
    config_model = BartyNodeConfig
    config: BartyNodeConfig = BartyNodeConfig()

    source_reservoir_ids: ClassVar[list[str]] = []
    target_reservoir_ids: ClassVar[list[str]] = []

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
                resource_name=f"{self.node_info.node_name} {material_name} Supply Reservoir",
                overrides={
                    "resource_description": f"Supply reservoir for {material_name} used by {self.node_info.node_name}",
                },
            )
            self.source_reservoir_ids.append(source_resource.resource_id)
            self.logger.log_debug(
                f" Source Reservoir '{material_name}' ID: {source_resource.resource_id}"
            )
            target_resource = self.resource_client.create_resource_from_template(
                template_name="barty_target_reservoir",
                resource_name=f"{self.node_info.node_name} {material_name} Target Reservoir",
                overrides={
                    "resource_description": f"Target reservoir for {material_name} used by {self.node_info.node_name}",
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

    def transfer(self, source: str, target: str, amount: float) -> None:
        """Transfer liquid from source to target"""
        source_resource = self.resource_client.get_resource(source)
        target_resource = self.resource_client.get_resource(target)
        available = source_resource.quantity
        self.resource_client.decrease_quantity(source_resource, amount)
        self.resource_client.increase_quantity(target_resource, min(amount, available))

    def _adjust_to_targets(
        self, targets: dict[int, float]
    ) -> ActionSucceeded | ActionFailed:
        """Adjust target reservoirs to the specified levels by filling or draining as needed.

        Args:
            targets: A mapping of pump index (0-3) to desired level in mL.

        Returns:
            ActionSucceeded with per-pump deltas, or ActionFailed on validation error.
        """
        num_pumps = len(self.config.consumable_name_map)
        for pump in targets:
            if pump < 0 or pump >= num_pumps:
                return ActionFailed(
                    errors=[f"Invalid pump index {pump}. Must be 0 to {num_pumps - 1}."]
                )

        for pump, target_level in targets.items():
            if target_level < 0:
                return ActionFailed(
                    errors=[
                        f"Target level for pump {pump} must be >= 0, got {target_level}."
                    ]
                )
            target_resource = self.resource_client.get_resource(
                self.target_reservoir_ids[pump]
            )
            if target_level > target_resource.capacity:
                return ActionFailed(
                    errors=[
                        f"Target level for pump {pump} ({target_level} mL) exceeds "
                        f"reservoir capacity ({target_resource.capacity} mL)."
                    ]
                )

        deltas = {}
        for pump, target_level in targets.items():
            target_resource = self.resource_client.get_resource(
                self.target_reservoir_ids[pump]
            )
            current_level = target_resource.quantity
            delta = target_level - current_level

            if delta > 0:
                self.barty_interface.fill([pump], delta)
                self.transfer(
                    self.source_reservoir_ids[pump],
                    self.target_reservoir_ids[pump],
                    delta,
                )
            elif delta < 0:
                self.barty_interface.drain([pump], abs(delta))
                self.transfer(
                    self.target_reservoir_ids[pump],
                    self.source_reservoir_ids[pump],
                    abs(delta),
                )

            deltas[pump] = delta

        return ActionSucceeded(json_result={"deltas": deltas})

    ### ACTIONS ###
    @action
    def fill_all(
        self, amount: Annotated[float, "Amount of liquid to fill, in milliliters"] = 10
    ) -> ActionSucceeded:
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
    ) -> ActionSucceeded:
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
    ) -> ActionSucceeded:
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
    ) -> ActionSucceeded:
        """Drains the specified amount of liquid from target pumps"""

        self.barty_interface.drain(pumps, amount)
        for pump in pumps:
            self.transfer(
                self.target_reservoir_ids[pump], self.source_reservoir_ids[pump], amount
            )
        return ActionSucceeded()

    @action
    def drain_to_empty(
        self,
        pumps: Annotated[List[int], "Pumps to drain from"],
    ) -> ActionSucceeded:
        """Drains the specified pumps until they are empty"""

        for pump in pumps:
            target_resource = self.resource_client.get_resource(
                self.target_reservoir_ids[pump]
            )
            amount = target_resource.quantity
            self.barty_interface.drain([pump], amount)
            self.transfer(
                self.target_reservoir_ids[pump],
                self.source_reservoir_ids[pump],
                amount,
            )
        return ActionSucceeded()

    @action
    def drain_all_to_empty(self) -> ActionSucceeded:
        """Drains all pumps until they are empty"""

        for i in range(4):
            target_resource = self.resource_client.get_resource(
                self.target_reservoir_ids[i]
            )
            amount = target_resource.quantity
            self.barty_interface.drain([i], amount)
            self.transfer(
                self.target_reservoir_ids[i], self.source_reservoir_ids[i], amount
            )
        return ActionSucceeded()

    @action
    def fill_to_target(
        self,
        targets: Annotated[
            dict[int, float],
            "Mapping of pump index (0-3) to target level in mL",
        ],
    ) -> ActionSucceeded | ActionFailed:
        """Fills or drains each specified pump to reach the target level"""

        return self._adjust_to_targets(targets)

    @action
    def fill_all_to_target(
        self,
        target_level: Annotated[
            float,
            "Target level in mL for all reservoirs",
        ],
    ) -> ActionSucceeded | ActionFailed:
        """Fills or drains all pumps to reach the specified target level"""

        targets = dict.fromkeys(
            range(len(self.config.consumable_name_map)), target_level
        )
        return self._adjust_to_targets(targets)


if __name__ == "__main__":
    barty_node = BartyNode()
    barty_node.start_node()
