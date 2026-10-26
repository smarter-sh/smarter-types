---
name: smarter-types-testing
description: Use when writing, fixing or running the smarter-types tests, or raising coverage. Covers pytest with the src layout, the Python 3.10-3.14 matrix, the invariants the tests protect (every kind has a place in the apply order and a journal thing; dependencies come first; values never change by accident), coverage, and how to report results.
---

# smarter-types Testing

## How to run

From the repository root, with this repository's own virtual environment,
`venv/`, which `make init` builds from `requirements/local.txt`. Never run
them in another project's environment, e.g. `../smarter/venv` or
`../smarter-python/venv`: those already have Django or the SDK installed, and
hide an accidental import of either.

```console
make test                          # pytest
make coverage                      # with a coverage report; fails below 95%
make typecheck                     # mypy
venv/bin/python -m pytest tests/test_kinds.py -k apply   # one module or test
```

- Run the tests yourself, after every change, and report the counts. Never
  ask the user to re-run them.
- Read the pass and fail counts, not only the coverage table: a coverage
  report alone is not a result.
- `pyproject.toml` sets `pythonpath = ["src", "."]`, so the tests import the
  source tree even without `pip install -e .`.

## Other Python versions

CI runs Python 3.10 to 3.14 (`ci.yml`). To try one locally, make a throwaway
virtual environment outside the repository:

```console
python3.10 -m venv /tmp/venv-py310
/tmp/venv-py310/bin/pip install -e ".[test]"
/tmp/venv-py310/bin/python -m pytest -q -p no:cacheprovider
```

3.10 is the one most likely to differ: no `enum.StrEnum`, no `typing.Self`.

## Layout and conventions

- One test module per source module: `kinds.py` is tested by
  `tests/test_kinds.py`, `journal.py` by `tests/test_journal.py`, and so on.
- Plain pytest functions, parametrized where a table reads better, as the
  existing modules do.
  No Django, no database, no network.
- Test names say what's being proven (`test_dependencies_come_first`), and
  each test has a one-line docstring stating the behavior it proves.
- Test through the public api (`from smarter_types import ...`), as the
  platform and the SDK use it. Don't call private helpers just to touch lines.

## What the tests protect

- **Every kind is complete.** These iterate over `SAMKinds` rather than a
  hand-written list, so a new kind is checked automatically:
  `test_every_kind_has_a_place_in_the_order` (`apply_order()` holds every kind
  exactly once), `test_every_kind_is_a_thing` (each kind is a
  `SmarterJournalThings` value, and `ChatConfig` is the only thing that isn't),
  `test_values_are_unique`, and `test_plugins_and_connections`. Never make one
  of them pass by excluding the new kind.
- **The apply order's dependencies.** `test_dependencies_come_first` asserts
  each pair that must hold (Secret before SqlConnection, SqlConnection before
  SqlPlugin, LLMClient before Prompt, ...), and `test_budget_is_last`. A kind
  that names, or is named by, another kind adds its pairs here, so that a
  reorder that breaks one fails with its name.
- **Values are promises.** Tests that look a member up by its literal value
  (`SAMKinds("Plugin") is SAMKinds.STATIC_PLUGIN`) protect manifests and stored
  journal rows. Don't update them to make a change pass: a change that breaks
  them is a major release (`smarter-types-development`, rule 6).
- **Model choices.** `test_things_choices` and
  `test_commands_choices_and_past_tense` fix what the platform's journal model
  accepts. A change to them needs a migration in the platform
  (`../smarter/skills/smarter-migrations`).

## Things that will bite you

- **`SAMKinds("Plugin")` is `STATIC_PLUGIN`.** A static plugin's kind is
  `Plugin`, not `StaticPlugin`; and `AUTH_TOKEN`'s value is
  `SmarterAuthToken`. Read the values from the class, not from memory.
- **Enum aliases.** Two members with the same value make the second an alias,
  missing from iteration. A test that counts members catches it.
- **Logger names** are module paths: `caplog` or
  `assertLogs("smarter_types.enum", ...)` for `from_url()`'s warning.

## Coverage

At least 95%, with branch coverage (`pyproject.toml`). CI uploads every job's
`coverage.xml` to Codecov, flagged by Python version.

## Reporting

Report the pass, fail and skip counts honestly, the coverage, which Python
versions you ran, and anything you didn't run. Name pre-existing failures and
separate them from anything your change caused. Confirm "pre-existing" by
running the test on unchanged code, e.g. a copy of the repository in your
scratchpad with the changed files replaced by `git show HEAD:<path>`: don't
assume it. Never `git stash` or `git checkout` to do so.
