.DEFAULT_GOAL := all
package_name = barty_node
extra_folders = test/
isort = python -m isort -rc --atomic $(package_name) $(extra_folders)
black = python -m black --target-version py37 $(package_name) $(extra_folders)
flake8 = python -m flake8 $(package_name)/ $(extra_folders)
pylint = python -m pylint $(package_name)/ $(extra_folders)
pydocstyle = python -m pydocstyle $(package_name)/
run_mypy = python -m mypy --config-file setup.cfg


.PHONY: format
format:
	$(black)
	$(isort)

.PHONY: lint
lint:
	$(black) --check --diff
	$(flake8)
	$(pydocstyle)

.PHONY: mypy
mypy:
	$(run_mypy) --package $(package_name)
	$(run_mypy) $(package_name)/
	$(run_mypy) $(extra_folders)


.PHONY: all
all: format lint
