#!/bin/bash

flake8 --exclude=venv* --statistics
pytest -v --cov=transaction --cov=transaction_store

