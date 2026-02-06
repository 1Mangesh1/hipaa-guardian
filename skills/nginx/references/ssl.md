# Nginx SSL/TLS Reference

## Let's Encrypt Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx   # Debian/Ubuntu
sudo dnf install certbot python3-certbot-nginx    # RHEL/Fedora
brew install certbot                              # macOS

# Get certificate (auto-configures nginx)
sudo certbot --nginx -d example.com -d www.example.com

# Get certificate (manual, no nginx changes)
sudo certbot certonly --nginx -d example.com

# Standalone (no web server running)
sudo certbot certonly --standalone -d example.com

# Renewal
sudo certbot renew --dry-run    # Test
sudo certbot renew              # Actual renewal

# Auto-renewal cron (usually auto-configured)
# 0 0,12 * * * certbot renew --quiet
```

## Production SSL Config

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://example.com$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.example.com;
    return 301 https://example.com$request_uri;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    # Certificates
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Protocol versions
    ssl_protocols TLSv1.2 TLSv1.3;

    # Ciphers
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS (1 year)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;

    # DH parameters (generate: openssl dhparam -out /etc/ssl/dhparam.pem 2048)
    ssl_dhparam /etc/ssl/dhparam.pem;

    # Session cache
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

## Self-Signed Certificate (Development)

```bash
# Generate self-signed cert
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout /etc/ssl/private/selfsigned.key \
  -out /etc/ssl/certs/selfsigned.crt \
  -subj "/CN=localhost"
```

## Wildcard Certificate

```bash
# Requires DNS challenge
sudo certbot certonly --manual --preferred-challenges dns \
  -d "*.example.com" -d "example.com"

# Or with DNS plugin (e.g., Cloudflare)
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
  -d "*.example.com" -d "example.com"
```

## Test SSL Configuration

```bash
# Test locally
curl -vI https://example.com

# Check certificate details
openssl s_client -connect example.com:443 -servername example.com

# Check expiry
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates

# Online test: https://www.ssllabs.com/ssltest/
```
