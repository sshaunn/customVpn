import pytest
from pathlib import Path


@pytest.fixture
def terraform_dir():
    """Get terraform directory"""
    return Path(__file__).parent.parent / "scripts" / "terraform"


def test_terraform_main_exists(terraform_dir):
    """Test main.tf exists"""
    main_tf = terraform_dir / "main.tf"
    assert main_tf.exists(), "main.tf missing"
    assert main_tf.is_file(), "main.tf is not a file"


def test_terraform_variables_exists(terraform_dir):
    """Test variables.tf exists"""
    variables_tf = terraform_dir / "variables.tf"
    assert variables_tf.exists(), "variables.tf missing"
    assert variables_tf.is_file(), "variables.tf is not a file"


def test_terraform_outputs_exists(terraform_dir):
    """Test outputs.tf exists"""
    outputs_tf = terraform_dir / "outputs.tf"
    assert outputs_tf.exists(), "outputs.tf missing"
    assert outputs_tf.is_file(), "outputs.tf is not a file"


def test_terraform_gitignore_exists(terraform_dir):
    """Test .gitignore exists"""
    gitignore = terraform_dir / ".gitignore"
    assert gitignore.exists(), ".gitignore missing in terraform dir"


def test_terraform_readme_exists(terraform_dir):
    """Test README.md exists"""
    readme = terraform_dir / "README.md"
    assert readme.exists(), "README.md missing in terraform dir"


def test_main_tf_has_provider(terraform_dir):
    """Test main.tf has AWS provider"""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    assert "provider \"aws\"" in content, "AWS provider not configured"
    assert "hashicorp/aws" in content, "AWS provider source missing"


def test_main_tf_has_security_group(terraform_dir):
    """Test main.tf has security group resource"""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    assert "aws_security_group" in content, "Security group resource missing"
    assert "customvpn-sg" in content, "Security group name missing"


def test_main_tf_has_correct_ports(terraform_dir):
    """Test main.tf has all required ports"""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    required_ports = ["22", "2222", "443", "8388"]
    for port in required_ports:
        assert port in content, f"Port {port} not configured"


def test_main_tf_has_ec2_instance(terraform_dir):
    """Test main.tf has EC2 instance resource"""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    assert "aws_instance" in content, "EC2 instance resource missing"
    assert "ubuntu" in content.lower(), "Ubuntu AMI not configured"


def test_main_tf_has_storage_config(terraform_dir):
    """Test main.tf has storage configuration"""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    assert "root_block_device" in content, "Storage config missing"
    assert "volume_size" in content, "Volume size not set"
    assert "20" in content, "Storage not 20GB"
    assert "gp3" in content, "Not using gp3 storage"


def test_variables_tf_has_region(terraform_dir):
    """Test variables.tf has region variable"""
    variables_tf = terraform_dir / "variables.tf"
    content = variables_tf.read_text()

    assert "aws_region" in content, "aws_region variable missing"
    assert "ap-southeast-1" in content, "Singapore region not default"


def test_variables_tf_has_instance_type(terraform_dir):
    """Test variables.tf has instance_type variable"""
    variables_tf = terraform_dir / "variables.tf"
    content = variables_tf.read_text()

    assert "instance_type" in content, "instance_type variable missing"
    assert "t3.micro" in content, "t3.micro not default"


def test_variables_tf_has_key_name(terraform_dir):
    """Test variables.tf has key_name variable"""
    variables_tf = terraform_dir / "variables.tf"
    content = variables_tf.read_text()

    assert "key_name" in content, "key_name variable missing"
    assert "customvpn-key" in content, "customvpn-key not default"


def test_outputs_tf_has_public_ip(terraform_dir):
    """Test outputs.tf has public_ip output"""
    outputs_tf = terraform_dir / "outputs.tf"
    content = outputs_tf.read_text()

    assert "public_ip" in content, "public_ip output missing"


def test_outputs_tf_has_ssh_command(terraform_dir):
    """Test outputs.tf has ssh_command output"""
    outputs_tf = terraform_dir / "outputs.tf"
    content = outputs_tf.read_text()

    assert "ssh_command" in content, "ssh_command output missing"


def test_terraform_gitignore_has_tfstate(terraform_dir):
    """Test .gitignore excludes tfstate files"""
    gitignore = terraform_dir / ".gitignore"
    content = gitignore.read_text()

    assert "*.tfstate" in content, "tfstate not ignored"
    assert ".terraform/" in content, ".terraform/ not ignored"


def test_readme_has_usage_instructions(terraform_dir):
    """Test README has basic usage instructions"""
    readme = terraform_dir / "README.md"
    content = readme_tf = readme.read_text()

    assert "terraform init" in content, "terraform init command missing"
    assert "terraform apply" in content, "terraform apply command missing"
    assert "terraform destroy" in content, "terraform destroy command missing"


@pytest.mark.skipif(True, reason="Requires Terraform binary installed")
def test_terraform_validate():
    """Test terraform validate passes (requires Terraform)"""
    pass


@pytest.mark.skipif(True, reason="Requires AWS credentials")
def test_terraform_plan():
    """Test terraform plan succeeds (requires AWS)"""
    pass
