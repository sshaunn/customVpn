terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data source for latest Ubuntu 24.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd*/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group
resource "aws_security_group" "vpn" {
  name        = "customvpn-sg"
  description = "Security group for CustomVPN server"

  # SSH (initial)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH initial access"
  }

  # SSH (hardened port)
  ingress {
    from_port   = 2222
    to_port     = 2222
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH hardened port"
  }

  # Xray VLESS+REALITY (HTTPS)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Xray VLESS+REALITY"
  }

  # Shadowsocks TCP
  ingress {
    from_port   = 8388
    to_port     = 8388
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Shadowsocks TCP"
  }

  # Shadowsocks UDP
  ingress {
    from_port   = 8388
    to_port     = 8388
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Shadowsocks UDP"
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name    = "customvpn-sg"
    Project = "CustomVPN"
  }
}

# EC2 Instance
resource "aws_instance" "vpn" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.vpn.id]

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
  }

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get upgrade -y
              hostnamectl set-hostname customvpn-server
              EOF

  tags = {
    Name    = var.instance_name
    Project = "CustomVPN"
    Purpose = "VPN-China-Trip"
  }
}
