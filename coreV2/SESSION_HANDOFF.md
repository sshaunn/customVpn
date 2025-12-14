# Session Handoff - CustomVPN V2

**Date**: 2025-12-15
**Status**: Clean slate, ready to build
**Location**: `/Users/shenpeng/Git/customVpn/coreV2/`

---

## What Was Done

### Cleanup
- ✅ Deleted entire V1 implementation (~650MB of old code)
- ✅ Removed 61 files, 5,272 lines of code
- ✅ Created clean `coreV2/` directory structure
- ✅ Committed and pushed to GitHub (commit: d8e89ff)

### Current Infrastructure
- ✅ VPS: Bandwagon 80.251.215.127
- ✅ User: `shaun` (with sudo)
- ✅ SSH: `ssh customvpn` (key-based auth working)
- ✅ Docker: Installed and running
- ✅ Domain: `shaunstudio.vip` → 80.251.215.127 (DNS working)

### VPS is Clean
```bash
ssh customvpn 'ls -la ~/'
# Output: Only .ssh, .bashrc, .profile
# No containers running
# No nginx installed yet
# Completely fresh
```

---

## Where We Are Now

**Project Structure:**
```
coreV2/
├── TASKS_V2.md          # 14 tasks defined
├── CHANGELOG_V2.md      # Change tracking
├── SESSION_HANDOFF.md   # This file
├── scripts/             # Empty (to create)
├── configs/             # Empty (to create)
├── docker/              # Empty (to create)
│   ├── xray/
│   └── shadowsocks/
└── tests/               # Empty (to create)
```

**Config Available:**
```bash
# In /Users/shenpeng/Git/customVpn/config.env
VPS_IP=80.251.215.127
VPS_USER=shaun
DOMAIN=shaunstudio.vip
ADMIN_USERNAME=shaun
ADMIN_UUID=ab87d164-971c-44d8-8c34-b4e4ff9f2e71
XRAY_PORT=443
SHADOWSOCKS_PORT=8388
WEBSOCKET_PATH=/api/v3/events/stream
```

---

## What to Do Next

### Start with Task 1.1: Create Xray Dockerfile

**File**: `coreV2/docker/xray/Dockerfile`

**Requirements:**
- Alpine-based (small size)
- Install Xray-core latest version
- Expose port 10000 (internal, Nginx will proxy)
- Non-root user
- Copy config at runtime

**Example Structure:**
```dockerfile
FROM alpine:latest

# Install Xray
RUN apk add --no-cache curl unzip && \
    curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -o /tmp/xray.zip && \
    unzip /tmp/xray.zip -d /usr/local/bin/ && \
    rm /tmp/xray.zip

# Non-root user
RUN adduser -D -u 1000 xray
USER xray

# Config will be mounted at runtime
EXPOSE 10000

CMD ["/usr/local/bin/xray", "run", "-c", "/etc/xray/config.json"]
```

**Test:**
```bash
cd coreV2
docker build -t xray-test docker/xray
```

---

## Task Breakdown (14 tasks total)

### Phase 1: Docker Images (20 min)
- [ ] Task 1.1: Xray Dockerfile
- [ ] Task 1.2: Shadowsocks Dockerfile
- [ ] Task 1.3: docker-compose.yml

### Phase 2: Config Templates (15 min)
- [ ] Task 2.1: Xray config template (Jinja2)
- [ ] Task 2.2: Shadowsocks config
- [ ] Task 2.3: Nginx config template
- [ ] Task 2.4: Fake website HTML

### Phase 3: Python Scripts (40 min)
- [ ] Task 3.1: config_generator.py
- [ ] Task 3.2: uploader.py
- [ ] Task 3.3: deployer.py
- [ ] Task 3.4: verifier.py
- [ ] Task 3.5: client_config.py

### Phase 4: Main Script (15 min)
- [ ] Task 4.1: deploy.py (orchestrates everything)

---

## Important Notes

### SSH Access
```bash
# Direct SSH to VPS
ssh customvpn

# Run commands
ssh customvpn 'whoami'  # Returns: shaun
ssh customvpn 'docker ps'  # Works, shaun is in docker group
```

### Git Setup
```bash
# Personal SSH key configured
git config --local core.sshCommand "ssh -i ~/.ssh/id_rsa_personal -F /dev/null"

# Push works
git push  # Goes to sshaunn/customVpn
```

### Do NOT
- ❌ Don't use bash scripts (hard to test)
- ❌ Don't create .md files in commits
- ❌ Don't add co-author to commits
- ❌ Don't install anything on VPS yet (wait for Python scripts)

### DO
- ✅ Use Python for all automation
- ✅ Write tests for each component
- ✅ Keep configs as Jinja2 templates
- ✅ Follow task order in TASKS_V2.md

---

## Dependencies Needed

Create `coreV2/requirements.txt`:
```txt
jinja2
paramiko
qrcode
pytest
pillow
```

---

## Context for Next Session

**User Goal**: Deploy stealth VPN on Bandwagon VPS for bypassing GFW during China trip

**Technical Approach**:
- VLESS + WebSocket + TLS (primary)
- Shadowsocks as fallback
- Nginx reverse proxy with fake website
- Everything in Docker containers
- Python-based deployment automation

**Key Insight from Analysis**:
- Traffic should look like normal HTTPS web browsing
- WebSocket path should look like API endpoint (`/api/v3/events/stream`)
- Need fake website for camouflage
- Domain fronting via Cloudflare (optional fallback)

---

## Quick Start for Next Session

```bash
# Navigate to project
cd /Users/shenpeng/Git/customVpn/coreV2

# Check tasks
cat TASKS_V2.md

# Start with Task 1.1
# Create docker/xray/Dockerfile

# When ready to test
docker build -t xray-test docker/xray
```

---

## Files to Reference

- **Task list**: `TASKS_V2.md`
- **VPS config**: `../config.env` (one level up)
- **Git repo**: `https://github.com/sshaunn/customVpn`
- **SSH config**: `~/.ssh/config` (has `customvpn` alias)

---

**Next Action**: Create Xray Dockerfile (Task 1.1)
