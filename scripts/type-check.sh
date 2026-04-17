#!/usr/bin/env bash

set -ex

uv run ruff check --select ANN ./src
