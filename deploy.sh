#!/bin/bash
set -e

# === Configuration ===
PROJECT_DIR=/opt/dance_portal_starter
VENV_DIR=$PROJECT_DIR/venv
SERVICE_NAME=gunicorn
NGINX_CONF_NAME=danceportal.conf
NGINX_CONF_PATH=/etc/nginx/sites-available/$NGINX_CONF_NAME

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

# === Nginx configuration (safe mode) ===
echo "🔹 Verifying Nginx configuration..."
if [ -f "$NGINX_CONF_PATH" ]; then
    echo "✅ Nginx config already exists — skipping overwrite to preserve SSL settings."
else
    echo "⚠️  Nginx config missing — copying fresh version from project."
    sudo cp $PROJECT_DIR/$NGINX_CONF_NAME /etc/nginx/sites-available/$NGINX_CONF_NAME
    sudo ln -sf /etc/nginx/sites-available/$NGINX_CONF_NAME /etc/nginx/sites-enabled/$NGINX_CONF_NAME
fi

sudo nginx -t

# === Restart services ===
echo "🔹 Restarting Gunicorn and Nginx..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl restart nginx

# === Verify SSL certificate ===
echo "🔍 Checking active SSL certificate..."
CERT_SUBJECT=$(echo | openssl s_client -connect 5678danceportal.com:443 -servername 5678danceportal.com 2>/dev/null | grep "subject=" || true)

if echo "$CERT_SUBJECT" | grep -q "localhost"; then
    echo "⚠️  Warning: SSL appears self-signed (CN=localhost)."
    echo "    Please verify /etc/nginx/sites-available/$NGINX_CONF_NAME points to:"
    echo "    /etc/letsencrypt/live/5678danceportal.com-0001/fullchain.pem"
else
    echo "✅ SSL certificate looks correct:"
    echo "    $CERT_SUBJECT"
fi

echo "✅ Deployment complete!"
echo "🌐 Visit: https://5678danceportal.com"
