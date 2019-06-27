#!/usr/bin/env bash

set -e

python -m mkdocs build

cp ./docs/index.md ./README.md