#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if needed
python create_superuser.py

# Use environment variable or default to 3 minutes timeout
TIMEOUT=${GUNICORN_TIMEOUT:-180}
# Configure Gunicorn with memory optimization settings
export GUNICORN_CMD_ARGS="--timeout $TIMEOUT --workers=2 --threads=2 --max-requests=500 --max-requests-jitter=50 --log-level=debug --preload" 