# Terraform VPS Infrastructure

Terraform configuration for deploying CustomVPN EC2 instance in Singapore.

## Prerequisites

1. Install Terraform: `brew install terraform` (macOS) or download from terraform.io
2. AWS credentials configured in `../../config.env`

## Quick Start

### 1. Create SSH Key Pair

```bash
cd /Users/shenpeng/Git/customVpn
aws ec2 create-key-pair \
  --key-name customvpn-key \
  --region ap-southeast-1 \
  --query 'KeyMaterial' \
  --output text > customvpn-key.pem
chmod 400 customvpn-key.pem
```

### 2. Initialize Terraform

```bash
cd scripts/terraform
terraform init
```

### 3. Plan Deployment

```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
terraform plan
```

### 4. Deploy VPS

```bash
terraform apply
```

Type `yes` when prompted.

### 5. Get Outputs

```bash
terraform output public_ip
terraform output ssh_command
```

## Configuration

Edit `variables.tf` or override via command line:

```bash
terraform apply -var="instance_type=t3.small"
```

## Destroy VPS

When done:

```bash
terraform destroy
```

## Files

- `main.tf` - Main infrastructure definition
- `variables.tf` - Configuration variables
- `outputs.tf` - Output values (IP, SSH command)
- `terraform.tfstate` - State file (gitignored)

## Instance Specs

- **Region:** Singapore (ap-southeast-1)
- **Type:** t3.micro (1GB RAM, 2 vCPUs)
- **Storage:** 20GB gp3 SSD
- **OS:** Ubuntu 24.04 LTS

## Security Group Rules

- Port 22: SSH (initial setup)
- Port 2222: SSH (hardened)
- Port 443: Xray VLESS+REALITY
- Port 8388: Shadowsocks (TCP/UDP)
