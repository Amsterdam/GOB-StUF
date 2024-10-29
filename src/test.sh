#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

echo() {
  builtin echo -e "$@"
}


echo "Running unit tests"
coverage run --source=gobstuf --data-file=/tmp/.coveragerc -m pytest tests/

echo "\nCoverage report"
coverage report --data-file=/tmp/.coveragerc --show-missing --fail-under=100

echo "\nRunning style checks"
flake8 gobstuf

echo "\nChecks complete"
