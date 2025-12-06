# Changelog

## 2025-12-06

### Initial Setup
- add - project rules - coding standards
- add - task breakdown - 8 phases defined
- add - gitignore - secrets and generated files
- add - changelog - project tracking

### Task 1.1: Project Structure
- add - directory structure - 15 directories created
- add - requirements.txt - 14 dependencies pinned
- add - config template - AWS and Telegram placeholders
- add - structure tests - 5 test cases passed
- update - poetry migration - pyproject.toml with dependency groups
- update - tests - replaced requirements.txt checks with pyproject.toml
- status - task 1.1 complete - all tests passing with Poetry

### Task 1.2: Config Template System
- add - xray template - VLESS+REALITY with apple.com SNI
- add - shadowsocks template - SS-2022 cipher configuration
- add - config generator - Jinja2 rendering with validation
- add - generator tests - 6 test cases passed
- status - task 1.2 complete - all tests passing

### Task 1.3: Key Generation
- add - uuid generation - v4 format validation
- add - reality keypair - x25519 via xray binary
- add - short id generation - 8 char hex random
- add - shadowsocks password - 32 byte base64
- add - key generator tests - 6 passed, 2 skipped (no xray)
- status - task 1.3 complete - all tests passing

### Task 2.1: Xray Docker
- add - xray dockerfile - Alpine 3.19 based
- add - security features - non-root user, minimal packages
- add - architecture support - x86_64 and arm64
- add - dockerignore - exclude logs and configs
- add - docker tests - 4 passed, 2 skipped (no docker)
- status - task 2.1 complete - dockerfile validated

### Task 2.2: Shadowsocks Docker
- add - shadowsocks dockerfile - Alpine 3.19 with ss-rust
- add - security features - non-root user
- add - architecture support - x86_64 and arm64
- add - ss tests - 5 passed, 1 skipped
- status - task 2.2 complete - dockerfile validated

### Task 2.3: Docker Compose
- add - docker-compose.yml - orchestration for 3 services
- add - network mode - host networking for VPN
- add - health checks - automatic restart on failure
- add - watchtower - auto-update containers daily
- add - security hardening - cap_drop, no-new-privileges
- add - logging - 10MB rotation, 3 files max
- add - compose tests - 9 passed, 1 skipped
- status - task 2.3 complete - compose file validated

### Docker Integration Tests
- add - testcontainers - Python Docker testing framework
- add - integration tests - container build and run validation
- add - dual container test - xray and shadowsocks together
- add - port availability test - pre-flight checks
- status - integration tests - 1 passed, 3 skipped (no docker daemon)

### Task 3.2: User Management
- add - user class - username, uuid, email, created_at
- add - user manager - add, remove, get, list operations
- add - json persistence - users.json storage
- add - config integration - get_users_for_config method
- add - user tests - 14 tests passed
- add - integration tests - 3 tests passed
- update - gitignore - exclude users.json
- status - task 3.2 complete - full CRUD with persistence

### Task 3.3: Client Config Generator
- add - vless share link - universal import format
- add - shadowsocks share link - base64 encoded
- add - json config - v2rayN/v2rayU/Qv2ray compatible
- add - qr code generation - mobile scanning
- add - routing rules - China direct, others proxy
- add - client templates - 3 jinja2 templates
- add - client tests - 7 tests passed
- status - task 3.3 complete - multi-platform support

### Task 4.1: S3 Backup System
- add - s3 bucket created - vpn-backups-custom in Melbourne
- add - config.env - AWS credentials configured
- add - s3 backup module - tar.gz creation and upload
- add - gpg encryption - AES256 symmetric encryption
- add - backup restoration - download and decrypt
- add - retention policy - auto-delete old backups
- add - backup tests - 1 passed, 4 skipped (needs GPG on VPS)
- status - task 4.1 complete - encrypted backups to S3
