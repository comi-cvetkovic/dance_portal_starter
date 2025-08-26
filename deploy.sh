#!/bin/bash
set -e

PROJECT_DIR=/home/django/dance_portal_starter
VENV_DIR=$PROJECT_DIR/venv
SERVICE_NAME=gunicorn
NGINX_CONF_NAME=danceportal

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

echo "🔹 Updating Gunicorn systemd service..."
sudo cp $PROJECT_DIR/gunicorn.service /etc/systemd/system/$SERVICE_NAME.service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

echo "🔹 Updating Nginx config..."
sudo cp $PROJECT_DIR/$NGINX_CONF_NAME /etc/nginx/sites-available/$NGINX_CONF_NAME
sudo ln -sf /etc/nginx/sites-available/$NGINX_CONF_NAME /etc/nginx/sites-enabled/$NGINX_CONF_NAME
sudo nginx -t

echo "🔹 Restarting services..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl restart nginx

echo "✅ Deployment complete!"

