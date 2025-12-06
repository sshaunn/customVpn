output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.vpn.id
}

output "public_ip" {
  description = "Public IP address"
  value       = aws_instance.vpn.public_ip
}

output "public_dns" {
  description = "Public DNS name"
  value       = aws_instance.vpn.public_dns
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.vpn.id
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ${var.key_name}.pem ubuntu@${aws_instance.vpn.public_ip}"
}

output "instance_details" {
  description = "Instance configuration summary"
  value = {
    type    = var.instance_type
    region  = var.aws_region
    storage = "20GB gp3 SSD"
    os      = "Ubuntu 24.04 LTS"
  }
}
