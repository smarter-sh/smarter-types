SAM Annotations
===============

A Smarter Application Manifest (SAM) may carry ``metadata.annotations``: a
map of string keys to string values that any client or extension attaches to a
resource for its own purposes, as Kubernetes annotations are. A key typically
names a resource in another system, e.g. an account in a CRM, and its value is
the identifier or setting that goes with it:

.. code-block:: yaml

    metadata:
      name: support-bot
      annotations:
        acme.com/crm-account-id: A-10042
        acme.com/active: "true"

:mod:`smarter_types.annotations` holds the rules that decide what a valid
annotation is. The platform enforces them when a manifest is applied, and a
client can check annotations with the same rules before it sends them. See
`Manifests <https://docs.smarter.sh/smarter-framework/smarter-manifests.html>`__
in Smarter's documentation for how the platform stores and acts on them.

Keys
----

A key is an optional prefix, a slash, and a name, e.g.
``acme.com/crm-account-id``:

- **The prefix** is a lowercase DNS subdomain of at most 253 characters, which
  names the key's owner. ``smarter.sh`` and its subdomains are reserved for the
  platform (:func:`~smarter_types.annotations.is_reserved_annotation_key`).
- **The name** is one or more segments separated by slashes. Each segment is 1
  to 63 characters, begins and ends with a letter or digit, and contains only
  letters, digits, ``-``, ``_`` and ``.``. Kubernetes allows one segment;
  Smarter allows several, e.g. ``smarter.sh/llmclient/use-case``, so every
  Kubernetes key is a Smarter key.
- **The whole key** is at most 317 characters.

.. code-block:: python

    from smarter_types import SmarterTypesValueError, validate_annotation_key

    validate_annotation_key("acme.com/crm-account-id")  # "acme.com/crm-account-id"

    try:
        validate_annotation_key("Acme.com/crm-account-id")
    except SmarterTypesValueError as e:
        print(e)  # the prefix must be a lowercase DNS subdomain

Values
------

Values are strings. YAML reads an unquoted ``true``, ``42`` or ``2026-10-28``
as a boolean, a number or a date, so
:func:`~smarter_types.normalize_annotations` converts them to the string that
was written: ``"true"``, ``"42"``, ``"2026-10-28"``. A list or a map is
rejected; quote structured data as a JSON string.

All of a resource's annotations together, keys and values in UTF-8, are
limited to 256 KiB, as in Kubernetes. A key may appear only once.

Older manifests wrote annotations as a list of one-key maps.
:func:`~smarter_types.normalize_annotations` accepts that form, either form as
a JSON string, and ``None``, and returns the map:

.. code-block:: python

    from smarter_types import normalize_annotations

    normalize_annotations([{"acme.com/crm-account-id": "A-10042"}, {"acme.com/active": True}])
    # {"acme.com/crm-account-id": "A-10042", "acme.com/active": "true"}

Selectors
---------

The cli api's ``get`` finds resources by their annotations with selectors in
the syntax of Kubernetes label selectors, one requirement per ``annotation``
query parameter. A resource must match every requirement:

============================  ==============================================
Requirement                   Matches resources whose annotation
============================  ==============================================
``acme.com/crm-id``           ``acme.com/crm-id`` exists, with any value
``!acme.com/crm-id``          ``acme.com/crm-id`` doesn't exist
``acme.com/crm-id=A-10042``   ``acme.com/crm-id`` is ``A-10042``
``acme.com/crm-id!=A-10042``  ``acme.com/crm-id`` is missing, or isn't ``A-10042``
============================  ==============================================

A value is everything after the first ``=``, and may contain commas, which is
why requirements aren't joined into one string.
:func:`~smarter_types.parse_annotation_requirement` checks one, and returns an
:class:`~smarter_types.annotations.AnnotationRequirement` whose ``str()`` is
the text to send:

.. code-block:: python

    from smarter_types import AnnotationOperator, parse_annotation_requirement

    requirement = parse_annotation_requirement("acme.com/crm-id!=A-10042")
    requirement.operator is AnnotationOperator.NOT_EQUALS  # True
    str(requirement)  # "acme.com/crm-id!=A-10042"
