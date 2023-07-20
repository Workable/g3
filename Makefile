install:
	poetry install

# Formatting
format-black:
	@black .

format-isort:
	@isort .

format: format-black format-isort

# Linting
lint-black:
	@black --check .

lint-isort:
	@isort --check .

lint-flake8:
	@flake8 .

lint-mypy:
	@mypy .

lint: lint-black lint-isort lint-flake8 lint-mypy

# Testing
test:
	@pytest

test-coverage:
	@pytest --cov=g3 --cov-report=term-missing --cov-report=html

test-coverage-fail:
	@pytest --cov=g3 --cov-report=term-missing --cov-report=html --cov-fail-under=80

# Deployment
clean:
	@rm -rf ./dist

build:
	@poetry build

publish:
	@poetry publish --repository jfrog --username $(ARTIFACTORY_USERNAME) --password $(ARTIFACTORY_API_KEY)

deploy: clean build publish
