# Barty

This is the repository for Barty, "the bartending robot", a low cost liquid consumable manager developed at Argonne National Lab's Rapid Prototyping Lab.

An example definition file can be found at `definitions/barty.node.yaml` and a description of the node's capabilities can be found at `definitions/barty.node.info.yaml`

## Installation and Usage

### Python

Note: your user must be in the same group as the `/dev/gpiomem` device (likely either `gpio` or `dialout`), in order to access the Raspberry Pi's GPIO pins. Otherwise, you must run the node as root (not recommended)

```bash
# Create a virtual environment named .venv
python -m venv .venv
# Activate the virtual environment on Linux or macOS
source .venv/bin/activate
# Alternatively, activate the virtual environment on Windows
# .venv\Scripts\activate
# Install the module and dependencies in the venv
pip install .
# Start the node
python -m barty_node --definition <path/to/definition.yaml>
```
