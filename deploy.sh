#!/bin/bash
set -e

PROJECT_DIR=/home/django/dance_portal_starter
VENV_DIR=$PROJECT_DIR/venv

cd $PROJECT_DIR

echo "🔹 Updating code from Git..."
git pull origin main

echo "🔹 Activating virtual environment..."
source $VENV_DIR/bin/activate

echo "🔹 Installing dependencies..."
pip install -r requirements.txt

echo "🔹 Running migrations..."
python manage.py migrate --noinput

echo "🔹 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔹 Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Deployment complete!"
