"""
Smarter-types: the types that the Smarter platform and its Python SDK share.

.. code-block:: python

    from smarter_types import SAMKinds

    sorted(manifests, key=lambda m: SAMKinds.apply_rank(m["kind"]))

See https://docs.smarter-types.smarter.sh/
"""

from .__version__ import __version__
from .annotations import (
    AnnotationOperator,
    AnnotationRequirement,
    normalize_annotations,
    parse_annotation_requirement,
    parse_annotation_selector,
    validate_annotation_key,
)
from .enum import SmarterEnumAbstract
from .exceptions import SmarterTypesError, SmarterTypesValueError
from .journal import (
    SCLIResponseMetadata,
    SmarterJournalApiResponseErrorKeys,
    SmarterJournalApiResponseKeys,
    SmarterJournalCliCommands,
    SmarterJournalThings,
)
from .kinds import SAMKinds

__all__ = [
    "AnnotationOperator",
    "AnnotationRequirement",
    "SAMKinds",
    "SCLIResponseMetadata",
    "SmarterEnumAbstract",
    "SmarterJournalApiResponseErrorKeys",
    "SmarterJournalApiResponseKeys",
    "SmarterJournalCliCommands",
    "SmarterJournalThings",
    "SmarterTypesError",
    "SmarterTypesValueError",
    "__version__",
    "normalize_annotations",
    "parse_annotation_requirement",
    "parse_annotation_selector",
    "validate_annotation_key",
]
