# Terraform Advanced Patterns

## Module Structure

```
modules/
├── web-server/
│   ├── main.tf        # Resources
│   ├── variables.tf   # Input variables
│   ├── outputs.tf     # Output values
│   └── versions.tf    # Provider requirements
```

```hcl
# modules/web-server/main.tf
resource "aws_instance" "this" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id

  tags = merge(var.tags, {
    Name = var.name
  })
}

resource "aws_security_group" "this" {
  name   = "${var.name}-sg"
  vpc_id = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ingress.value.cidrs
    }
  }
}

# modules/web-server/variables.tf
variable "name" { type = string }
variable "ami_id" { type = string }
variable "instance_type" { type = string; default = "t3.micro" }
variable "subnet_id" { type = string }
variable "vpc_id" { type = string }
variable "tags" { type = map(string); default = {} }
variable "ingress_rules" {
  type = list(object({
    port  = number
    cidrs = list(string)
  }))
  default = []
}

# modules/web-server/outputs.tf
output "instance_id" { value = aws_instance.this.id }
output "public_ip" { value = aws_instance.this.public_ip }
output "security_group_id" { value = aws_security_group.this.id }
```

## Remote State Data Source

```hcl
# Access state from another project
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "terraform-state"
    key    = "vpc/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_instance" "web" {
  subnet_id = data.terraform_remote_state.vpc.outputs.public_subnet_ids[0]
}
```

## Backend Configurations

```hcl
# S3 backend with DynamoDB locking
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

# Terraform Cloud
terraform {
  cloud {
    organization = "my-org"
    workspaces {
      name = "my-app-prod"
    }
  }
}
```

## Moved Blocks (Refactoring)

```hcl
# Rename resource without destroy/recreate
moved {
  from = aws_instance.web
  to   = aws_instance.app_server
}

# Move into module
moved {
  from = aws_instance.web
  to   = module.web_server.aws_instance.this
}
```

## Import Blocks (Terraform 1.5+)

```hcl
import {
  to = aws_instance.web
  id = "i-1234567890abcdef0"
}

# Generate config
terraform plan -generate-config-out=generated.tf
```

## Sensitive Data

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}

output "connection_string" {
  value     = "postgres://admin:${var.db_password}@${aws_db_instance.main.endpoint}"
  sensitive = true
}

# Use with terraform output -json to see sensitive values
```

## Testing (Terraform 1.6+)

```hcl
# tests/main.tftest.hcl
run "create_instance" {
  command = plan

  assert {
    condition     = aws_instance.web.instance_type == "t3.micro"
    error_message = "Instance type should be t3.micro"
  }
}

run "check_tags" {
  command = plan

  assert {
    condition     = aws_instance.web.tags["Environment"] == "dev"
    error_message = "Should be tagged with dev environment"
  }
}
```

```bash
terraform test
```
