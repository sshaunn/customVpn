variable "aws_region" {
  description = "AWS region for VPS deployment"
  type        = string
  default     = "ap-southeast-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "instance_name" {
  description = "Name tag for EC2 instance"
  type        = string
  default     = "customvpn-server"
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default     = "customvpn-key"
}
