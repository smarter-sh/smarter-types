smarter-types |project_version|
===============================

.. image:: https://img.shields.io/badge/a%20project%20of-The%20Smarter%20Project-2F6FEB
   :target: https://smarter.sh
   :alt: A project of The Smarter Project

.. image:: https://github.com/smarter-sh/smarter-types/actions/workflows/release.yml/badge.svg?branch=main
   :target: https://github.com/smarter-sh/smarter-types/actions/workflows/release.yml
   :alt: Release

.. image:: https://codecov.io/gh/smarter-sh/smarter-types/graph/badge.svg
   :target: https://codecov.io/gh/smarter-sh/smarter-types
   :alt: Coverage

.. image:: https://img.shields.io/pypi/v/smarter-types?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/smarter-types/
   :alt: PyPI

.. image:: https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white
   :alt: Python 3.10+

.. image:: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
   :target: https://github.com/smarter-sh/smarter-types/blob/main/LICENSE.txt
   :alt: AGPL-3.0-or-later

|

**smarter-types** holds the plain-Python type definitions that the
`Smarter <https://github.com/smarter-sh/smarter>`__ platform and its
`Python SDK <https://github.com/smarter-sh/smarter-python>`__ use together.
It provides shared definitions for Smarter Application Manifest (SAM) kinds,
their apply order, the Smarter Journal's things and cli commands, and the
rules of SAM annotations.

These definitions give the platform and SDK a consistent contract while
keeping the package usable in plain Python, without Django.

.. code-block:: python

    from smarter_types import SAMKinds

    SAMKinds.str_to_kind("sqlplugin")  # "SqlPlugin"
    SAMKinds.plural(SAMKinds.API_CONNECTION)  # "ApiConnections"

    # apply a set of manifests so that each resource comes after the ones it names.
    manifests.sort(key=lambda m: SAMKinds.apply_rank(m["kind"]))

Features
--------

- **SAMKinds**, the single source of truth for which SAM kinds exist.
- **The apply order**: :meth:`~smarter_types.kinds.SAMKinds.apply_order` and
  :meth:`~smarter_types.kinds.SAMKinds.apply_rank` sort a set of manifests so
  that every resource is applied after the resources it names.
- **The Smarter Journal's enumerations**: the things it records, whose values
  come from SAMKinds, and the verbs of the ``/api/v1/cli/`` api.
- **SAM annotations**: the rules of a valid annotation key and value, the
  legacy list form, the size limit, and annotation selectors
  (:doc:`guide/annotations`).
- **Plain Python**: no Django, no Pydantic. Its only dependency is
  ``inflection``. Typed (``py.typed``).

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/why
   guide/kinds
   guide/journal
   guide/annotations

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference

.. toctree::
   :maxdepth: 1
   :caption: Project

   project/changelog
   project/contributing
   project/license
   adr

Indices
-------

- :ref:`genindex`
- :ref:`modindex`
- :ref:`search`
