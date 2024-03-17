#!/bin/bash

source venv/Scripts/activate
sanic -p 8089 --workers 4 --factory src.server:create_app
