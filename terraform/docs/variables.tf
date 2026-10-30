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

# The repository uses GitHub's immutable OIDC subject, which names the owner and the
# repository by name and numeric id, so that a deleted and re-created repository of the
# same name can't assume the role. Its prefix is the sub_claim_prefix that
#   gh api repos/smarter-sh/smarter-types/actions/oidc/customization/sub
# returns. The ids are GitHub's public ids, not secrets.
variable "github_oidc_subject_prefix" {
  description = "The prefix of the OIDC subject of the GitHub repository whose Release workflow publishes the site: repo:<owner>@<owner id>/<name>@<repository id>."
  type        = string
  default     = "repo:smarter-sh@170533864/smarter-types@1434400086"
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
