POETRY ?= poetry
DOCKER ?= docker

CLI_IMAGE ?= judicor-cli:local
CONTROL_IMAGE ?= judicor-control-plane:local

.PHONY: install test format run-cli run-control docker-build-cli docker-build-control docker-run-control ci

install:
	$(POETRY) install

test:
	$(POETRY) run pytest --cov=judicor --cov-report=term-missing

format:
	$(POETRY) run black src tests

lint:
	$(POETRY) run flake8 src tests

run-cli:
	$(POETRY) run judicor --help

run-control:
	$(POETRY) run uvicorn judicor.control_plane.app:app --host 0.0.0.0 --port 8000 --reload

docker-build-cli:
	$(DOCKER) build -f docker/Dockerfile.cli -t $(CLI_IMAGE) .

docker-build-control:
	$(DOCKER) build -f docker/Dockerfile.control-plane -t $(CONTROL_IMAGE) .

docker-run-control:
	$(DOCKER) run --rm -p 8000:8000 $(CONTROL_IMAGE)

ci: format test
