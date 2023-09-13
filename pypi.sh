#!/usr/bin/env bash

# to be run on a master branch clone

# requires:
# python -m pip install --upgrade build
# python -m pip install --upgrade twine

rm -rf dist
python -m build
twine upload dist/*

rm -rf dist
