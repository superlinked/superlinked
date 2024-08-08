# Contribute to Superlinked deployment aka Server

## TODO...

## Pre-commit installation and configuration

We are using [pre-commit](https://pre-commit.com/) to run linters and unit tests locally before each push.

In order to install `pre-commit` via pip or brew, please follow the instructions in the link above. (but really it's just a `brew install pre-commit`)

The base configuration is already provided in `.pre-commit-config.yaml`. Run `pre-commit install` to install pre-commit into your git hooks. pre-commit will now run before every push. Every time you clone a project using pre-commit, running `pre-commit install` should always be the first thing you do.

If you want to manually run all pre-commit hooks on a repository, run `pre-commit run --all-files`. To run individual hooks use `pre-commit run <hook_id>`.

The first time pre-commit runs on a file it will automatically download, install, and run the hook. Note that running a hook for the first time may be slow. For example: If the machine does not have node installed, pre-commit will download and build a copy of node.
