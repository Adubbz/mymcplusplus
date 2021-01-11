#!/bin/bash
cd "$(dirname "$0")"
set -xe
rm -rf dist
python setup.py sdist bdist_wheel
twine upload dist/*
