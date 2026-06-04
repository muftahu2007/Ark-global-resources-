#!/bin/bash
# Start the Django-Q background worker in the background
python manage.py qcluster &

# Start the main web server in the foreground
gunicorn global_ark.wsgi --log-file -
