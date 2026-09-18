PYTHON ?= python3
VENV ?= .venv
TOOLS := $(VENV)/bin


install:
	$(PYTHON) -m venv $(VENV)
	$(TOOLS)/pip install flake8 mypy

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +

lint:
	$(TOOLS)/flake8 --exclude=$(VENV) --max-line-length=79 .
	$(TOOLS)/mypy --strict .

.PHONY: install run debug clean lint