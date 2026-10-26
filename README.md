# smarter-types

[![A project of The Smarter Project](https://img.shields.io/badge/a%20project%20of-The%20Smarter%20Project-2F6FEB)](https://smarter.sh)
[![Release](https://github.com/smarter-sh/smarter-types/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/smarter-sh/smarter-types/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/smarter-sh/smarter-types/graph/badge.svg)](https://codecov.io/gh/smarter-sh/smarter-types)
[![PyPI](https://img.shields.io/pypi/v/smarter-types?logo=pypi&logoColor=white)](https://pypi.org/project/smarter-types/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE.txt)
[![Docs](https://img.shields.io/badge/docs-docs.smarter--types.smarter.sh-blue?logo=readthedocs)](https://docs.smarter-types.smarter.sh/)

The plain-Python type definitions that the
[Smarter](https://github.com/smarter-sh/smarter) platform and the
[Smarter Python SDK](https://github.com/smarter-sh/smarter-python)
(`pip install smarter-api`) share.

```python
from smarter_types import SAMKinds

SAMKinds.str_to_kind("sqlplugin")         # "SqlPlugin"
SAMKinds.plural(SAMKinds.API_CONNECTION)  # "ApiConnections"

# apply a set of manifests so that each resource comes after the ones it names.
manifests = [{"kind": "SqlPlugin"}, {"kind": "SqlConnection"}, {"kind": "Secret"}]
manifests.sort(key=lambda m: SAMKinds.apply_rank(m["kind"]))
[m["kind"] for m in manifests]            # ["Secret", "SqlConnection", "SqlPlugin"]
```

**Documentation: <https://docs.smarter-types.smarter.sh/>**

## Why it exists

The platform (a Django application) and the SDK (which runs without Django)
must agree on which kinds of manifest exist, which verbs the `/api/v1/cli/`
api has, and what the journal records. smarter-types is the shared source of
truth for these definitions, and both depend on it. Each re-exports the
classes from the modules that used to provide them, so their own imports
don't change.

## What's in it

- **`smarter_types.kinds.SAMKinds`**: every SAM kind, and the single source of
  truth for which kinds exist. `str_to_kind()`, `plural()`, `all_plugins()`,
  `all_connections()`, and the apply order: `apply_order()` and `apply_rank()`.
- **`smarter_types.journal`**: `SmarterJournalThings` (the things the Smarter
  Journal records; each kind's value comes from `SAMKinds`),
  `SmarterJournalCliCommands` (the verbs of `/api/v1/cli/`), and the keys of
  the cli api's responses.
- **`smarter_types.enum.SmarterEnumAbstract`**: the base class of these
  enumerations, with `all()`, `list_all()`, the url slugs and `from_url()`.
- **`smarter_types.exceptions`**: `SmarterTypesError`, and
  `SmarterTypesValueError`, which is also a `ValueError`.

Plain Python: no Django, no Pydantic. Its only dependency is
[inflection](https://pypi.org/project/inflection/). Typed (`py.typed`).

## Installation

```console
pip install smarter-types
```

It needs Python 3.10 or newer. The Smarter platform and the Smarter Python SDK
install it for you.

## Development

```console
make            # list every command
make init       # create venv/ from requirements/local.txt, install the package and the git hooks
make test       # run the tests
make coverage   # run the tests with a coverage report (at least 95%)
make typecheck  # check the type annotations with mypy
make lint       # run the pre-commit hooks on every file
make sphinx-build   # build the Sphinx docs into docs/build/html
make sphinx-publish # publish them to docs.smarter-types.smarter.sh (releases do it themselves)
make build      # build the sdist and wheel, and check them
make python-requirements  # recompile the pinned requirements/*.txt
```

CI runs the hooks, mypy and the tests on every supported Python version, the
docs build, and a package build, on every pull request, and on every push to
`main`, `alpha` and `beta` as the first step of the Release workflow. Coverage
is reported to [Codecov](https://codecov.io/gh/smarter-sh/smarter-types).
When CI passes, the Release workflow releases with semantic-release, from the
conventional commit messages, and publishes to PyPI from `main` (or to TestPyPI
from `alpha` and `beta`). Once PyPI has a release from `main`, the same
workflow publishes its documentation to docs.smarter-types.smarter.sh.
`make release-dry-run` shows the next version.

### Adding a kind

1. Add the member to `SAMKinds`, and give it a place in `apply_order()`: after
   every kind its manifests may name, and before every kind that may name it.
   Add it to `SmarterJournalThings` too, with its value taken from `SAMKinds`.
2. Release it, with a `feat` commit.
3. Raise the minimum version of `smarter-types` in the platform and the SDK,
   and add the kind's broker and models there.

## Contributing

Bug reports, questions and pull requests are welcome. Please
[open an issue](https://github.com/smarter-sh/smarter-types/issues) before
starting on a larger change, so that its design can be agreed first.

1. Fork the repository, and branch from `main`.
2. Run `make init`. It also installs the pre-commit hooks, which are the lint
   standard (black, flake8, isort, pyupgrade, codespell, bandit, Prettier) and
   check each commit message.
3. Make your change with its tests. `make coverage` must stay at 95% or more.
4. Write [conventional commits](https://www.conventionalcommits.org/), e.g.
   `feat(kinds): add the Orchestrator kind`. Releases are versioned from them:
   `fix` makes a patch release, `feat` a minor one.
5. Open a pull request that says what changed and why, and links its issue.

Removing or renaming a member, or changing a value, breaks the platform, the
SDK and manifests already written, so it needs a major release.

Governance of the Smarter projects is described in
[smarter-sh/community](https://github.com/smarter-sh/community). Everyone who
takes part is expected to follow the [code of conduct](CODE_OF_CONDUCT.md).

## License

[AGPL-3.0-or-later](LICENSE.txt)
