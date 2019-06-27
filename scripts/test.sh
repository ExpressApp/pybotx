#!/usr/bin/env bash

set -e
set -x

pytest --cov=botx --cov-report=term-missing ${@}
coverage report --show-missing --fail-under=100

bash ./scripts/lint.sh