#!/bin/bash

cd $1
rm -rf .env
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
