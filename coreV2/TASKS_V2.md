# CustomVPN V2 - Task Breakdown (Python-based)

## Current Status
- VPS: Bandwagon 80.251.215.127 (user: shaun)
- Domain: shaunstudio.vip → 80.251.215.127
- SSH: Working (ssh customvpn)
- Docker: Installed ✓
- Language: Python 3 (testable, reliable)

---

## Phase 1: Docker Images (20 min)

### Task 1.1: Xray Dockerfile
**File**: `docker/xray/Dockerfile`
- Alpine-based
- Install Xray-core
- Expose port 10000
**Test**: `docker build -t xray-test docker/xray`

### Task 1.2: Shadowsocks Dockerfile
**File**: `docker/shadowsocks/Dockerfile`
- Alpine-based
- Install shadowsocks-rust
- Expose port 8388
**Test**: `docker build -t ss-test docker/shadowsocks`

### Task 1.3: docker-compose.yml
**File**: `configs/docker-compose.yml`
- Xray + Shadowsocks services
- Host networking
- Auto-restart
**Test**: `docker compose config`

---

## Phase 2: Config Templates (15 min)

### Task 2.1: Xray config template
**File**: `configs/xray.json.j2`
- VLESS + WebSocket
- Variables: {{UUID}}, {{DOMAIN}}, {{PATH}}
**Test**: Jinja2 rendering

### Task 2.2: Shadowsocks config
**File**: `configs/shadowsocks.json`
- 2022-blake3-aes-256-gcm
- Generate random password
**Test**: JSON validation

### Task 2.3: Nginx config template
**File**: `configs/nginx.conf.j2`
- HTTPS + WebSocket proxy
- Variables: {{DOMAIN}}, {{PATH}}
**Test**: Template rendering

### Task 2.4: Fake website
**File**: `configs/index.html`
- Simple portfolio page
**Test**: Valid HTML

---

## Phase 3: Python Scripts (40 min)

### Task 3.1: config_generator.py
**Purpose**: Generate all configs from templates
```python
def generate_configs(uuid, domain, ws_path):
    # Render Jinja2 templates
    # Write to output directory
    # Return config paths
```
**Test**: `pytest test_config_generator.py`

### Task 3.2: uploader.py
**Purpose**: Upload files to VPS via SSH
```python
def upload_to_vps(local_dir, remote_dir):
    # Use paramiko or subprocess
    # Upload configs and Dockerfiles
    # Verify upload
```
**Test**: Mock SSH, verify file list

### Task 3.3: deployer.py
**Purpose**: Remote deployment orchestration
```python
def deploy():
    # SSH to VPS
    # Run setup commands
    # Build Docker images
    # Start containers
    # Configure Nginx
    # Get SSL cert
```
**Test**: Mock SSH commands

### Task 3.4: verifier.py
**Purpose**: Health check
```python
def verify_deployment():
    # Check Docker containers
    # Check ports
    # Check SSL cert
    # Check website
    # Return status report
```
**Test**: Mock responses

### Task 3.5: client_config.py
**Purpose**: Generate client configs
```python
def generate_client_config(uuid, domain, path):
    # Generate VLESS link
    # Generate QR code
    # Save to file
```
**Test**: Validate link format

---

## Phase 4: Main Deployment Script (15 min)

### Task 4.1: deploy.py (main entry point)
**Purpose**: Orchestrate entire deployment
```python
# Load config.env
# 1. Generate configs
# 2. Upload files
# 3. Deploy to VPS
# 4. Verify
# 5. Generate client config
# 6. Display results
```
**Test**: Integration test (full flow)

---

## Total: 90 minutes

## File Structure
```
coreV2/
├── deploy.py              (Task 4.1 - main)
├── config.env             (VPS settings)
├── requirements.txt       (Python deps)
├── scripts/
│   ├── config_generator.py  (Task 3.1)
│   ├── uploader.py          (Task 3.2)
│   ├── deployer.py          (Task 3.3)
│   ├── verifier.py          (Task 3.4)
│   └── client_config.py     (Task 3.5)
├── configs/
│   ├── xray.json.j2         (Task 2.1)
│   ├── shadowsocks.json     (Task 2.2)
│   ├── nginx.conf.j2        (Task 2.3)
│   ├── index.html           (Task 2.4)
│   └── docker-compose.yml   (Task 1.3)
├── docker/
│   ├── xray/Dockerfile      (Task 1.1)
│   └── shadowsocks/Dockerfile (Task 1.2)
├── tests/
│   └── test_*.py            (Unit tests)
└── docs/
    ├── TASKS_V2.md
    └── CHANGELOG_V2.md
```

---

## Dependencies
```txt
jinja2
paramiko
qrcode
pytest
```

---

## Next Action
Task 1.1: Create Xray Dockerfile
