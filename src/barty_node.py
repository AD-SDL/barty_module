"""A Node implementation to use in automated tests."""

from typing import Annotated, List

from madsci.client.event_client import EventClient
from madsci.common.types.action_types import (
    ActionFailed,
    ActionRequest,
    ActionRunning,
    ActionSucceeded,
)
from madsci.common.types.base_types import Error
from madsci.common.types.node_types import RestNodeConfig
from madsci.common.utils import threaded_task
from madsci.node_module.abstract_node_module import action
from madsci.node_module.rest_node_module import RestNode

from barty_interface import BartyInterface


class BartyNodeConfig(RestNodeConfig):
    """Configuration for Barty the bartender robot."""

    # Barty has nothing extra to setup in config
    pass


class BartyNode(RestNode):
    """A node for Barty the bartender robot."""

    barty_interface: BartyInterface = None
    config_model = BartyNodeConfig

    logger = EventClient()

    def startup_handler(self) -> None:
        """Initialize or reinitialize Barty."""
        self.logger.log("Barty initializing...")
        self.barty_interface = BartyInterface(logger=self.logger)
        self.logger.log("Barty initialized!")

    def shutdown_handler(self) -> None:
        """Shutdown Barty Node. Close connection and release resources"""
        self.logger.log("Barty shutting down...")
        del self.barty_interface
        self.barty_interface = None
        self.logger.log("Shutdown complete.")

    def state_handler(self) -> None:
        """Periodically called to update the current state of the node."""

    # TODO: implement the following admin actions
    def pause(self) -> None:
        """Pause the node."""
        self.logger.log("Pausing node...")
        self.node_status.paused = True
        self.logger.log("Node paused.")
        return True

    def resume(self) -> None:  # TODO: implement
        """Resume the node."""
        self.logger.log("Resuming node...")
        self.node_status.paused = False
        self.logger.log("Node resumed.")
        return True

    def shutdown(self) -> None:  # TODO: implement
        """Shutdown the node."""
        self.shutdown_handler()
        return True

    def reset(self) -> None:  # TODO: implement
        """Reset the node."""
        self.logger.log("Resetting node...")
        result = super().reset()
        self.logger.log("Node reset.")
        return result

    def safety_stop(self) -> None:  # TODO implement
        """Stop the node."""
        self.logger.log("Stopping node...")
        self.node_status.stopped = True
        self.logger.log("Node stopped.")
        return True

    def cancel(self) -> None:  # TODO: implement
        """Cancel the node."""
        self.logger.log("Canceling node...")
        self.node_status.cancelled = True
        self.logger.log("Node cancelled.")
        return True

    ### ACTIONS ###
    @action(
        name="drain_ink_all_motors",
        description="Drains specified amount of liquid from all motors",
    )
    def drain_all(
        self,
        amount: Annotated[int, "Amount of ink to drain, in milliliters"] = 100,
    ):
        """Drains specified amount of liquid from all motors"""

        self.barty_interface.drain_all(int(amount))
        return ActionSucceeded()

    @action(
        name="fill_ink_all_motors",
        description="fills the specified amount of ink on all pumps",
    )
    def fill_all(
        self, amount: Annotated[int, "Amount of ink to fill, in milliliters"] = 60
    ):
        """Refills the specified amount of liquid from all motors"""

        self.barty_interface.refill_all(int(amount))
        return ActionSucceeded()

    @action(
        name="refill_ink",
        description="fills the specified amount of ink on target pumps",
    )
    def refill_target(
        self,
        action: ActionRequest,
        motors: Annotated[List[int], "motors to run"],
        amount: Annotated[int, "Amount of ink to fill, in milliliters"] = 5,
    ):
        """Refills the specified amount of ink on target pumps"""

        @threaded_task
        def run_refill_target():
            try:
                self.barty_interface.refill(motors, amount)
                self._extend_action_history(ActionSucceeded(action_id=action.action_id))
            except Exception as e:
                self._extend_action_history(
                    ActionFailed(
                        action_id=action.action_id, errors=Error.from_exception(e)
                    )
                )

        run_refill_target()

        return ActionRunning()


if __name__ == "__main__":
    barty_node = BartyNode()
    barty_node.start_node()
