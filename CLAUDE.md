# CLAUDE.md

Guidance for Claude Code (and other coding agents) working in this repository.

smarter-types holds the plain-Python type definitions that the Smarter
platform and the Smarter Python SDK share, so that they are defined once
instead of copied. It is published to PyPI as `smarter-types`, with the import
name `smarter_types`. The platform is
[Smarter](https://github.com/smarter-sh/smarter) (usually checked out beside
this repository as `../smarter`), and the SDK is
[smarter-python](https://github.com/smarter-sh/smarter-python) (`../smarter-python`,
PyPI `smarter-api`, import `smarter`). Its documentation is published to
https://docs.smarter-types.smarter.sh/.

Detailed know-how lives in the Agent Skills under `skills/` (symlinked to
`.claude/skills`). **Load `smarter-types-development` first for any change.**
Its table says which narrower `smarter-types-*` skill covers each kind of
work. This file holds only what applies to nearly every task.

## Hard rules

1. **Never run git write commands**, here, in `../smarter` or in
   `../smarter-python`. "Write a git commit" means print the command as text:
   one `git commit` with one `-m` per paragraph, conventional-commit header of
   72 characters or fewer, authored by
   `Lawrence McDaniel <lpm0073@gmail.com>`, co-authored by
   `Claude <noreply@anthropic.com>`. See `smarter-types-git-commits`.
2. **Run the tests yourself** after any change (`make test`, `make coverage`).
   Report failures honestly.
3. **Plain Python only.** The only runtime dependency is `inflection`. Nothing
   here may import Django or Pydantic, or need settings or a database: the SDK
   runs without them.
4. **`SAMKinds` is the single source of truth for the existence of a kind.**
   Other enumerations take their values from it, and every kind has a
   deliberate place in `SAMKinds.apply_order()`.
5. **Values are promises.** Removing or renaming a member, or changing a
   value, breaks the platform, the SDK, manifests already written and journal
   entries already stored. That needs a major release.
6. **The pre-commit hooks are the lint standard** (`make lint`).
7. **Coverage:** at least 95% (`make coverage`).
8. **This repository is public.** No credentials, account ids, private
   hostnames or customer data.

## Repository map

| Path                               | Contents                                                    |
| ---------------------------------- | ----------------------------------------------------------- |
| `src/smarter_types/kinds.py`       | `SAMKinds`: every SAM kind, and the apply order             |
| `src/smarter_types/journal.py`     | The journal's things, cli commands and response keys        |
| `src/smarter_types/enum.py`        | `SmarterEnumAbstract`, the enumerations' base class         |
| `src/smarter_types/exceptions.py`  | `SmarterTypesError`, `SmarterTypesValueError`               |
| `src/smarter_types/__version__.py` | The version. Written by semantic-release, never by hand     |
| `tests/`                           | pytest tests, one module per source module                  |
| `.github/workflows/ci.yml`         | CI: lint, mypy and tests on Python 3.10-3.14, docs, build   |
| `.github/workflows/release.yml`    | Release: semantic-release, build, PyPI, the docs site       |
| `release.config.js`                | semantic-release: version file, changelog                   |
| `codecov.yml`                      | Codecov targets: 95% project and patch                      |
| `requirements/in/*.in`             | Unpinned requirements, compiled into `requirements/*.txt`   |
| `docs/source/`                     | Sphinx docs: guide, api reference, ADRs (`adr/`)            |
| `terraform/docs/`                  | The docs site's AWS resources: S3, CloudFront, ACM, Route53 |
| `skills/`                          | Agent Skills, symlinked to `.claude/skills`                 |

## Conventions

- Docstrings are reStructuredText (`:param:`, `:returns:`, `:raises:`), for
  Sphinx autodoc.
- Log messages start with `ClassName.method()`, and use %-style arguments.
- A change here usually has a second half in `../smarter` and
  `../smarter-python` (raise their minimum version, then use it). Say so in
  your summary.
