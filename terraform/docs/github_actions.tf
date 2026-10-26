#------------------------------------------------------------------------------
# The Release workflow's access to the docs site.
#
# After a release reaches PyPI, the workflow's publish-docs job uploads the
# site and invalidates CloudFront. It signs in with GitHub's OIDC token, so no
# AWS key is stored in GitHub, and only a job in this repository's "docs"
# environment can assume the role. That environment is limited to main in the
# repository's settings, as the "pypi" environment is.
#------------------------------------------------------------------------------

# GitHub's OIDC provider is one per AWS account, shared by every repository's
# workflows, each with a role of its own. A per-repository stack must only read
# it: creating it fails in an account that already has one, and destroying the
# stack would break every other repository's workflows.
data "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"
}

# This stack created the provider before it was shared. Forget it without
# destroying it. Remove this block once every copy of the state has applied it.
removed {
  from = aws_iam_openid_connect_provider.github_actions

  lifecycle {
    destroy = false
  }
}

data "aws_iam_policy_document" "docs_publisher_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github_actions.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repository}:environment:${var.github_environment}"]
    }
  }
}

resource "aws_iam_role" "docs_publisher" {
  name               = "smarter-types-docs-publisher"
  description        = "The smarter-types Release workflow, publishing ${var.domain_name}"
  assume_role_policy = data.aws_iam_policy_document.docs_publisher_trust.json
}

# Exactly what make sphinx-publish does: sync the bucket, and invalidate the distribution.
data "aws_iam_policy_document" "docs_publisher" {
  statement {
    sid       = "ListTheBucket"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.docs.arn]
  }

  statement {
    sid       = "SyncTheSite"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.docs.arn}/*"]
  }

  statement {
    sid       = "InvalidateTheDistribution"
    actions   = ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"]
    resources = [aws_cloudfront_distribution.docs.arn]
  }
}

resource "aws_iam_role_policy" "docs_publisher" {
  name   = "publish-docs"
  role   = aws_iam_role.docs_publisher.id
  policy = data.aws_iam_policy_document.docs_publisher.json
}
