SAM Kinds and the Apply Order
=============================

The kinds
---------

:class:`~smarter_types.kinds.SAMKinds` has one member for every kind of Smarter
Application Manifest: plugins, connections, account resources (accounts,
users, api keys, secrets, guardrails, budgets), prompt resources (LLMClients,
LLMHosts, MCPClients, custom domains, orchestrators), providers, proxies, and
vector stores. Its class methods read and group them:

.. code-block:: python

    from smarter_types import SAMKinds

    SAMKinds.all()                          # every kind's value
    SAMKinds.str_to_kind("llmclient")       # "LLMClient"
    SAMKinds.plural("ApiConnection")        # "ApiConnections"
    SAMKinds.all_plugins()                  # [SAMKinds.STATIC_PLUGIN, SAMKinds.API_PLUGIN, ...]
    SAMKinds.all_connections()              # [SAMKinds.API_CONNECTION, SAMKinds.SQL_CONNECTION]

:meth:`~smarter_types.kinds.SAMKinds.plural` pluralizes only the final
CamelCase word, so ``ApiConnection`` becomes ``ApiConnections``.

The apply order
---------------

SAM resources refer to one another **by name**. A SqlPlugin's
``spec.connection`` is the name of a SqlConnection, and a SqlConnection's
``password`` is the name of a Secret. The platform resolves each name when it
applies a manifest, so the resource that is named must already exist. A set of
manifests, such as a project in a git repository, can only be applied in an
order where every resource comes after the resources that it names.

:meth:`~smarter_types.kinds.SAMKinds.apply_order` is that order, for every
kind, and :meth:`~smarter_types.kinds.SAMKinds.apply_rank` is a kind's position
in it. A kind that isn't a SAM kind ranks last. Sort by it:

.. code-block:: python

    from pathlib import Path

    import yaml

    from smarter_types import SAMKinds

    manifests = [yaml.safe_load(p.read_text()) for p in Path("manifests").glob("*.yaml")]
    for manifest in sorted(manifests, key=lambda m: SAMKinds.apply_rank(m["kind"])):
        apply(manifest)  # e.g. the SDK's client, or the smarter cli

``sorted()`` is stable, so manifests of the same kind keep their order.
Accounts come first, because everything belongs to one; Secrets come before
everything that names a Secret; LLMClients come after the Plugins, Guardrails,
MCPClients and CustomDomains they name; and Budgets come last, because they can
name nearly any kind of resource. The docstring of
:meth:`~smarter_types.kinds.SAMKinds.apply_order` gives every kind's place,
and why.

Adding a kind
-------------

A new kind is a member of ``SAMKinds`` **and** a deliberate place in
``apply_order()``: after every kind its manifests may name, and before every
kind that may name it. The tests fail until both exist. Then:

#. Release smarter-types (a ``feat`` commit makes a minor release).
#. Raise the platform's and the SDK's minimum version of ``smarter-types`` to
   that release, and add the kind's broker and model there.
