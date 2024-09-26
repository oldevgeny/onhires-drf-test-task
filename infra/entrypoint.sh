#!/bin/bash

# Apply database migrations
poetry run python onhires_drf_test_task/manage.py migrate

# Collect static files (skipped for now)
# poetry run python manage.py collectstatic --noinput

# Start the Django server
exec "$@"
