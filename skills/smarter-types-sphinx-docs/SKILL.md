---
name: smarter-types-sphinx-docs
description: Use when adding or editing smarter-types' Sphinx documentation in docs/source, published to https://docs.smarter-types.smarter.sh/ - the user guide, the api reference generated from docstrings, the architectural decision records (ADRs) in docs/source/adr - or when building, publishing, or changing the site's AWS hosting (terraform/docs). Covers the layout, headings and toctrees, autodoc pages, how to write an ADR, the evergreen-prose rule, make sphinx-build (warnings are errors), make sphinx-publish, and the Terraform stack.
---

# smarter-types Sphinx Documentation

The docs live in `docs/source/`, built by Sphinx with the Read the Docs theme
and published to **https://docs.smarter-types.smarter.sh/**. Extensions
(`docs/source/conf.py`): autodoc, intersphinx (Python's docs),
viewcode, copybutton, `notfound.extension` (the 404 page) and `sphinx_sitemap`.
They follow Smarter's conventions (`../smarter/skills/smarter-sphinx-docs`), on
a much smaller site.

## Build to verify

Unlike Smarter's 20-minute build, this one takes seconds. Build after every
docs or docstring change:

```console
make sphinx-build      # rm -rf docs/build, then sphinx-build -W --keep-going: every warning is an error
open docs/build/html/index.html
make sphinx-linkcheck  # every external link, when you've added some
```

It must succeed with no warnings. `conf.py` puts `src/` on `sys.path`, so
autodoc imports the source tree; there is no Django to set up. intersphinx
fetches Python's inventory, so the build needs the network.

`-W` catches malformed reST (a heading underline shorter than its title, a
directive whose content doesn't follow a blank line, a page in no toctree),
but not a page that renders wrong. Open each page you changed and read it:
code-block content indented consistently, lists that render as lists, links
that land where they should.

## Layout

| Content                          | Location                                                         |
| -------------------------------- | ---------------------------------------------------------------- |
| Landing page, badges, toctrees   | `index.rst`: Getting Started, User Guide, Reference, Project     |
| Getting started                  | `installation.rst`, `quickstart.rst`                             |
| User guide, one topic per page   | `guide/*.rst`: why, kinds (and the apply order), journal         |
| API reference                    | `reference.rst`, and one autodoc page per module in `reference/` |
| Changelog, contributing, license | `project/*.rst`                                                  |
| Architectural decision records   | `adr.rst` (the toctree), and `adr/NNN-<slug>.rst`                |
| Files copied as they are         | `_extra/` (`robots.txt`)                                         |

Headings: `=` for the page title, `-` for sections, then `~` and `^`. Every
page must be in a toctree, or the build warns.

## Cross-references

- **Another page of this site:** `:doc:`, relative to the referring page
  (`` :doc:`kinds` `` from `guide/journal.rst`), or absolute from `docs/source/`
  with a leading `/` (`` :doc:`/reference/kinds` ``). A missing target warns, so
  the build checks these.
- **A Python object:** `:class:`, `:meth:`, `:func:` with its full dotted
  path, and `~` to show only the last name
  (`` :class:`~smarter_types.kinds.SAMKinds` ``). Python's own objects
  (`` :class:`enum.Enum` ``) resolve through intersphinx. `nitpicky` is off, so a
  wrong path renders as plain text without a warning: check the link in the
  built page.
- **Smarter's docs, or the SDK's:** another site, so an absolute url, never
  `:doc:`, e.g.
  `` `Manifests <https://docs.smarter.sh/smarter-framework/smarter-manifests.html>`__ ``.
  docs.smarter.sh serves pages from its root (old `/en/latest/` urls
  redirect there). Sphinx doesn't check these; `make sphinx-linkcheck` does.

## The api reference comes from docstrings

An autodoc page is a title and `.. automodule:: smarter_types.<module>` with
`:members:`.
`conf.py` sets `members` and `show-inheritance` by default. A new module gets a
page in `reference/` and an entry in `reference.rst`. Fix a wrong reference in
the docstring, never the `.rst` (`smarter-types-docstrings`).

## ADRs

One decision each, in Michael Nygard's format, in the format of Smarter's
(`../smarter/docs/source/adr/`). Read `adr/000-intro.rst` first.

- **Sections, in order:** Status, Context, Decision, Alternatives Considered,
  Consequences (**Positive:** and **Negative:** lists), Related ADRs.
- **State the rule and the forces behind it. No history**: not how the code
  came to be, not what Smarter did or does. Say what is decided, in the words
  that matter (e.g. "`SAMKinds` is the _single source of truth_").
- **Title:** `ADR-NNN: <Decision>`, numbered after the last one, in a file
  named `NNN-<slug>.rst`, added to `adr.rst`'s toctree.
- **Related ADRs** link this site's ADRs with a `:doc:` role, and a Smarter
  ADR that this one adapts with its GitHub url. Links to Smarter belong only
  there:

  ```rst
  - :doc:`ADR-001: Plain-Python Types Shared by the Platform and the SDK <001-scope>`
  - `Smarter ADR-005: Manifests <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/005-manifests.rst>`__
  ```

- **Keep them brief**: a few sentences per section.
- **Never rewrite a decision.** Add an ADR that supersedes it, and set the old
  one's Status to `Superseded by ADR-NNN`.

## Writing rules

- **Evergreen prose**, as in Smarter: no "New in 0.2" sections. Weave a change
  into the page where its topic belongs. The changelog carries the history.
- Write for a reader new to this package, and perhaps to Smarter. Define a
  term on first use (a SAM kind, the apply order, the journal), and link the
  page that explains it.
- **Every example must be true.** Check it against the code and its tests, or
  run it. E.g. a static plugin's kind is `Plugin`, not `StaticPlugin`.
- `double backticks` for literals, settings and commands, and
  `.. code-block:: python` or `console` for examples. Console examples start
  with `$ ` (copybutton strips it).
- The README, `index.rst`, the guide and `SAMKinds.apply_order()`'s docstring overlap.
  When behavior changes, update all of them in the same change.

## Publishing

```console
make sphinx-publish   # sphinx-build, aws s3 sync --delete, CloudFront invalidation of /*
```

The Release workflow's `publish-docs` job publishes the site the same way after
every release from `main`, once PyPI has it (`smarter-types-release`), so a
release needs no step here. `make sphinx-publish` is for publishing between
releases, e.g. a docs fix. It reads the bucket and distribution from the
Terraform outputs, so it needs `make terraform-init` once, and AWS credentials
for the account. The user publishes; publish yourself only when asked.

## The site's AWS resources (`terraform/docs/`)

Everything is in Terraform; never change these resources by hand or with the
aws cli:

- an ACM certificate (us-east-1), validated by a Route53 record;
- a **private** S3 bucket named after the domain (us-east-2): all public
  access blocked, ACLs disabled, readable only by the distribution (OAC and
  the bucket policy);
- a CloudFront distribution: HTTPS only, the managed CachingOptimized policy,
  `404.html` for missing pages (S3 answers 403 for them), HTTP/2 and 3, IPv6;
- A and AAAA alias records in the `smarter.sh` zone;
- the `smarter-types-docs-publisher` role that the Release workflow's `docs`
  environment assumes, allowed only to sync the bucket and invalidate the
  distribution (`github_actions.tf`), trusting only this repository's `docs`
  environment. GitHub's OIDC provider, which the role trusts, is one per
  account and shared by every repository's stack, so this stack only reads it
  (`data "aws_iam_openid_connect_provider"`). This stack created the provider
  before it was shared; a `removed` block with `destroy = false` hands it off,
  and can be deleted once that is applied.

```console
make terraform-init    # once: the S3 backend (state key smarter-types/docs/terraform.tfstate)
make terraform-plan    # writes terraform/docs/tfplan: read it before applying
make terraform-apply   # applies exactly that plan
```

The state bucket's name contains the AWS account id, so the Makefile reads it
from the caller's credentials at run time. Terraform uses the credentials
selected by `AWS_PROFILE` directly; it needs no separate account id input.
Never write an account id, or a distribution id, into this public repository.
Run
`terraform -chdir=terraform/docs fmt` and `validate` after editing, and apply
only a plan the user has seen: these are live, billable resources in a shared
account and DNS zone.

### Rules for these stacks

These are what went wrong before; each one was found the hard way.

- **Plain `terraform` must work.** `cd terraform/docs && terraform plan` with
  only `AWS_PROFILE` set must not prompt for anything. Terraform signs in as
  the profile's account; never add a required variable that only `make` can
  fill (an `aws_account_id` with no default made a bare `terraform apply`
  stop at a prompt). The account id is needed only for the state bucket's
  name, at `make terraform-init`. An account guard, if any, is an optional
  variable (`default = null`, and
  `allowed_account_ids = var.aws_account_id == null ? null : [var.aws_account_id]`).
- **Read account-wide singletons, never create them.** GitHub's OIDC
  provider (`token.actions.githubusercontent.com`, one per account), the
  `smarter.sh` hosted zone and the state bucket are shared by every
  repository's stack. A stack reads them with a `data` source. Creating one
  fails with `EntityAlreadyExists` (409) in an account that has it, and a
  stack that owns one breaks every other repository when it is destroyed.
  To hand off one that a stack already owns, switch to the `data` source and
  add a `removed { from = ... lifecycle { destroy = false } }` block; the plan
  must say "will no longer be managed by Terraform, but will not be
  destroyed". Nothing manages the OIDC provider now; it is left in place.
- **Look in AWS before writing a stack.** Check with read-only `aws` calls
  whether the bucket, distribution, certificate, records or role already
  exist. Existing resources are adopted with `import` blocks and a
  configuration that describes them as they are, until the plan shows imports
  and no change to anything live, and no destroys. Compute import ids from
  `data` sources (e.g. a certificate's ARN from `data "aws_acm_certificate"`)
  so that no account id is written into the repository.
- **Plan before you hand it over.** After any change, run `terraform plan`
  yourself with the user's profile (it only reads) and read it: a stack that
  validates can still fail at apply. Never leave a stale `tfplan` behind.
- **When the user's apply fails, fix the stack.** Don't explain why it was
  run "wrong" or offer workarounds; the stack is what must work.
