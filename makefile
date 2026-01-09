POETRY ?= poetry

.PHONY: install test format

install:
	$(POETRY) install

test:
	$(POETRY) run pytest --cov=judicor --cov-report=term-missing

format:
	$(POETRY) run black src tests
