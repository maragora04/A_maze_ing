PYTHON   := python3
MAIN     := a_maze_ing.py
CONFIG   := config.txt
MYPY_FLAGS := --warn-return-any --warn-unused-ignores \
              --ignore-missing-imports --disallow-untyped-defs \
              --check-untyped-defs

# never write __pycache__ when running through make
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: install run debug clean lint lint-strict build

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install flake8 mypy build

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .mypy_cache -prune -exec rm -rf {} +
	rm -rf build dist *.egg-info

lint:
	flake8 .
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 .
	mypy . --strict

build: clean
	$(PYTHON) -m build
	cp dist/* .

run:
	-$(PYTHON) $(MAIN) $(CONFIG)
	@$(MAKE) --no-print-directory clean