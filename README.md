# Barty

This is the repository for Barty, the low cost liquid handler developed at Argonne National Lab's Rapid Prototyping Lab.

## Installation

Note: your user must be in the same group as the `/dev/gpiomem` device (likely either `gpio` or `dialout`), in order to access the Raspberry Pi's GPIO pins.

```
git clone https://github.com/AD-SDL/barty_module.git
cd barty_module
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```
cd barty_module
source .venv/bin/activate
python -m barty_module --port 8000
```
