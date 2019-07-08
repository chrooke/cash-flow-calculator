#!/bin/bash
flake8 --exclude=venv* --statistics
pytest -v --cov=cash_flow

