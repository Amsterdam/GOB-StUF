#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

# Clear any cached results
#find . -name "*.pyc" -exec rm -f {} \;

#export GOB_RUN_MODE=TEST
export COVERAGE_FILE=/tmp/.coverage

echo "Running tests"
coverage run --source=./gobstuf -m pytest tests/

echo "Running coverage report"
coverage report --show-missing --fail-under=100

echo "Running style checks"
flake8
