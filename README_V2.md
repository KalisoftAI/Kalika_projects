# Kalika India E-Commerce Platform Deployment Guide
**This document provides a comprehensive guide for deploying the Kalika India project, which consists of a Django e-commerce frontend and a FastAPI admin dashboard, on an Ubuntu-based EC2 instance.**

## Project Stack
Backend: Django & FastAPI

Web Server / Reverse Proxy: Nginx

Application Servers: Gunicorn (for Django) & Uvicorn (for FastAPI)

Database: PostgreSQL

-------

## Deployment Steps
Follow these steps in order to deploy the application from the server's command line.

--------

# Kalika Project Django Deployment Guide

This guide provides step-by-step instructions for deploying and updating the Kalika Django project.

## 1. Update Codebase

Pull the latest changes from the repository.

```bash
git pull origin Kalika_project_Django
```

---

## 2. Update settings.py

Open `settings.py` and add your domain names to the `ALLOWED_HOSTS` list.

```python
# settings.py

# Before
# ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# After
ALLOWED_HOSTS = ['[www.kalikaindia.com](https://www.kalikaindia.com)', 'kalikaindia.com', 'localhost', '127.0.0.1']
```

---

## 3. Use a Virtual Environment (Best Practice)

Activate your Python virtual environment. On Windows/Linux, the command is typically:

```bash
source env/bin/activate
```

---

## 4. Install Dependencies

Install all required packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

---

## 5. Update Database

These steps will recreate the `products` table in your PostgreSQL database.

First, switch to the `postgres` user and connect to the database:

```bash
sudo -i -u postgres
psql
\c ecom_prod_catalog
```

Next, drop the existing `products` table. **Warning**: This will delete all data in the table.

```sql
DROP TABLE products CASCADE;
```

Finally, exit PostgreSQL and the `postgres` user session.

```bash
exit
exit
```

---

## 6. Prepare Database with Script

You'll need to run a Python script to populate the new database table.

First, edit `dbtest2.py` to ensure the path to `filtered-products-new.xlsx` is correct.

Then, run the script:

```bash
python dbtest2.py
```

---

## 7. Create uvicorn.service File

Create a systemd service file to manage the Uvicorn server, which runs your ASGI application.

```bash
sudo nano /etc/systemd/system/uvicorn.service
```

Add the following configuration. Make sure to verify that the paths match your server's setup.

```ini
[Unit]
Description=Uvicorn instance to serve the ASGI application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/Kalika_projects/ecommerce_project/ecommerce
ExecStart=/home/ubuntu/Kalika_projects/ecommerce_project/ecommerce/env/bin/uvicorn --app-dir /home/ubuntu/Kalika_projects/ecommerce_project/ecommerce ecommerce.asgi:application --host 127.0.0.1 --port 8001

[Install]
WantedBy=multi-user.target
```

Reload the systemd daemon, restart the Uvicorn service, and check its status.

```bash
sudo systemctl daemon-reload
sudo systemctl restart uvicorn.service
sudo systemctl status uvicorn.service
```

---

## 8. Configure Nginx

Create or edit your Nginx site configuration file to proxy requests to your application servers.

```bash
sudo nano /etc/nginx/sites-available/kalikaproject
```

Add the following server block configuration. This setup handles redirects from HTTP to HTTPS, serves static and media files, and proxies requests to Gunicorn and Uvicorn.

```nginx
upstream app_server {
    server unix:/home/ubuntu/Kalika_projects/gunicorn.sock fail_timeout=0;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name kalikaindia.com [www.kalikaindia.com](https://www.kalikaindia.com);
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name kalikaindia.com [www.kalikaindia.com](https://www.kalikaindia.com);

    # SSL Certificate Paths
    ssl_certificate /etc/nginx/ssl/kalikaindia_com.crt;
    ssl_certificate_key /etc/nginx/ssl/kalikaindia_com.key;

    # SSL Security Settings
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Static and Media files
    location /static/ {
        alias /home/ubuntu/Kalika_projects/ecommerce_project/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/Kalika_projects/ecommerce_project/mediafiles/;
    }

    # Proxy to Uvicorn for Django Admin
    location /admin/ {
        proxy_pass [http://127.0.0.1:8001](http://127.0.0.1:8001);
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy to Gunicorn for the main app
    location / {
        proxy_pass http://app_server;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Test the Nginx configuration for syntax errors and restart the service.

```bash
sudo nginx -t
sudo systemctl restart nginx
```

Check the Nginx logs for any issues.

```bash
sudo tail -n 50 /var/log/nginx/access.log
```

---

## 9. Create gunicorn.service File

Create a systemd service file to manage the Gunicorn server, which runs your WSGI application.

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add the following configuration. Again, ensure all paths are correct for your environment.

```ini
[Unit]
Description=gunicorn daemon for ecommerce project
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Kalika_projects/ecommerce_project/ecommerce
ExecStart=/home/ubuntu/Kalika_projects/ecommerce_project/ecommerce/env/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/ubuntu/Kalika_projects/gunicorn.sock \
    ecommerce.wsgi:application

[Install]
WantedBy=multi-user.target
```

Restart Gunicorn and check its status.

```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn.service
```

---

## 10. Restart All Services After Changes

After making any changes to the service files or configuration, it's a good practice to restart all related services to ensure they are applied correctly.

```bash
sudo systemctl daemon-reload
sudo systemctl restart uvicorn
sudo systemctl restart nginx
sudo systemctl restart gunicorn


