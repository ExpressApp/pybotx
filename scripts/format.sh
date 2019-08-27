#!/usr/bin/env bash

set -e

# Sort imports one per line, so autoflake can remove unused imports
isort --recursive  --force-single-line-imports botx tests

autoflake --recursive --remove-all-unused-imports --remove-unused-variables --in-place botx tests --exclude=__init__.py
black botx tests
isort --recursive --multi-line=3 --trailing-comma --line-width 88 --force-grid-wrap=0 --combine-as botx tests
