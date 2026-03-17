cd /home/debian/api/api 
source ./.venv/bin/activate
gunicorn --workers 4 -b 0.0.0.0:3232 'api_run:flask_api'
