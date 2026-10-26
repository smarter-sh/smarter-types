---
name: smarter-types-typing
description: Use when writing or reviewing type annotations in smarter-types, which ships py.typed so that the platform's, the SDK's and their users' type checkers read them. Covers the Python 3.10 syntax that pyupgrade enforces, annotating Enum class methods (str | SAMKinds, from __future__ import annotations), when Any is honest, and checking with make typecheck (mypy).
---

# smarter-types Type Annotations

The package ships `py.typed`, so **the platform's, the SDK's, and their users'
type checkers** read these annotations, and their editors show them. An
annotation is a claim; make it true. This is Smarter's rule
(`../smarter/skills/smarter-python-typing`), without Smarter's aliases: this
package depends on nothing that defines them.

## Syntax

- Python 3.10 and newer: `X | None`, `list[str]`, `tuple[str, ...]`,
  `type[SAMKinds]`. pyupgrade (`--py310-plus`) rewrites the old forms in
  annotations; write the new ones to begin with.
- A class method that takes or returns its own enum names the class in its
  annotation (`kind: str | SAMKinds`). The modules start with
  `from __future__ import annotations` so that works without quotes.

## Say what a method really returns

- `all()` returns values (`list[str]`); `all_plugins()` returns members
  (`list[SAMKinds]`). Keep that distinction in the annotation, so a caller
  knows whether it needs `.value`.
- A method that can't find something returns `None` only if its annotation
  says `| None`; one that raises says so in `:raises:`.

## When `Any` is acceptable

Almost never here: these are enumerations of strings. If you reach for `Any`,
list the types instead. Avoid `Optional[Any]`: it says no more than `Any`.

- **A finite set of types** is a union (`str | bytes`). If callers must then
  narrow it, that's the truth about the function; consider splitting it into
  two functions, each with one return type.
- **A return type that depends on an argument's type** takes `@overload`, or a
  `TypeVar` for a function that returns the object it was given.
- **A value that is only stored, compared or passed on** is `object`, not
  `Any`: it accepts anything and keeps the checker on.
- **A circular import** is solved with `if TYPE_CHECKING:`, never with `Any`.
  With `from __future__ import annotations`, the annotation needs no quotes.
- **The docstring's `:type:` and `:rtype:`** change with the annotation
  (`smarter-types-docstrings`).

## Checking your work

```console
make typecheck          # mypy, on src/smarter_types
git diff --name-only -- '*.py' | xargs grep -nE '(: *|-> *|\[)Any\b'
```

`make typecheck` must pass; CI runs mypy in every test job. For each `Any` the
grep finds, ask whether you can list the types instead.
