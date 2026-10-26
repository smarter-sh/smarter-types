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
- **Every example must be true.** Check it against the code and its tests, or
  run it. E.g. a static plugin's kind is `Plugin`, not `StaticPlugin`.
- `double backticks` for literals, settings and commands. Console examples
  start with `$ ` (copybutton strips it).
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
  distribution (`github_actions.tf`). It trusts GitHub's OIDC provider, which
  is one per AWS account: this stack reads it with a data source, because
  cache-results' docs stack creates it. Apply that stack first in a new
  account.

```console
make terraform-init    # once: the S3 backend (state key smarter-types/docs/terraform.tfstate)
make terraform-plan    # writes terraform/docs/tfplan: read it before applying
make terraform-apply   # applies exactly that plan
```

The state bucket's name and `allowed_account_ids` contain the AWS account id,
so the Makefile reads it from the caller's credentials at run time. Never write
an account id, or a distribution id, into this public repository. Run
`terraform -chdir=terraform/docs fmt` and `validate` after editing, and apply
only a plan the user has seen: these are live, billable resources in a shared
account and DNS zone.
