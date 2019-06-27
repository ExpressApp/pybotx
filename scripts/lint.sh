#!/usr/bin/env bash

set -e
set -x


flake8 botx
mypy --disallow-untyped-defs --follow-imports=skip botx

black --check botx tests
isort --recursive --check-only --multi-line=3 --trailing-comma --line-width 88 --force-grid-wrap=0 --combine-as botx tests
