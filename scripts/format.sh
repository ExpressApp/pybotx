#!/usr/bin/env bash

set -e

autoflake --recursive --remove-all-unused-imports --remove-unused-variables --in-place botx tests --exclude=__init__.py
black botx tests
isort --recursive --multi-line=3 --trailing-comma --line-width 88 --force-grid-wrap=0 --combine-as botx tests
