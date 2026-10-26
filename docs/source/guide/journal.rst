The Smarter Journal's Enumerations
==================================

The Smarter Journal records every request to the platform's ``/api/v1/cli/``
api, and the response it sent. :mod:`smarter_types.journal` holds the
enumerations that a journal entry, and a cli response, are made of.

Things
------

:class:`~smarter_types.journal.SmarterJournalThings` lists the things that the
journal records: every SAM kind, plus one thing that isn't a manifest,
``PROMPT_CONFIG`` (``ChatConfig``), a chat's configuration. Each kind's value
comes from :class:`~smarter_types.kinds.SAMKinds`, so the two can't disagree:

.. code-block:: python

    from smarter_types import SAMKinds, SmarterJournalThings

    SmarterJournalThings.SQL_PLUGIN.value == SAMKinds.SQL_PLUGIN.value  # True

Cli commands
------------

:class:`~smarter_types.journal.SmarterJournalCliCommands` lists the verbs of
the ``/api/v1/cli/`` api, such as ``apply``, ``get``, ``describe``, ``delete``
and ``deploy``. Each is the last part of its url, e.g.
``/api/v1/cli/apply/``:

.. code-block:: python

    from smarter_types import SmarterJournalCliCommands

    SmarterJournalCliCommands("apply") is SmarterJournalCliCommands.APPLY  # True

Response keys
-------------

The cli api's json responses use fixed keys: ``api``, ``thing``, ``metadata``,
``data``, and on an error ``error``, with its own keys such as ``errorClass``
and ``description``. :mod:`smarter_types.journal` names them, so that the
platform writes and the SDK reads the same keys.
