# Barty

This is the repository for Barty, "the bartending robot", a low cost liquid consumable manager developed at Argonne National Lab's Rapid Prototyping Lab.

## Installation and Usage

### Python

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
python src/barty_module --definition <path/to/definition.yaml>
```
