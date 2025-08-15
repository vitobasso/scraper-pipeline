# Scans

For a quick check:

* **Local scan**:

  ```bash
  sudo apt install lynis
  sudo lynis audit system
  ```
* **Network scan**:

  ```bash
  sudo apt install nmap
  nmap -sV -Pn your.server.ip
  ```
* **Web app scan**: use **OWASP ZAP** or **Nikto**.

  ```bash
  nikto -h http://your.server.ip
  ```

Best done from a separate machine so you see what’s exposed to the internet.


# Hardening

Here’s a short, practical hardening checklist for your GCP VM:

---

### 1. **SSL/TLS**

* Force modern protocols only:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
```

* Reload nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

* Optional: enable HSTS for HTTPS sites.

---

### 2. **Systemd service hardening (exposed services only)**

* Focus on: `ssh.service`, `nginx.service`, `uvicorn.service`.
* Add minimal hardening in `/etc/systemd/system/<service>.service.d/hardening.conf`:

```ini
[Service]
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=full
ProtectHome=read-only
ProtectKernelModules=yes
ProtectControlGroups=yes
ProtectKernelTunables=yes
```

* Reload and restart:

```bash
sudo systemctl daemon-reexec
sudo systemctl restart ssh nginx uvicorn
```

---

### 3. **SSH**

* Disable password auth:

```ini
PasswordAuthentication no
PermitRootLogin no
```

* Use key-based login only.

---

### 5. **Firewall / Network**

* Allow only necessary ports:

```bash
sudo ufw default deny incoming
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

* Consider limiting SSH to your IP.

---

### 6. **Updates**

* Enable unattended upgrades:

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

This fixes the **high-risk items** without breaking your VM or web stack.
