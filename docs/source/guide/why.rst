Why smarter-types Exists
========================

The Smarter platform (a Django application) and the Smarter Python SDK
(``smarter-api``) speak the same language: the same kinds of manifest, the
same cli verbs, the same journal. Each used to define those enumerations
itself, so adding a kind meant changing both, and forgetting one made the SDK
reject a manifest that the platform accepts, or the other way round.

smarter-types defines them once. Both the platform and the SDK depend on it.

Defined once
------------

:class:`~smarter_types.kinds.SAMKinds` is the single source of truth for which
kinds exist. Other enumerations derive from it rather than repeat it: each of
:class:`~smarter_types.journal.SmarterJournalThings`' kinds takes its value
from the SAMKinds member of the same name. A kind is added in one place, and
reaches the platform and the SDK when they raise their minimum version of this
package.

Imports don't change
--------------------

The platform and the SDK re-export these classes from the modules that
defined them before, so code that imports them from there keeps working:

.. code-block:: python

    # in the platform
    from smarter.apps.api.v1.manifests.enum import SAMKinds

    # in the SDK
    from smarter.models.kinds import SAMKinds

    # the same class, from either
    from smarter_types import SAMKinds

No Django
---------

The SDK runs anywhere Python does, without Django, so nothing here may need
Django, Pydantic, settings or a database. A plain tuple of Django model
``choices`` is fine; a model, a form or a serializer is not. Things that only
the platform needs, such as the web console's icon of each kind, stay in the
platform. See :doc:`../adr/001-scope`.
