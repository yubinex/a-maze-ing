UV ?= uv
CONFIG ?= config.txt

install:
	$(UV) sync

run:
	$(UV) run python a_maze_ing.py "$(CONFIG)"

debug:
	$(UV) run python -m pdb a_maze_ing.py "$(CONFIG)"

clean:
	rm -rf .venv build dist maze.txt
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -prune -exec rm -rf {} +
	find . -type d -name '*.egg-info' -prune -exec rm -rf {} +

lint:
	$(UV) run flake8 --exclude=.venv .
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV) run mypy --strict .
	$(UV) run flake8 --exclude=.venv .

test:
	$(UV) run python -m unittest discover -s tests

mazegen-release:
	$(UV) build --out-dir .

.PHONY: install run debug clean lint lint-strict test mazegen-release
