---
name: smarter-types-docstrings
description: Use when writing or editing Python docstrings in smarter-types. Docstrings are the package's api reference (Sphinx autodoc on docs.smarter-types.smarter.sh), so they follow Smarter's reStructuredText field-list style (:param:, :type:, :returns:, :rtype:, :raises:), the layout that pydocstringformatter enforces, the rule that module docstrings start with a sentence, and how to document enum members and the apply order.
---

# smarter-types Docstrings

Docstrings explain the code to contributors, and become the package's api
reference through Sphinx autodoc (`smarter-types-sphinx-docs`). The style is
Smarter's (`../smarter/skills/smarter-docstrings`), so that the platform, the
SDK and this package read the same. The platform's and the SDK's own docs
render these classes too, through their re-exports, so a docstring here is
read in three places.

## Style: reStructuredText field lists

```python
@classmethod
def apply_rank(cls, kind: str | SAMKinds) -> int:
    """
    Return the position of a kind in :meth:`apply_order`.

    .. code-block:: python

        SAMKinds.apply_rank(SAMKinds.SECRET) < SAMKinds.apply_rank("SqlConnection")  # True

    :param kind: The kind, as a member or its value, in any case.
    :type kind: str | SAMKinds
    :returns: The kind's position, or the length of :meth:`apply_order` for a kind that isn't a SAM kind.
    :rtype: int
    """
```

- `:param:` for every parameter, with `:type:`.
- `:returns:` says what the value means, including `None` cases, with `:rtype:`.
- `:raises X:` for each exception a caller should handle, e.g.
  `:raises SmarterTypesValueError: If the string is not a SAM kind.`
- Never Google style (`Args:`, `Attributes:`): Sphinx renders it as prose.
- **`:type:` and `:rtype:` repeat the annotation, spelled the same way**
  (`str | None`, not `Optional[str]`). The platform omits them because it
  runs `sphinx_autodoc_typehints`; this package doesn't, so the fields are
  where the reference gets its types. Change both in the same edit.
- Indent continuation lines by four spaces.

## Enum members

Document a member with a string literal directly below it; autodoc shows it
under the member:

```python
SECRET = "Secret"
"""An encrypted value, such as a password or an api key, that other resources name."""
```

## The apply order's docstring is its specification

`SAMKinds.apply_order()`'s docstring lists every kind, in order, with what its
manifests name and what names it. A kind added to the tuple gets its numbered
entry in the same edit, and a reorder changes both. Reviewers read the
docstring to check the tuple.

## Layout (pydocstringformatter enforces it)

- Opening `"""` on its own line, then a **one-line summary ending with a
  period**, a blank line, then the body. A two-line summary is mangled: the
  formatter puts a period at the end of the first line. Put the whole first
  sentence on the summary line, however long.
- A body paragraph starts with a capital letter. One that starts lower case
  usually means a summary was split.
- One blank line between paragraphs, and between the body and the fields.
- **pydocstringformatter capitalizes the first word.** A module docstring that
  starts with `smarter_types.kinds` becomes `Smarter_types.kinds`. Start module
  docstrings with a sentence ("Every kind of Smarter Application Manifest.").
  The same goes for a summary that starts with a name: put it in double
  backticks, or rephrase.

## Content

- **Module docstrings** say what the module holds, and who reads it: the
  platform, the SDK, or both.
- **Class docstrings** say what the enumeration represents, and where its
  values end up (manifests, journal entries, urls, cli commands).
- **Methods** cover purpose, parameters, return value and exceptions. Nothing
  here has side effects; a method that gains one says so.
- Say why, not only what, when the reason isn't obvious, e.g. why a kind comes
  before another in the apply order.
- Be accurate. A docstring that describes old behavior is worse than none.
  Change it in the same edit as the behavior.

## reST inside docstrings

- Double backticks for literals (values, file names), and Sphinx roles for
  cross-references, e.g. `:class:`~smarter_types.kinds.SAMKinds``,
`:meth:`apply_order``, `:mod:`smarter_types.journal``. The `~` shows only
  the last component.
- Don't reference the platform's or the SDK's modules with a role: this
  package's docs can't resolve them. Name them in double backticks.
- Example code: `.. code-block:: python` (or `console`), a blank line, then
  indented content.
- Lists and code blocks need a blank line before them.

## Test docstrings

A test module has a one-line docstring naming what it tests
(`"""Tests of smarter_types.kinds."""`), and each test a one-line docstring
stating the behavior it proves.

## Verify

Run the pre-commit hooks on the file and review what pydocstringformatter
changed (`smarter-types-code-quality`), then `make sphinx-build`, which fails
on any warning.
