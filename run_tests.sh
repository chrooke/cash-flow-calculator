#!/bin/bash

flake8 --exclude=venv* --statistics
pytest -v --cov=transaction
pytest -v --cov=transaction-store
pytest -v --cov=cash-flow
