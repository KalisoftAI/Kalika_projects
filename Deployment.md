
### Step 1: Launch an EC2 Instance

1. Log into AWS Management Console.
2. Navigate to EC2 Dashboard:

3. Search for EC2 and click on Instances.

4. Launch a New Instance:

    1. Click on Launch Instance.
    2.  Choose Ubuntu Server 22.04 LTS as the AMI.
    3. Select t2.micro as the instance type.
    4. Create a new key pair (e.g., flask-todos) and download it.

5. Configure Security Group:
    Allow SSH (port 22), HTTP (port 80), and HTTPS (port 443) traffic.

    Launch the Instance.

### Step 2: Connect to Your EC2 Instance

1. Get the Public IPv4 DNS from the EC2 dashboard.

2. Change Permissions for Key Pair:

    bash

    <code>chmod 400 path_to_key_pair/flask-todos.pem</code>

3. SSH into the Instance:

    bash

    <code>ssh -i path_to_key_pair/flask-todos.pem ubuntu@your-instance-public-ipv4-dns-address</code>


### Step 3: Set Up PostgreSQL
1. Install PostgreSQL:
    1. <code>sudo apt update</code>

    2. sudo apt install postgresql postgresql-contrib


2. Create a Database and User:

bash
sudo -u postgres psql

CREATE DATABASE flaskdb;

CREATE USER flaskuser WITH PASSWORD 'yourpassword';

ALTER ROLE flaskuser SET client_encoding TO 'utf8';

ALTER ROLE flaskuser SET default_transaction_isolation TO 'read committed';

ALTER ROLE flaskuser SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE flaskdb TO flaskuser;
\q



### Step 4: Install Flask and Dependencies

1. Install Required Packages:
bash
<code>sudo apt install python3-pip python3-dev nginx curl</code>

2. Set Up a Virtual Environment:
    1. sudo apt install python3-venv

    2. mkdir ~/flask-todos && cd ~/flask-todos

    3. python3 -m venv venv

    4. source venv/bin/activate

3. Install Flask and Other Dependencies:

<code>pip install -r requirements.txt</code>

### Step 5: Set Up Gunicorn

1. Install Gunicorn:

bash

<code>pip install gunicorn</code>

Test Gunicorn with Your Flask App (replace app with your Flask app name):
bash
<code>gunicorn --bind 0.0.0.0:8000 app:app</code>


### Step 6: Configure Nginx
Create Nginx Configuration File:

bash
<code>sudo nano /etc/nginx/sites-available/flask-todos</code>

Add Configuration:
Replace server_name with your EC2 public DNS:

text
<code>
server {
    listen 80;
    server_name your_public_ip_or_domain;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
</code>

Enable the Configuration:

bash
<code>sudo ln -s /etc/nginx/sites-available/flask-todos /etc/nginx/sites-enabled</code>

Test Nginx Configuration:

bash
<code>sudo nginx -t</code>

Restart Nginx:

bash
<code>sudo systemctl restart nginx</code>

### Step 7: Finalize Deployment
Start Gunicorn as a Service (optional):
Create a service file for Gunicorn to manage it easily.

bash
<code>sudo nano /etc/systemd/system/gunicorn.service</code>

Add the following configuration (adjust paths accordingly):

text
[Unit]
Description=gunicorn daemon for Flask app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/flask-todos/
Environment="PATH=/home/ubuntu/flask-todos/venv/bin"
ExecStart=/home/ubuntu/flask-todos/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/flask-todos/flask-todos.sock app:app

[Install]
WantedBy=multi-user.target

Enable and Start Gunicorn Service:

sudo systemctl start gunicorn

sudo systemctl enable gunicorn

Your Flask application should now be accessible via your EC2 instance's public IP or domain name in a web browser!