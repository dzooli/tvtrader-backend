#!/bin/bash

source venv/Scripts/activate
python -m src.starter
# alternative: using Sanic CLI
#sanic -d -p 8089 --fast src.server:app
