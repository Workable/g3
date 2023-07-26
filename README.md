# G
All-in-one CLI to commit your work to Github [[Docs](https://docs.google.com/presentation/d/1BZN4cfeGYR9U4UjXF6wH_-x9l8DwGOgJRZr7UDKXiMQ/)]

## Installation
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
