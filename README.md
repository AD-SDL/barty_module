# Barty

This is the repository for Barty, the low cost liquid handler developed at Argonne National Lab's Rapid Prototyping Lab.

## Installation

```
git clone https://github.com/AD-SDL/barty_module.git
cd barty_module
pip install -r requirements/requirements.txt
pip install -e .
```

## Usage

```
cd barty_module/barty_node
sudo uvicorn barty_rest_node:app --host=<hostname> --port=8000
```
