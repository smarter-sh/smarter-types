---
name: smarter-types-development
description: Start here for any change to the smarter-types repository, the plain-Python type definitions (SAMKinds, the apply order, the Smarter Journal's enumerations, SmarterEnumAbstract) that the Smarter platform and the Smarter Python SDK share, published to PyPI as smarter-types. Gives the non-negotiable rules, the package's design, how to add a SAM kind or cli command end to end, how the platform and the SDK re-export these classes and stay in sync, and an index of the narrower skills to load for each kind of work.
---

# smarter-types Development

`smarter-types` (import name `smarter_types`) holds the type definitions that
the Smarter platform ([smarter](https://github.com/smarter-sh/smarter),
usually checked out as `../smarter`) and the Smarter Python SDK
([smarter-python](https://github.com/smarter-sh/smarter-python),
`../smarter-python`, PyPI `smarter-api`, import `smarter`) must share. Before it
existed, each defined its own copy, and the copies drifted.

## Repository map

| Path                               | What lives there                                                             |
| ---------------------------------- | ---------------------------------------------------------------------------- |
| `src/smarter_types/kinds.py`       | `SAMKinds`: every SAM kind, `apply_order()`, `apply_rank()`, `plural()`      |
| `src/smarter_types/journal.py`     | `SmarterJournalThings`, `SmarterJournalCliCommands`, the response keys       |
| `src/smarter_types/enum.py`        | `SmarterEnumAbstract`: `all()`, `list_all()`, slugs, `from_url()`            |
| `src/smarter_types/exceptions.py`  | `SmarterTypesError`, `SmarterTypesValueError(SmarterTypesError, ValueError)` |
| `src/smarter_types/__version__.py` | The version. **Written by semantic-release**, never by hand                  |
| `tests/`                           | pytest tests, one module per source module                                   |
| `docs/source/`                     | Sphinx docs: guide, api reference, the ADRs (`docs/source/adr/`)             |
| `requirements/in/*.in`             | Unpinned requirements, compiled into the pinned `requirements/*.txt`         |
| `.github/workflows/`               | `ci.yml` (lint, mypy, tests, docs, build), `release.yml` (release, PyPI)     |
| `release.config.js`                | semantic-release's configuration                                             |
| `.pre-commit-config.yaml`          | The lint standard                                                            |
| `skills/`                          | These skills                                                                 |

## Non-negotiable rules

1. **Never execute git write commands**, here, in `../smarter` or in
   `../smarter-python`. "Write a git commit" means output the command text.
   See `smarter-types-git-commits`.
2. **Run the tests yourself** after every change (`make test`,
   `make coverage`). Never ask the user to re-run them. Report failures
   honestly. See `smarter-types-testing`.
3. **Plain Python only.** The only runtime dependency is `inflection`. Never
   import Django, Pydantic or anything that needs settings or a database: the
   SDK runs without them, and installing it must not install Django
   (ADR-001).
4. **`SAMKinds` is the single source of truth for the existence of a kind.**
   Other enumerations derive from it: each kind of `SmarterJournalThings` is
   `SAMKinds.<MEMBER>.value`, never a repeated string literal.
5. **Every kind has a deliberate place in `SAMKinds.apply_order()`**: after
   every kind its manifests may name, and before every kind that may name it.
   The tests fail for a kind without one. Never append a kind to the end to
   make them pass; work out what it names.
6. **Values are promises.** A member's value is written in manifests, stored
   in journal rows and Django `choices`, and sent over the api. Removing or
   renaming a member, or changing a value, is a breaking change: a major
   release with a `BREAKING CHANGE:` footer (`smarter-types-release`).
7. **The pre-commit hooks are the lint standard.** See `smarter-types-code-quality`.
8. **Coverage:** at least 95% (`pyproject.toml` fails the report below it).
9. **This repository is public.** No credentials, account ids, private
   hostnames or customer data in code, tests, docs or skills.
10. **Use this repository's own `venv/`**, built by `make init` from
    `requirements/local.txt`, never another project's. A requirement is added
    to `requirements/in/*.in`, then compiled with `make python-requirements`.
11. **Decisions are recorded as ADRs** in `docs/source/adr/`. Read ADR-001
    (scope) before adding anything new to the package.

## When the user reports that something didn't happen

If the user says that something didn't happen, e.g. "it did not create a
release", "PyPI still has the old version" or "the docs didn't change", that
is a problem to fix, not a claim to debate. Don't answer with evidence that it
did happen somewhere else, e.g. a prerelease on `alpha` or TestPyPI when they
mean `main` and PyPI. Find out what is missing from their point of view, why,
and fix it, or hand them the one command or click that fixes it.

## Pattern-first workflow

The package is small and consistent, and almost every change has a precedent.

1. Identify what kind of change it is: a kind, a cli command, a response key,
   a helper on `SmarterEnumAbstract`, a test, a doc page.
2. Find the existing members or functions of the same kind, and the tests and
   docs that go with them.
3. Copy their structure, naming, docstrings and logging. Don't introduce a new
   pattern when one exists.
4. Make the change, then its tests, docstrings and docs.
5. Run the hooks and the tests, and fix what they find.

When existing code disagrees with these skills, the code that is newest and
consistent with most of the package wins. Say so in your summary.

## What belongs here

- Enumerations and constants that **both** the platform and the SDK read.
- Helpers that return plain values, such as a tuple of Django model `choices`
  (a list of string pairs needs no Django).
- **Not:** anything only one side needs (e.g. the web console's icon of each
  kind stays in the platform), Pydantic models, Django models, forms,
  serializers, or anything that reads settings or a database.

## How the platform and the SDK use it

Both depend on `smarter-types`, and **re-export** its classes from the modules
that defined them before, so that their own imports don't change:

- the platform: `smarter.apps.api.v1.manifests.enum` (`SAMKinds`),
  `smarter.lib.journal.enum` (the journal's enumerations),
  `smarter.common.enum` (`SmarterEnumAbstract`);
- the SDK: `smarter.models.kinds` (`SAMKinds`).

A release reaches them only when their minimum version of `smarter-types` is
raised (`smarter-types-release`). Read their code in `../smarter` and
`../smarter-python` (read only, unless the user asks you to change them) to see
how a change here lands there:

- **Read the local checkouts**, not GitHub: grep them like any local code.
  First check that they are current:
  `../smarter/skills/smarter-project-repositories/scripts/repos-status.sh smarter smarter-python`
  (read only: it shows each checkout's branch, uncommitted changes, and
  whether it matches its remote). A checkout that is behind can mislead you.
  Say so, and give the user the `git -C ../<repository> pull` to run. Don't
  run it yourself: rule 1 applies to every repository.
- **Each has its own `CLAUDE.md` and skills.** Read them before changing
  anything there, and follow their rules, not this repository's: e.g. the
  platform's tests run in its Docker containers, not on the host.

## Adding a SAM kind, end to end

1. `kinds.py`: add the member to `SAMKinds`, in its group (plugins,
   connections, account, prompt, provider, proxy, vectorstore), with a
   docstring. If it is a plugin or connection, add it to `all_plugins()` or
   `all_connections()`.
2. `kinds.py`: give it a place in `apply_order()`, and a numbered entry in
   that method's docstring saying what it names and what names it.
3. `journal.py`: add it to `SmarterJournalThings`, its value taken from
   `SAMKinds`, and to `choices()` (the platform's journal model's choices: a
   change there is a migration in the platform).
4. Tests: `test_every_kind_has_a_place_in_the_order` and
   `test_every_kind_is_a_thing` must pass without being edited to exclude it.
   Add its pairs to `test_dependencies_come_first`, and its plural to
   `test_plural` if its last word pluralizes irregularly.
5. Docs: `docs/source/guide/kinds.rst` if a group or the order's summary
   changes.
6. Commit as `feat(kinds): add the <Kind> kind` (a minor release).
7. After it is on PyPI: in `../smarter`, raise the pin and add the kind's
   broker, model and api contract (its `smarter-sam-resource` skill); in
   `../smarter-python`, raise the minimum version and add its model.

A new cli command is the same, in `SmarterJournalCliCommands`, its
`choices()` and `past_tense()`.

## Logging

```python
logger = logging.getLogger(__name__)  # standard library
logger.warning("%s.from_url() could not extract manifest kind from URL: %s", cls.__name__, url)
```

- Messages start with `ClassName.method()` (`cls.__name__` or
  `type(self).__name__`, then the unformatted method name with `()`), so that
  a line can be traced to its code. Keep the name right when you rename the
  method.
- %-style arguments, never f-strings: a message that isn't emitted is never
  formatted, and aggregators can group messages by their template.
- The package logs little: only a value it can't interpret, at `warning`.
  Pick a level deliberately; nothing here is an `error` the caller can't
  handle from the return value.
- Never log a secret: an api key, a token, an `Authorization` header. Nothing
  here handles one today; a new message that could include one leaves it out.

## Which skill to load

| Task                                                    | Skill                        |
| ------------------------------------------------------- | ---------------------------- |
| Tests, the Python matrix, coverage                      | `smarter-types-testing`      |
| Docstrings                                              | `smarter-types-docstrings`   |
| Type annotations, `Any`, mypy                           | `smarter-types-typing`       |
| Lint, format, pre-commit                                | `smarter-types-code-quality` |
| Writing a commit message                                | `smarter-types-git-commits`  |
| CI, Codecov, semantic-release, versions, PyPI, the pins | `smarter-types-release`      |
| Documentation pages, ADRs, the docs site                | `smarter-types-sphinx-docs`  |

## Definition of done

- The change follows an existing pattern, and keeps rules 3 to 6.
- Tests cover it, and you ran `make test` and `make coverage` yourself. Report
  failures honestly, including pre-existing ones.
- `make typecheck` and the pre-commit hooks pass.
- Public objects have reST docstrings, and the README and guide describe any
  change a user can see.
- Your summary says whether the platform and the SDK need their minimum
  version raised, or other changes, to use it.
- Your summary says what changed, what you verified, and what you skipped.
