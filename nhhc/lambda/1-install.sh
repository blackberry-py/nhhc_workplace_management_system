#!/usr/bin/env bash
python3.11 -m venv .lambda-venv
source .lambda-venv/bin/activate
pip install -r requirements.txt
