#!/bin/bash

# Install miniogre wheel

## uninstall older versions
rm -r dist
pipx uninstall miniogre

## Build wheel and install miniogre
poetry build && pipx install dist/*.whl
