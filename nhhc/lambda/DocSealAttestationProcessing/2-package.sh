#!/usr/bin/env bash
mkdir python
cp -r .lambda-venv/lib python/
zip -r layer_content.zip python
