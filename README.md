# 🛒 E-commerce PunchOut Catalog (Django)

A Django-based PunchOut Catalog system with PostgreSQL integration. This project enables suppliers to receive and process PunchOut orders using cXML data, ideal for enterprise e-procurement platforms.

---

## 🚀 Features

- Django-based backend  
- PostgreSQL as the production database  
- PunchOut order capture and storage  
- Session-based cXML order tracking  
- Collectstatic for deployment readiness  

---

## 📦 Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ecom-punchout-catalog.git
cd ecom-punchout-catalog
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### Django Commands

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

### 🗄 PostgreSQL Setup

```bash
Download PostgreSQL:
 https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
```

### Postgres Database Configuration

```bash
-- Create Database and User
CREATE DATABASE ecom_prod_catalog;
CREATE USER vikas WITH PASSWORD 'kalika1667';

-- Grant Privileges
GRANT ALL PRIVILEGES ON DATABASE ecom_prod_catalog TO vikas;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vikas;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO vikas;

-- Create PunchOut Orders Table
CREATE TABLE punchout_orders (
    id BIGSERIAL PRIMARY KEY,
    session_key VARCHAR(40) NOT NULL,
    cxml_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    supplier_id VARCHAR(255),
    punchout_request_url VARCHAR(500),
    punchout_response_url VARCHAR(500),
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR'
);

-- Grant Table Access
GRANT ALL PRIVILEGES ON TABLE punchout_orders TO vikas;
```

### Product file data store to Database table 
#### first go to dbtest2 file and change the csv file path in that code with you actual csv path
  file name: kalika_catalog_products_s31.csv
```bash
  python dbtest2.py
```


### **NOTE : - Check environment file (.env) is in .gitignore file before push any code **

# Deploying a Django Project on AWS EC2
This guide provides a clear, step-by-step process for deploying a Django project on an AWS EC2 instance with PostgreSQL, Gunicorn, and Nginx, including SSL configuration. It is designed for developers who want a reliable, production-ready deployment workflow.

---

# Prerequisites
AWS account with EC2 access

SSH key pair (.pem file)

GitHub repository for your Django project

Domain name (for SSL)

Basic knowledge of Linux command line

# 1. Launch EC2 Instance and Connect via SSH

Launch an Ubuntu EC2 instance from the AWS Console.

Open the EC2 dashboard, select your instance, and click Connect.

Use the SSH client command provided, for example:

bash
- ssh -i "yt-video.pem" ubuntu@ec2-52-90-110-55.compute-1.amazonaws.com

# 2. Fixing PEM File Permissions (if needed)
If you encounter public key permission issues on Windows, run these commands in PowerShell as Administrator:

powershell
- icacls.exe kalika_ecom.pem /reset
- icacls.exe kalika_ecom.pem /grant:r "$($env:username):(R)"
- icacls.exe kalika_ecom.pem /inheritance:r

# 3. Install and Configure PostgreSQL
Update packages and install PostgreSQL:

bash
- sudo apt update
- sudo apt install -y curl ca-certificates gnupg
- curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | sudo tee /usr/share/keyrings/postgresql-key.gpg >/dev/null
- echo "deb [signed-by=/usr/share/keyrings/postgresql-key.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
- sudo apt update
- sudo apt install -y postgresql-17 postgresql-contrib-17
- sudo systemctl status postgresql@17-main
- psql --version

Switch to the postgres user and configure the database:

bash
-sudo -i -u postgres
-psql

In the psql shell:

sql
-\password postgres -- Set password to kalika1667
- CREATE DATABASE ecom_prod_catalog;

- CREATE USER vikas WITH PASSWORD 'kalika1667';
- GRANT CONNECT ON DATABASE ecom_prod_catalog TO vikas;
- \c ecom_prod_catalog

- CREATE TABLE punchout_orders (
    id BIGSERIAL PRIMARY KEY,
    session_key VARCHAR(40) NOT NULL,
    cxml_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    supplier_id VARCHAR(255),
    punchout_request_url VARCHAR(500),
    punchout_response_url VARCHAR(500),
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR'
);

- GRANT ALL PRIVILEGES ON TABLE punchout_orders TO vikas;
- \q
- exit
- Grant additional privileges:

sql
- GRANT USAGE, CREATE ON SCHEMA public TO vikas;
- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vikas;
- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vikas;
- ALTER DEFAULT PRIVILEGES IN SCHEMA public FOR ROLE vikas GRANT ALL PRIVILEGES ON TABLES TO vikas;
- ALTER DEFAULT PRIVILEGES IN SCHEMA public FOR ROLE vikas GRANT ALL PRIVILEGES ON SEQUENCES TO vikas;


# 4. Clone the Project Repository
bash
- git clone --branch Kalika_project_Django https://github.com/KalisoftAI/Kalika_projects.git
cd Kalika_projects/

# 5. Install Python and Dependencies
bash
- sudo apt update && sudo apt upgrade -y
- python3 --version

# If needed, pull the latest code:

bash
- git pull origin Kalika_project_Django

# 6. Set Up Virtual Environment
Install pip and venv:

bash
- sudo apt install python3-pip python3.12-venv -y
- python3 -m venv env
- source env/bin/activate

# 7. Install Project Requirements
Edit or create requirements.txt and add your dependencies:

text
Django==4.2.7
python-dotenv==1.0.1
django-crispy-forms==2.4
crispy-bootstrap4==2025.6
boto3==1.38.5
psycopg2-binary==2.9.10
lxml==5.3.0
xmltodict==0.14.2
Install requirements:

bash
- pip install -r requirements.txt

# 8. Database Setup and Testing
Edit and run your database test script as needed:

bash
- sudo nano dbtest2.py
- python dbtest2.py

# 9. Run the Django Application
Navigate to your Django project directory and start the development server:

bash
- cd ecommerce_project/ecommerce
- python manage.py runserver

# 10. SSL Certificate Setup
Create the SSL directory:

bash
- sudo mkdir -p /etc/nginx/ssl

# From your local machine, copy the certificate and key files to the EC2 instance:

powershell
- scp -i C:\kalika-secrets\kalika-ecommerce.pem C:\nginx\ssl\CER_CRT_Files\kalikaindia_com.crt ubuntu@44.211.220.119:~/
- scp -i C:\kalika-secrets\kalika-ecommerce.pem C:\nginx\ssl\kalikaindia_com.key ubuntu@44.211.220.119:~/

Move and set permissions:

bash
- sudo mv kalikaindia_com.crt /etc/nginx/ssl/
- sudo mv kalikaindia_com.key /etc/nginx/ssl/
- sudo chown -R root:root /etc/nginx/ssl
- sudo chmod 600 /etc/nginx/ssl/kalikaindia_com.key
- sudo chmod 644 /etc/nginx/ssl/kalikaindia_com.crt

# 11. Install and Configure Gunicorn

Install Gunicorn:

bash
- pip install gunicorn
- Collect static files and apply migrations:

bash
- python manage.py collectstatic
- python manage.py migrate

Create and edit the Gunicorn service file:

bash
- sudo nano /etc/systemd/system/gunicorn.service

Paste the following (update paths as needed):

text
[Unit]
Description=gunicorn daemon
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/your-project-directory
ExecStart=/home/ubuntu/your-project-directory/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/your-project-directory/your_project.sock your_project.wsgi:application
[Install]
WantedBy=multi-user.target
Enable and start Gunicorn:

bash
- sudo systemctl start gunicorn
- sudo systemctl enable gunicorn

# 12. Install and Configure Nginx

Install Nginx:

bash
- sudo apt update && sudo apt upgrade -y
- sudo apt install nginx -y

Edit the Nginx config:

bash
- sudo nano /etc/nginx/sites-available/default

Example configuration:

text
server {
    listen 443 ssl http2;
    server_name kalikaindia.com www.kalikaindia.com;

    ssl_certificate /etc/nginx/ssl/kalikaindia_com.crt;
    ssl_certificate_key /etc/nginx/ssl/kalikaindia_com.key;

    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location /static/ {
        alias /home/ubuntu/Kalika_projects/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/Kalika_projects/mediafiles/;
    }

    location / {
        proxy_pass http://app_server;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

Test and restart Nginx:

bash
- sudo nginx -t
- sudo systemctl restart nginx

# 13. Final Steps and Verification
Ensure all services are running: PostgreSQL, Gunicorn, and Nginx.

-- Visit your domain (e.g., https://kalikaindia.com) to verify the deployment.

Check logs for troubleshooting if needed.

Congratulations! Your Django project is now deployed on AWS EC2 with a production-ready stack.
