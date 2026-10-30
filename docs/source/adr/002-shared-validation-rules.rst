ADR-002: Shared Validation Rules
================================

Status
------
Accepted

Context
-------
Some values that a client writes into a manifest or a request have rules: an
annotation's key and value, or an annotation selector. The platform enforces
them, and a client such as the SDK needs the same rules to check a value
before it sends it. Copied into the client, the rules drift, and a value that
one side accepts the other rejects.

Decision
--------
The rules that decide whether a value is valid, when both the platform and its
clients need them, are defined here, as plain functions and constants.

- They return plain values, and raise
  :class:`~smarter_types.exceptions.SmarterTypesValueError`. The platform
  translates that into its own exception where it needs one.
- They follow :doc:`001-scope`: no Django, no Pydantic. A small result, such
  as a parsed selector requirement, is a frozen dataclass.
- What the platform does with a valid value, such as storing it or querying by
  it, stays in the platform.

Alternatives Considered
-----------------------
- Keep the rules in the platform only. Clients learn of an invalid value only
  from a failed request.
- Publish the rules as JSON Schema. A schema can describe a key's pattern, but
  not normalization, such as converting a YAML boolean to ``"true"``, or the
  legacy list form of annotations.

Consequences
------------
- **Positive:**

  - The platform and its clients accept and reject the same values.
  - A client can report an invalid value without a request.

- **Negative:**

  - Making a rule stricter rejects values that manifests already hold, so it
    is a breaking change: a major release.

Related ADRs
------------
- :doc:`ADR-001: Plain-Python Types Shared by the Platform and the SDK <001-scope>`
- `Smarter ADR-033: Don't Repeat Yourself <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/033-dry.rst>`__
