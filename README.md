# G3
All-in-one CLI to commit your work to Github [[Docs](https://docs.google.com/presentation/d/1BZN4cfeGYR9U4UjXF6wH_-x9l8DwGOgJRZr7UDKXiMQ/)]

## Install
```bash
pip install g3
```

## Configuration

```bash
g3 configure
```

You will be asked to enter:
- your Github token 
- your open-ai key
- the openai model you want to use
- the temperature which will be used to generate the commit messages and PR descriptions
- the openai api version
- the tone which will be used in the commit messages and PR descriptions
- the commit message max characters
- the PR description max words


## Usage

### Commit

```bash
g3 commit
```

#### Options:
- --tone: The tone used
- --jira: The jira ticket(s) referenced
- --include: Include a phrase you want
- --edit: On a commit

### PR

```bash
g3 pr
```

#### Options:
- --tone: The tone used
- --jira: The jira ticket(s) referenced
- --include: Include a phrase you want
- --edit: On a pr

### Alias

You can also make an `alias g=g3` so that you execute simply `g commit` and `g pr`.

## Development

The project requires `Python 3.11` and [Poetry](https://python-poetry.org/docs/#installation) for dependency management. 

Optionally configure poetry to create the virtual environment within the project as follows:
```shell script
poetry config virtualenvs.in-project true
```

### Build

Now install the project, along with its development dependencies, in a local virtual environment as follows:

```shell
poetry install
```
You may enable the virtual environment, so that you run modules without the `poetry run` prefix, as follows:
```
source `poetry env info -p`/bin/activate
```
or simply as follows:
```
poetry shell
```

### Contribution

You are expected to enable pre-commit hooks so that you get your code auto-sanitized before being committed.
* mypy:   Static type checker of variables and functions based on [PEP 484](https://peps.python.org/pep-0484/) 
* isort:  Optimizes imports
* black:  Opinionated code formatter based on [PEP 8](https://peps.python.org/pep-0008/) 
* flake8: Improves code style and quality based on [PEP 8](https://peps.python.org/pep-0008/)

Install pre-commit before starting to contribute to the project as follows:
```
pre-commit install
```
