# Prod Deployment

## Requirements

- The Scraper needs to run continuously for ~30 minutes and be retriggered periodically
- The Api needs to listen to http
- Persistent storage for the scraped files
- Free services only

#### Negative Scope

- Scalability is not needed for now

## Solution

#### 1. [Google Cloud](https://cloud.google.com) VM instance

Works for the long-running Scraper, Api and permanent storage.
Has free instance type: e2-micro.

#### 2. Uvicorn

ASGI web server that can run our API which is based on FastAPI, a web framework.

#### 3. Nginx

Reverse proxy to handle HTTPS.

#### 4. [DuckDNS](https://www.duckdns.org/)

A free subdomain DNS.
We're currently using:

- monitor-de-acoes.duckdns.org
- 34.42.227.37 (stable public ip of the VM in GCP)

#### 5. Certbot

Free certificate authority

## Step-by-step

#### 1. Connect to the VM

```
gcloud compute ssh vitobasso@scraper --zone "us-central1-f" --project "api-project-**********"
```

#### 2. Install this project

Refer to [README.md](../README.md), "Local Setup"

#### 3. Install Nginx and Certbot

```bash
sudo apt install nginx certbot python3-certbot-nginx
```

#### 4. Get a signed certificate with CertBot

```bash
sudo certbot certonly --nginx -d monitor-de-acoes.duckdns.org
# Certificate is saved at: /etc/letsencrypt/live/monitor-de-acoes.duckdns.org/fullchain.pem
# Key is saved at:         /etc/letsencrypt/live/monitor-de-acoes.duckdns.org/privkey.pem
```

We add `certonly` here to prevent certbot automatically installing the cert in Nginx default conf.

#### 5. Configure Nginx

Configure Nginx to listen on our domain name and use the certificate.

```bash
sudo tee /etc/nginx/sites-enabled/monitor-de-acoes.duckdns.org.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name monitor-de-acoes.duckdns.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name monitor-de-acoes.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/monitor-de-acoes.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitor-de-acoes.duckdns.org/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;  # your uvicorn app port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
```

#### 6. Restart Nginx and run Uvicorn

```
sudo systemctl restart nginx
uvicorn src.api.api:app --host 127.0.0.1 --port 8000
```

#### 7. Set Uvicorn to automatically launch on VM restarts

Add Uvicorn to systemd. 
We can set `--host 127.0.0.1` because Uvicorn will only be accessed indirectly through Nginx, which is running on localhost.

```bash
sudo tee /etc/systemd/system/uvicorn.service > /dev/null<<'EOF'
[Unit]
Description=Uvicorn server
After=network.target

[Service]
User=vitobasso
WorkingDirectory=/home/vitobasso/stocks-scraper
ExecStart=/home/vitobasso/stocks-scraper/.venv/bin/uvicorn src.api.api:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable uvicorn
sudo systemctl start uvicorn
```

#### 8. Schedule the Scraper periodically

[//]: # (TODO)

## Research

Here is some information about the choices made and discarded alternatives.

### Cloud services

#### [Google Cloud](https://cloud.google.com) VM instance

A non-managed VM seems to be the easiest way to get a long-running async job/script, Api and storage for free.
The VM instance type available in "always free" is e2-micro.
Other solutions like Cloud Run, a managed service, seemed to require Block Storage, which is not available in GCP "
always free".
Firestore, a no-SQL document storage, or SQL would options but require re-implementing the file logic.
I believe the downside of VM instance would be bad scalability, but we don't have that requirement.

#### Alternatives

- https://dashboard.render.com/cron/new
- https://replit.com/ # free trial
- https://railway.com/ # no longer has free tier
- https://vercel.com/ # node.js only. has a beta python managed service but can't do long-running job with starage.

### Domain name

We need a domain name to get a certificate for HTTPS.
Without HTTPS the browser would fail with "Blocked: mixed-content" because
the [Frontent](https://github.com/vitobasso/stocks-dashboard-web) uses HTTPS.

- https://www.duckdns.org/ # free subdomain
- https://freedns.afraid.org/ # get subdomains from random people's domains
- https://cloud.google.com/domains/docs/register-domain # not free