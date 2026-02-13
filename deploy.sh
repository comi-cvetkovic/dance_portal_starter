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

# Allow server-local .env to differ, but block deploy if any code/config files are dirty.
DIRTY_NON_ENV=$(git status --porcelain --untracked-files=normal | grep -vE '^(.. )?\.env$|^\?\? \.env$' || true)
if [ -n "$DIRTY_NON_ENV" ]; then
    echo "Uncommitted non-.env changes detected; aborting deploy."
    echo "$DIRTY_NON_ENV"
    echo "Commit/revert these files, or keep only .env as local server state."
    exit 1
fi

git pull --ff-only origin main

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
echo "INFO: Ensure /opt/dance_portal_starter/.env exists on the server (not in git)."

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
