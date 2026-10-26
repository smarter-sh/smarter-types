#------------------------------------------------------------------------------
# The documentation site, docs.smarter-types.smarter.sh: Terraform and
# provider versions, and where the state is kept.
#
# The state bucket's name contains the AWS account id, which this public
# repository must not, so it is passed at init time:
#   make terraform-init   (terraform init -backend-config="bucket=...")
#------------------------------------------------------------------------------

terraform {
  # 1.10 for the S3 backend's native state locking (use_lockfile).
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    key          = "smarter-types/docs/terraform.tfstate"
    region       = "us-east-2"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region

  # Only this AWS account may be operated on by this stack.
  allowed_account_ids = [var.aws_account_id]

  default_tags {
    tags = local.tags
  }
}

# CloudFront only uses ACM certificates from us-east-1.
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  allowed_account_ids = [var.aws_account_id]

  default_tags {
    tags = local.tags
  }
}
