UV ?= uv

install:
	$(UV) sync

run:
	$(UV) run python a_maze_ing.py config.txt

debug:
	$(UV) run python -m pdb a_maze_ing.py config.txt

clean:
	rm -rf .venv
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +

lint:
	$(UV) run flake8 --exclude=.venv --max-line-length=79 .
	$(UV) run mypy --strict .

.PHONY: install run debug clean lint