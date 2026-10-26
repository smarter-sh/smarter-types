ADR-001: Plain-Python Types Shared by the Platform and the SDK
==============================================================

Status
------
Accepted

Context
-------
The Smarter platform and the Smarter Python SDK must agree on the same
enumerations: the kinds of manifest, the order in which to apply them, and the
Smarter Journal's things and cli commands. Defined in each, the copies drift:
a kind added to the platform is rejected by the SDK until someone copies it
there. The SDK runs without Django, so whatever both share can't need Django.

Decision
--------
smarter-types holds the type definitions that the platform and the SDK share,
and both depend on it.

- **Plain Python only.** No Django, no Pydantic, no settings, no database. Its
  only runtime dependency is ``inflection``.
- **SAMKinds is the single source of truth for the existence of a kind.**
  Other enumerations derive from it: each kind in ``SmarterJournalThings``
  takes its value from the ``SAMKinds`` member of the same name. A kind's
  place in ``SAMKinds.apply_order()`` is part of its definition.
- **Imports don't change.** The platform and the SDK re-export these classes
  from the modules that defined them before, e.g.
  ``smarter.apps.api.v1.manifests.enum`` and ``smarter.models.kinds``.
- **What belongs here:** enumerations and constants that both sides read, and
  helpers that return plain values, such as a tuple of Django model
  ``choices``.
- **What doesn't:** anything that only one side needs (e.g. the web console's
  icon of each kind), and anything that needs Django, Pydantic, settings or a
  database (models, forms, serializers, Pydantic models).

Alternatives Considered
-----------------------
- Keep a copy in each, with a test that compares them. The test finds drift
  only after it happens, and only in the repository that runs it.
- Let the SDK import the platform. The SDK would then install Django.
- Generate the SDK's enumerations from the platform's api contract. That
  covers the kinds' values, but not the methods, such as the apply order.

Consequences
------------
- **Positive:**

  - A kind, cli command or journal thing is defined once, and the platform and
    the SDK can't disagree about it.
  - The package is small, fast to test, and installs anywhere.

- **Negative:**

  - A new kind takes a release here, then a change of minimum version in the
    platform and the SDK.
  - Removing or renaming a member breaks both, and manifests already written,
    so it needs a major release.

Related ADRs
------------
- `Smarter ADR-005: Manifests <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/005-manifests.rst>`__
- `Smarter ADR-024: Broker Model <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/024-broker-model.rst>`__
