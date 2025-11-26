# Nginx IP Whitelist Setup

This configuration places Nginx in front of both the backend (FastAPI on port 8001) and the frontend (React on port 3000) and enforces the whitelist **before** any request reaches the applications.

## How it works
- Allowed IPs: `217.131.25.91`, `127.0.0.1`, and `::1`.
- Any other IP immediately receives a **403** response rendered with the React `/access-denied` page.
- `/api/*` routes proxy to the backend; every other path proxies to the frontend (including `/login`).
- Caddy is no longer needed; disable or remove it so Nginx is the only reverse proxy.

## Deploying
1. Copy `diogenes.conf` to your Nginx configuration (e.g., `/etc/nginx/sites-available/diogenes.conf`).
2. Enable the site and reload Nginx:
   ```bash
   sudo ln -sf /etc/nginx/sites-available/diogenes.conf /etc/nginx/sites-enabled/diogenes.conf
   sudo nginx -t
   sudo systemctl reload nginx
   ```
3. Keep `ENABLE_BACKEND_IP_CHECK=true` in `backend/.env` for defense-in-depth, but Nginx performs the first-line block.
