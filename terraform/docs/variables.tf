#------------------------------------------------------------------------------
# Inputs of the documentation site's stack.
#------------------------------------------------------------------------------

variable "aws_region" {
  description = "The region of the S3 bucket that holds the built site."
  type        = string
  default     = "us-east-2"
}

variable "domain_name" {
  description = "The documentation site's host name."
  type        = string
  default     = "docs.smarter-types.smarter.sh"
}

variable "hosted_zone_name" {
  description = "The Route53 hosted zone that the site's records go in."
  type        = string
  default     = "smarter.sh"
}

variable "github_repository" {
  description = "The GitHub repository whose Release workflow publishes the site, as owner/name."
  type        = string
  default     = "smarter-sh/smarter-types"
}

variable "github_environment" {
  description = "The GitHub environment of the Release workflow's publish-docs job: the only job that can assume the publisher role."
  type        = string
  default     = "docs"
}

locals {
  bucket_name = var.domain_name

  tags = {
    Project   = "smarter-types"
    Component = "docs"
    Terraform = "true"
    Source    = "github.com/smarter-sh/smarter-types/terraform/docs"
  }
}
