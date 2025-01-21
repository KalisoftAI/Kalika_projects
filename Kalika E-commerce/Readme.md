# Website Deployment Guide

This document outlines the steps for deploying the website on an EC2 instance using the provided deployment details.

---

## Prerequisites

1. **Access Credentials**: Ensure you have the `.pem` key file (`mumbai_ecomm_webserver.pem`) for SSH access.
2. **Tools Installed**:
   - SSH client
   - Python and virtual environment packages
   - Nginx installed and configured on the EC2 instance

---

## Deployment Steps

### Step 1: SSH into the EC2 Instance
Use the following command to connect to your EC2 instance:

```bash
ssh -i "mumbai_ecomm_webserver.pem" ubuntu@ec2-35-154-229-59.ap-south-1.compute.amazonaws.com
```

### Step 2: Activate the Virtual Environment
Activate the virtual environment for the project:

```bash
source venv/bin/activate
```

### Step 3: Restart or Start Nginx
To ensure Nginx is running, restart the service:

```bash
sudo /etc/init.d/nginx restart
```

If Nginx is not running, start it manually:

```bash
sudo /etc/init.d/nginx start
```

### Step 4: Configure Firewall Rules
Allow HTTP traffic on port 80 by adding the following iptables rule:

```bash
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
```

---

## Punchout Process

### Code Configuration
Ensure that the redirect URL is updated in the code for the Punchout process. The redirect URL provided should match the one updated in SAP Ariba for proper buyer redirection.

- Example configuration:
  - **Redirect URL**: Ensure the URL specified in the code aligns with the buyer's SAP Ariba configuration.

---

## Troubleshooting

1. **Nginx Issues**:
   - Check Nginx logs for any errors:
     ```bash
     sudo tail -f /var/log/nginx/error.log
     ```

2. **SSH Connection Errors**:
   - Verify that the `.pem` file has the correct permissions:
     ```bash
     chmod 400 mumbai_ecomm_webserver.pem
     ```

3. **Virtual Environment Issues**:
   - Ensure the `venv` directory exists and is properly set up. If not, create and set up the virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

---

## Notes

- Ensure the EC2 instance's security group allows inbound traffic on port 80.
- Regularly update the `nginx.conf` file to reflect any changes in server configurations.

---

This document serves as a quick reference for deploying and managing the website. Ensure all configurations are validated before deploying to production.
