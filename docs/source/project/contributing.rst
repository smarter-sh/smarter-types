Contributing
============

Bug reports, questions and pull requests are welcome. Please
`open an issue <https://github.com/smarter-sh/smarter-types/issues>`__ before
starting on a larger change, so that its design can be agreed first.

Development setup
-----------------

.. code-block:: console

    $ git clone https://github.com/smarter-sh/smarter-types.git
    $ cd smarter-types
    $ make init

``make init`` creates the repository's own virtual environment, ``venv/``,
from the pinned ``requirements/local.txt``, installs the package in editable
mode, and installs the pre-commit hooks. ``make`` alone lists every command.

.. code-block:: console

    $ make test             # the tests
    $ make coverage         # with a coverage report: at least 95%
    $ make typecheck        # mypy
    $ make lint             # the pre-commit hooks, on every file
    $ make sphinx-build     # these docs, with warnings as errors

Pull requests
-------------

1. Fork the repository, and branch from ``main``.
2. Make your change with its tests. ``make coverage`` must stay at 95% or
   more. CI checks this, on every supported Python version.
3. Update the docs and docstrings for anything a user can see.
4. Write `conventional commits <https://www.conventionalcommits.org/>`__,
   e.g. ``feat(kinds): add the Orchestrator kind``. Releases are versioned from
   them: ``fix`` makes a patch release, ``feat`` a minor one.
5. Open a pull request that says what changed and why, and links its issue.

A few rules keep the platform and the SDK in step. They are explained in the
:doc:`../adr`:

- Plain Python only: nothing here may need Django, Pydantic, settings or a
  database.
- ``SAMKinds`` is the single source of truth for which kinds exist. Other
  enumerations take their values from it.
- A new kind needs a place in ``SAMKinds.apply_order()``.
- Removing or renaming a member, or changing a value, breaks the platform, the
  SDK, and manifests already written, so it needs a major release.

Code of conduct
---------------

Everyone who takes part is expected to follow the
`code of conduct <https://github.com/smarter-sh/smarter-types/blob/main/CODE_OF_CONDUCT.md>`__.
Governance of the Smarter projects is described in
`smarter-sh/community <https://github.com/smarter-sh/community>`__.
