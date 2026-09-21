UV ?= uv

install:
	$(UV) sync

run:
	$(UV) run python a_maze_ing.py config.txt

debug:
	$(UV) run python -m pdb a_maze_ing.py config.txt

clean:
	rm -rf .venv build dist
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
	find . -type d -name '*.egg-info' -prune -exec rm -rf {} +

lint:
	$(UV) run flake8 --exclude=.venv .
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV) run mypy --strict .
	$(UV) run flake8 --exclude=.venv .

mazegen-release:
	$(UV) build --out-dir .

.PHONY: install run debug clean lint lint-strict mazegen-release
