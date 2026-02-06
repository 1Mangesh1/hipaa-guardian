---
name: nginx
description: Nginx web server configuration for reverse proxy, SSL/TLS, load balancing, and static hosting. Use when user asks to "configure nginx", "set up reverse proxy", "add SSL", "nginx location block", "load balancer config", "serve static files", or any web server configuration tasks.
---

# Nginx

Web server configuration, reverse proxy, and SSL/TLS.

## Basic Server Block

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name example.com www.example.com;

    root /var/www/myapp;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

## Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Multiple backends
upstream backend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

server {
    listen 80;
    server_name app.example.com;

    location / {
        proxy_pass http://backend;
    }
}
```

## SSL/TLS (HTTPS)

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # SSL hardening
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

```bash
# Get SSL cert with Certbot
sudo certbot --nginx -d example.com -d www.example.com

# Renew certs
sudo certbot renew --dry-run
```

## Location Blocks

```nginx
# Exact match
location = /health {
    return 200 "OK";
    add_header Content-Type text/plain;
}

# Prefix match
location /api/ {
    proxy_pass http://localhost:3000/;
}

# Regex match (case-sensitive)
location ~ \.php$ {
    fastcgi_pass unix:/var/run/php-fpm.sock;
}

# Regex match (case-insensitive)
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Priority order:
# 1. = exact
# 2. ^~ prefix (stops regex search)
# 3. ~ or ~* regex
# 4. prefix (longest match)
```

## Caching & Performance

```nginx
# Static file caching
location /static/ {
    alias /var/www/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

# Gzip compression
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://localhost:3000;
    }
}

# Connection limiting
limit_conn_zone $binary_remote_addr zone=addr:10m;

location /download/ {
    limit_conn addr 5;
}
```

## SPA (Single Page Application)

```nginx
server {
    listen 80;
    server_name app.example.com;

    root /var/www/app/dist;
    index index.html;

    # All routes fall back to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Don't cache index.html
    location = /index.html {
        add_header Cache-Control "no-cache";
    }
}
```

## Common Commands

```bash
# Test configuration
sudo nginx -t

# Reload (no downtime)
sudo nginx -s reload

# Start/stop
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx

# View logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Enable site
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t && sudo nginx -s reload
```

## Security Headers

```nginx
# Add to server block
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

## Reference

For HTTPS setup and security hardening: `references/ssl.md`
