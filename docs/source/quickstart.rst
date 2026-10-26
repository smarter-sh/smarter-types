Quickstart
==========

Name a kind
-----------

Every kind of Smarter Application Manifest is a member of
:class:`~smarter_types.kinds.SAMKinds`. ``str()`` of a member is the kind as a
manifest spells it:

.. code-block:: python

    from smarter_types import SAMKinds

    str(SAMKinds.SQL_CONNECTION)  # "SqlConnection"
    SAMKinds.SQL_CONNECTION.value  # "SqlConnection"

Read a kind from a manifest
---------------------------

A manifest's ``kind`` can be written in any case.
:meth:`~smarter_types.kinds.SAMKinds.str_to_kind` returns its canonical
spelling, and raises :class:`~smarter_types.exceptions.SmarterTypesValueError`
for a kind that doesn't exist:

.. code-block:: python

    from smarter_types import SAMKinds, SmarterTypesValueError

    SAMKinds.str_to_kind("sqlconnection")  # "SqlConnection"

    try:
        SAMKinds.str_to_kind("NoSuchKind")
    except SmarterTypesValueError as e:
        print(e)

``SmarterTypesValueError`` is also a ``ValueError``.

Apply manifests in order
------------------------

Resources name one another, so a set of manifests must be applied in an order
where each resource comes after the ones it names. Sort them by
:meth:`~smarter_types.kinds.SAMKinds.apply_rank`:

.. code-block:: python

    manifests = [
        {"kind": "SqlPlugin", "metadata": {"name": "courses"}},
        {"kind": "SqlConnection", "metadata": {"name": "stackademy-db"}},
        {"kind": "Secret", "metadata": {"name": "stackademy-db-password"}},
    ]
    manifests.sort(key=lambda m: SAMKinds.apply_rank(m["kind"]))
    [m["kind"] for m in manifests]  # ["Secret", "SqlConnection", "SqlPlugin"]

See :doc:`guide/kinds` for the whole order, and why.

Next, :doc:`guide/why`.
