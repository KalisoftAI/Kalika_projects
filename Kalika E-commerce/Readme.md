# README: Website Deployment Guide

This document provides a comprehensive guide for deploying a Flask-based website on an EC2 instance, including configurations for Nginx and SSL certificates.

---

## Prerequisites

1. **Access Credentials**: Ensure you have the `.pem` file (e.g., `mumbai_ecomm_webserver.pem`) for SSH access.
2. **Software Requirements**:
   - Python 3.x
   - pip
   - Git
   - Nginx
   - Flask and required Python libraries (specified in `requirements.txt`).
3. **Domain Configuration**:
   - Ensure the domain (e.g., `kalisoft.in`) points to the EC2 instance IP (e.g., `35.154.229.59`).

---

## Deployment Steps

### 1. SSH into the EC2 Instance
```bash
ssh -i "mumbai_ecomm_webserver.pem" ubuntu@ec2-35-154-229-59.ap-south-1.compute.amazonaws.com
```

### 2. Update and Install Required Software
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3-pip python3-venv nginx -y
```

### 3. Clone the Git Repository
Clone the repository containing the project:
```bash
git clone -b <branch_name> https://<username>:<personal_access_token>@github.com/<username>/<repository>.git
```

### 4. Set Up the Virtual Environment
Navigate to the project directory and set up the virtual environment:
```bash
cd <repository_name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure and Start Nginx
Edit the Nginx configuration for the domain:
```bash
sudo nano /etc/nginx/sites-available/default
```
Add the following configuration:
```nginx
server {
    listen 80;
    server_name kalisoft.in www.kalisoft.in;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Test and reload Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Configure SSL with Self-Signed Certificate
Generate and configure a self-signed SSL certificate:
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
-keyout /etc/ssl/certs/private.pem \
-out /etc/ssl/certs/kali_certificate.crt
```
Update the Nginx configuration for SSL:
```nginx
server {
    listen 443 ssl;
    server_name kalisoft.in www.kalisoft.in;

    ssl_certificate /etc/ssl/certs/kali_certificate.crt;
    ssl_certificate_key /etc/ssl/certs/private.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Reload Nginx:
```bash
sudo systemctl reload nginx
```

### 7. Start the Flask Application
Run the Flask app using Gunicorn:
```bash
sudo apt install gunicorn
sudo gunicorn --bind 0.0.0.0:5000 app:app
```

To configure Gunicorn as a service:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```
Add the following:
```ini
[Unit]
Description=gunicorn daemon for Flask app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/<repository_name>
Environment="PATH=/home/ubuntu/<repository_name>/venv/bin"
ExecStart=/home/ubuntu/<repository_name>/venv/bin/gunicorn --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```
Start and enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

---

## Troubleshooting

1. **Nginx Errors**:
   - Check logs: `sudo tail -f /var/log/nginx/error.log`

2. **SSL Issues**:
   - Verify SSL file permissions:
     ```bash
     sudo chmod 600 /etc/ssl/certs/private.pem
     sudo chmod 644 /etc/ssl/certs/kali_certificate.crt
     ```

3. **Gunicorn Service Errors**:
   - Check service status:
     ```bash
     sudo systemctl status gunicorn
     ```

---

## Notes

- For secure deployment, consider using Let's Encrypt for free SSL certificates.
- Ensure the security group for your EC2 instance allows traffic on ports 80 and 443.

---

This guide covers the deployment of a Flask app with Nginx and self-signed SSL on an EC2 instance. Customize the steps based on your project requirements.
