# How to Use CustomVPN

Your VPN is deployed and running on **Melbourne (Australia)** at `54.206.37.229`

## 📱 Quick Setup

### Method 1: Import via Share Links (Easiest)

Copy one of these links into your VPN client app:

**VLESS+REALITY (Recommended - Faster, More Secure):**
```
vless://ab87d164-971c-44d8-8c34-b4e4ff9f2e71@54.206.37.229:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.apple.com&fp=chrome&pbk=R8rHTLBhepmWAsfQJxXXnJidciDJxzPAzk2kQH7r5z0&sid=934bfa15&type=tcp&headerType=none#admin
```

**Shadowsocks (Fallback - Better Compatibility):**
```
ss://MjAyMi1ibGFrZTMtYWVzLTI1Ni1nY206WTQ5a0dLbm0zd29ScHRvSkhMY3VWdlo4UTMyblZwWEQrR3ZscnFEa0U1TT0=@54.206.37.229:8388#admin-fallback
```

### Method 2: Manual Configuration

If your app doesn't support import links, use these settings:

#### VLESS+REALITY Settings:
- **Server:** `54.206.37.229`
- **Port:** `443`
- **UUID:** `ab87d164-971c-44d8-8c34-b4e4ff9f2e71`
- **Protocol:** VLESS
- **Security:** REALITY
- **Flow:** xtls-rprx-vision
- **SNI:** `www.apple.com`
- **Public Key:** `R8rHTLBhepmWAsfQJxXXnJidciDJxzPAzk2kQH7r5z0`
- **Short ID:** `934bfa15`
- **Fingerprint:** chrome

#### Shadowsocks Settings:
- **Server:** `54.206.37.229`
- **Port:** `8388`
- **Password:** `Y49kGKnm3woRptoJHLcuVvZ8Q32nVpXD+GvlrqDkE5M=`
- **Method:** `2022-blake3-aes-256-gcm`

## 📲 Recommended Apps

### iOS (App Store)
- **v2Box** - Free, supports VLESS+REALITY
- **Shadowrocket** - $2.99, very stable

### Android (Google Play / APK)
- **v2rayNG** - Free, supports VLESS+REALITY
- **ShadowsocksAndroid** - Free, Shadowsocks only

### macOS
- **Qv2ray** - Free, full-featured
- **ClashX Pro** - Free, simple UI

### Windows
- **v2rayN** - Free, most popular
- **Clash for Windows** - Free, good UI

## 🔧 VPS Management

### Check VPN Status
```bash
ssh customvpn
cd customVpn
docker compose ps
```

### View Logs
```bash
docker compose logs -f xray
docker compose logs -f shadowsocks
```

### Restart Services
```bash
docker compose restart
```

### Add More Users
```bash
sudo /root/.local/bin/poetry run python scripts/python/user_manager.py add <username> <email>
```

### Create Backup
```bash
sudo /root/.local/bin/poetry run python scripts/python/s3_backup.py
```

## 🌍 Migration to Singapore

When ready to move to Singapore (closer to China):

1. **Update terraform config:**
   ```bash
   cd scripts/terraform
   # Edit terraform.tfvars: change region to ap-southeast-1
   terraform apply
   ```

2. **Deploy VPN:**
   ```bash
   ssh <new-singapore-ip>
   git clone https://github.com/sshaunn/customVpn.git
   cd customVpn
   # Copy config.env from Melbourne
   sudo bash deploy.sh
   ```

3. **Update client apps** with new server IP

## 🔒 Security Best Practices

- ✅ VPN is encrypted end-to-end
- ✅ Firewall configured
- ✅ SSH on custom port (2222)
- ✅ Auto-updates enabled (Watchtower)
- ✅ Telegram notifications configured

## 📊 Monitoring

You'll receive Telegram notifications for:
- Service down alerts
- Deployment updates
- Backup status

Check Telegram: You should have received test messages during integration tests!

## 🆘 Troubleshooting

### Can't connect?
1. Check VPS is running: `ssh customvpn 'docker compose ps'`
2. Check ports are open: `nc -zv 54.206.37.229 443`
3. View logs: `docker compose logs -f`

### Slow connection?
- Try Shadowsocks instead of VLESS
- Check VPS location (Melbourne may be far from China)
- Consider migrating to Singapore

### Need help?
- Check logs: `docker compose logs`
- Check container health: `docker compose ps`
- Restart services: `docker compose restart`

## ✨ What's Running

- **Xray (VLESS+REALITY)** - Port 443 - Advanced anti-censorship
- **Shadowsocks** - Port 8388 - Reliable fallback
- **Watchtower** - Auto-updates containers
- **Monitoring** - Health checks every 5 minutes

Enjoy your private VPN! 🚀
