#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python seed.py
gunicorn helpdesk.wsgi --log-file -
