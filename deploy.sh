#!/bin/bash
set -e

# === Configuration ===
PROJECT_DIR=/opt/dance_portal_starter
VENV_DIR=$PROJECT_DIR/venv
SERVICE_NAME=gunicorn
NGINX_CONF_NAME=danceportal

echo "🚀 Starting deployment for Dance Portal..."
cd $PROJECT_DIR

# === Git update ===
echo "🔹 Resetting code to latest from GitHub..."
git fetch origin main
git reset --hard origin/main

# === Virtual environment ===
echo "🔹 Activating virtual environment..."
source $VENV_DIR/bin/activate

# === Dependencies ===
echo "🔹 Installing/Updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# === Django operations ===
echo "🔹 Running migrations..."
python manage.py migrate --noinput

echo "🔹 Collecting static files..."
python manage.py collectstatic --noinput

# === Gunicorn service ===
echo "🔹 Updating Gunicorn systemd service..."
sudo cp $PROJECT_DIR/gunicorn.service /etc/systemd/system/$SERVICE_NAME.service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# === Nginx configuration ===
echo "🔹 Updating Nginx configuration..."
sudo cp $PROJECT_DIR/$NGINX_CONF_NAME /etc/nginx/sites-available/$NGINX_CONF_NAME
sudo ln -sf /etc/nginx/sites-available/$NGINX_CONF_NAME /etc/nginx/sites-enabled/$NGINX_CONF_NAME
sudo nginx -t

# === Restart services ===
echo "🔹 Restarting Gunicorn and Nginx..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🌐 Visit: http://91.98.154.49  or  https://5678danceportal.com"
