#!/usr/bin/env bash

set -e

# Sort imports one per line, so autoflake can remove unused imports
isort --recursive  --force-single-line-imports botx tests
bash ./scripts/format.sh