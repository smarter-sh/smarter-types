---
name: smarter-types-release
description: Use when working on smarter-types' CI/CD, dependencies or releases - the requirements files (requirements/in/constraints.in, base.in, local.in, compiled by make python-requirements), the CI workflow (lint, mypy and tests on Python 3.10-3.14, docs, terraform, build), Codecov, semantic-release (release.config.js, versions, the changelog, tags, prereleases from alpha and beta), the Release workflow and PyPI trusted publishing, supported Python versions, and raising the platform's and the SDK's minimum version - or when asked why CI failed, what the next version will be, or how to cut a release.
---

# smarter-types CI/CD and Releases

## CI (`.github/workflows/ci.yml`)

Runs on every pull request, and as the first job of every Release run, which
starts on every push to `main`, `alpha` and `beta`:

| Job         | What it does                                                                     |
| ----------- | -------------------------------------------------------------------------------- |
| `lint`      | `pre-commit run --all-files`: the same hooks as `make lint`                      |
| `test`      | `mypy`, then `coverage run -m pytest`, on Python 3.10, 3.11, 3.12, 3.13, 3.14    |
| `docs`      | `sphinx-build -W`: the same as `make sphinx-build`                               |
| `terraform` | `terraform fmt -check` and `validate` of `terraform/docs`, without AWS access    |
| `build`     | after the others: `python -m build`, `twine check --strict`, the `dist` artifact |

Every `make` target has a CI counterpart, and the other way round: keep them
consistent when you change either.

```console
gh run list --limit 5
gh run view <id>            # jobs and annotations
gh run view <id> --log-failed
```

- Each test job uploads `coverage.xml` to **Codecov** (`codecov.yml`: 95%
  project and patch targets), flagged by Python version. Codecov merges them.
  The upload needs the repository secret `CODECOV_TOKEN`, and never fails CI.
- Action versions are pinned to a major (`actions/checkout@v7`). Look up the
  latest with `gh api repos/<owner>/<action>/releases/latest --jq .tag_name`
  rather than from memory; an old major shows a Node.js deprecation
  annotation.
- Lint workflows with actionlint before committing:
  `docker run --rm -v "$(pwd)":/repo --workdir /repo rhysd/actionlint:latest`.

## Versions come from commits: semantic-release

`release.config.js` configures semantic-release. From the conventional
commits since the last tag (`smarter-types-git-commits`):

- `fix` and `perf` make a patch release, `feat` a minor one, a
  `BREAKING CHANGE:` footer a major one. Other types make none.
- It writes the version into `src/smarter_types/__version__.py` (which
  `pyproject.toml` reads, through hatchling), updates `CHANGELOG.md`, commits
  both as `chore(release): <version> [skip ci]`, tags `v<version>`, and
  publishes a GitHub release.
- **Never edit `__version__.py` or `CHANGELOG.md` by hand**, and never write a
  `chore(release)` commit.
- `main` makes releases. `alpha` and `beta` make prereleases, e.g.
  `0.2.0-alpha.1`, which Python's packaging normalizes to `0.2.0a1`.
- With no tags at all, semantic-release's first release is `1.0.0`. To start
  at `0.1.0` instead, the user tags the first commit `v0.0.0` before the first
  push to `main` (as cache-results did); never run `git tag` yourself.

## The Release workflow (`.github/workflows/release.yml`)

Runs on **every push to `main`, `alpha` and `beta`**: a push to `main` makes a
release, and a push to `alpha` or `beta` a prerelease. A push whose commits
since the last tag release nothing (`docs`, `ci`, `build`, `chore`, ...) runs CI
and stops. semantic-release's own commit ends in `[skip ci]`, so it starts no
run. Runs are one at a time per branch: a push during a release waits, then
releases everything since the last tag. It can also be started by hand:

```console
make release-dry-run     # gh workflow run release.yml -f dry_run=true: CI, then the next version
make release             # the same as a push, e.g. to re-run a release
gh run watch
```

1. `ci`: the whole CI workflow (`ci.yml` is also a reusable workflow). Nothing
   is released unless it passes.
2. `release`: semantic-release, as above. A dry run stops here, and the run's
   summary shows the last and next versions.
3. `dist`: checks out the new tag, builds, `twine check --strict`, and fails
   unless `__version__.py` is the release, and `dist/` holds exactly one wheel
   and one sdist of it, named with the PEP 440 spelling (`0.2.0-alpha.1` is
   `0.2.0a1`).
4. `attach`: uploads the distributions to the GitHub release.
5. `publish-testpypi`, then `verify-testpypi`: a rehearsal on TestPyPI, when
   the variable `PUBLISH_TO_TESTPYPI` is `"true"`. The verify job installs the
   upload back, its dependencies from PyPI and only smarter-types from TestPyPI
   (anyone can upload a look-alike of a dependency there), and checks the
   installed `__version__`.
6. `publish-pypi`, then `verify-pypi`: PyPI, **from `main` only**, when
   `PUBLISH_TO_PYPI` is `"true"`, and only if the rehearsal passed or is off.
   Prereleases from `alpha` and `beta` stop at TestPyPI.
7. `publish-docs`: once `verify-pypi` passed, and when `PUBLISH_DOCS` is
   `"true"`, builds the Sphinx site from the release tag (warnings are errors),
   syncs it to the docs bucket, invalidates CloudFront, and waits until
   https://docs.smarter-types.smarter.sh/ shows the new version. It runs in the
   `docs` environment and signs in to AWS with GitHub's OIDC token, as the
   role in `terraform/docs/github_actions.tf`, which only that environment can
   assume and which can only sync the bucket and invalidate the distribution.
   So the site always documents what PyPI serves, and prereleases never reach it.

- Releasing and publishing are **one workflow**, so that a tagged release
  can't miss PyPI. Don't split them.
- Uploads use **trusted publishing** (OIDC): there is no PyPI token anywhere.
  Each index needs `release.yml` registered as a trusted publisher of the
  `smarter-types` project, for the `testpypi` and `pypi` environments.
- Uploads `skip-existing`, so a run that failed after an upload can be run
  again.

- The README's and docs' status badge is the Release workflow's, on `main`:
  `ci.yml` runs on pushes only inside it.

Secrets: `CODECOV_TOKEN` (coverage), and `PAT` only when `main` is protected
against `GITHUB_TOKEN`'s pushes. Variables: `PUBLISH_TO_TESTPYPI` and
`PUBLISH_TO_PYPI`, `"false"` until the trusted publishers are registered;
`PUBLISH_DOCS`, `"false"` until the publisher role exists; and
`DOCS_AWS_ROLE_ARN`, `DOCS_BUCKET` and `DOCS_DISTRIBUTION_ID`, which are
`terraform/docs`' outputs `publisher_role_arn`, `bucket_name` and
`distribution_id`. They are repository variables, not files, because this
public repository must not contain an account or distribution id. The `docs`
environment allows only `main`, as `pypi` does.

## Dependencies and requirements

Laid out as Smarter's (`../smarter/smarter/requirements/`), see ADR-013:

| File                                 | What it holds                                                           |
| ------------------------------------ | ----------------------------------------------------------------------- |
| `pyproject.toml`                     | What the **published** package needs: `inflection`, and the extras      |
| `requirements/in/constraints.in`     | Global version constraints, with a reason each. Every `.in` includes it |
| `requirements/in/base.in`            | The runtime requirements, unpinned                                      |
| `requirements/in/local.in`           | `-r base.in`, plus every developer tool, unpinned and commented         |
| `requirements/base.txt`, `local.txt` | **Generated** by pip-compile: every version pinned. Never edit by hand  |

```console
make python-requirements   # pip-compile --upgrade both .in files, then install local.txt and the package
make init                  # rebuild venv/ from local.txt, install the package editable, and the git hooks
```

- A new development tool goes into `in/local.in`, with a comment saying what
  it is for, then `make python-requirements`. A new runtime dependency is a
  decision (ADR-001: plain Python, `inflection` only): it goes into
  `pyproject.toml` **and** `in/base.in`, with the same lower bound in
  `constraints.in`.
- A version that must be avoided goes into `constraints.in`, with the reason,
  as Smarter's does (e.g. `pip-tools>=7.6.1`).
- `--no-strip-extras` keeps `coverage[toml]`'s extra in `local.txt`.
- The compiled files are committed, as a `build(deps):` commit.
- CI installs the package with its extras, not `local.txt`, so that it tests
  what users install.

## Supported versions

Python 3.10 and newer. When a Python release arrives or reaches end of life,
change together: the `ci.yml` matrix, the `pyproject.toml` classifiers (and
`requires-python`), the README's badge, and `CLAUDE.md`. The platform and the
SDK must support at least the same range. Dropping a version is a breaking
change.

## The platform's and the SDK's minimum versions

A release reaches its users only when they raise their requirement:

- **The platform** (`../smarter`) pins `smarter-types` in
  `smarter/requirements/in/` and its compiled files. Its Docker image runs
  `manage.py` while it builds, so a platform change that needs a new kind
  can't be built until that version is on PyPI. To test before then, build a
  wheel (`python -m build --wheel`) and `pip install --no-deps` it into the
  running `smarter-app` container (`../smarter/skills/smarter-docker-environment`).
- **The SDK** (`../smarter-python`) requires `smarter-types>=<version>` in its
  `pyproject.toml` and `requirements/in/`.

Each bump is a commit of that repository's own, following its own git-commits
skill. Never change them unless the user asks; say in your summary that they
are needed.
