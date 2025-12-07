#!/bin/bash

set -e

echo "======================================="
echo "  CustomVPN Cloudflare Deployment"
echo "======================================="
echo ""

DOMAIN="shaunstudio.vip"
EMAIL="your@email.com"  # Change this to your email

# Check if running as root
if [ "$EUID" -ne 0 ]; then
   echo "Please run as root (use sudo)"
   exit 1
fi

echo "[1/7] Installing dependencies..."
apt-get update
apt-get install -y docker.io docker-compose certbot

echo "[2/7] Creating directories..."
mkdir -p docker/nginx/ssl/live/$DOMAIN
mkdir -p docker/nginx/html

echo "[3/7] Obtaining SSL certificate..."
echo "This will get SSL certificate for $DOMAIN"

# Stop any service using port 80
docker-compose -f docker-compose-cloudflare.yml down 2>/dev/null || true

# Get certificate
certbot certonly --standalone \
  -d $DOMAIN \
  --non-interactive \
  --agree-tos \
  --email $EMAIL \
  --preferred-challenges http

# Copy certificates to nginx directory
cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem docker/nginx/ssl/live/$DOMAIN/
cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem docker/nginx/ssl/live/$DOMAIN/
cp -L /etc/letsencrypt/live/$DOMAIN/chain.pem docker/nginx/ssl/live/$DOMAIN/
chmod 644 docker/nginx/ssl/live/$DOMAIN/*

echo "[4/7] Building Docker images..."
docker-compose -f docker-compose-cloudflare.yml build

echo "[5/7] Starting services..."
docker-compose -f docker-compose-cloudflare.yml up -d

echo "[6/7] Verifying services..."
sleep 5
docker-compose -f docker-compose-cloudflare.yml ps

echo ""
echo "[7/7] Checking service health..."
if docker exec nginx-proxy wget --spider -q http://localhost/; then
    echo "✓ Nginx: Running"
else
    echo "✗ Nginx: Failed"
fi

if docker exec xray-websocket nc -zv 127.0.0.1 10000 2>&1 | grep -q succeeded; then
    echo "✓ Xray WebSocket: Running"
else
    echo "✗ Xray WebSocket: Failed"
fi

if docker exec shadowsocks-fallback nc -zv 127.0.0.1 8388 2>&1 | grep -q succeeded; then
    echo "✓ Shadowsocks: Running"
else
    echo "✗ Shadowsocks: Failed"
fi

echo ""
echo "======================================="
echo "  Deployment Complete!"
echo "======================================="
echo ""
echo "Next Steps:"
echo "1. Add DNS A record in Cloudflare:"
echo "   Name: vpn"
echo "   Value: $(curl -s ifconfig.me)"
echo "   Proxy: ON (Orange cloud)"
echo ""
echo "2. Import this config to v2rayNG:"
echo ""
echo "vless://ab87d164-971c-44d8-8c34-b4e4ff9f2e71@shaunstudio.vip:443?encryption=none&security=tls&type=ws&host=shaunstudio.vip&path=%2Fvlessws&sni=shaunstudio.vip#CloudflareVPN"
echo ""
echo "3. Test website: https://shaunstudio.vip"
echo ""
echo "View logs: docker-compose -f docker-compose-cloudflare.yml logs -f"
echo "Check status: docker-compose -f docker-compose-cloudflare.yml ps"
echo ""
