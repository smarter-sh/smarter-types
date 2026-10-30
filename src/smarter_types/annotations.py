"""
The rules of SAM annotations: what a valid key, value and set of annotations is, and how selectors are written.

A SAM manifest's ``metadata.annotations`` follow Kubernetes annotations: a map of string keys to
string values that any client or extension may attach to a resource, for its own purposes. A key
is an optional DNS-subdomain prefix that names its owner, e.g. ``acme.com``, then a slash and a
name, e.g. ``acme.com/crm-account-id``. Smarter's keys are a superset of Kubernetes keys: the name
may have several slash-separated segments, e.g. ``smarter.sh/llmclient/use-case``. Every valid
Kubernetes key is a valid Smarter key.

The platform enforces these rules when a manifest is applied, and a client, such as the Smarter
Python SDK, can check annotations and selectors with them before it sends a request.

.. code-block:: python

    from smarter_types import normalize_annotations, parse_annotation_requirement

    normalize_annotations({"acme.com/crm-account-id": "A-10042", "acme.com/active": True})
    # {"acme.com/crm-account-id": "A-10042", "acme.com/active": "true"}

    str(parse_annotation_requirement("acme.com/crm-account-id!=A-10042"))  # "acme.com/crm-account-id!=A-10042"
"""

from __future__ import annotations

import datetime
import decimal
import json
import re
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Union

from .enum import SmarterEnumAbstract
from .exceptions import SmarterTypesValueError

ANNOTATION_KEY_PREFIX_MAX_LENGTH = 253
"""The longest key prefix, a DNS subdomain such as ``acme.com``, as in Kubernetes."""

ANNOTATION_KEY_SEGMENT_MAX_LENGTH = 63
"""The longest segment of a key's name, the parts between slashes, as in Kubernetes."""

ANNOTATION_KEY_MAX_LENGTH = ANNOTATION_KEY_PREFIX_MAX_LENGTH + 1 + ANNOTATION_KEY_SEGMENT_MAX_LENGTH
"""The longest key, 317 characters: the longest key that Kubernetes accepts."""

ANNOTATIONS_TOTAL_MAX_BYTES = 256 * 1024
"""The most that one resource's annotations, keys and values together, may hold: 256 KiB, as in Kubernetes."""

RESERVED_ANNOTATION_PREFIXES = ("smarter.sh",)
"""
Key prefixes that belong to the Smarter platform, as ``kubernetes.io`` belongs to Kubernetes.

A prefix's subdomains are reserved too, e.g. ``llmclient.smarter.sh``. Manifests may carry
these keys, but only Smarter's own code acts on them.
"""

ANNOTATION_SELECTOR_PARAM = "annotation"
"""The query parameter of the cli ``get`` api that holds an annotation selector.

For example, ``?annotation=acme.com/crm-id=42``.
"""

_DNS_LABEL = r"[a-z0-9]([-a-z0-9]*[a-z0-9])?"
DNS_SUBDOMAIN_PATTERN = re.compile(rf"{_DNS_LABEL}(\.{_DNS_LABEL})*")
"""A DNS subdomain as Kubernetes defines it (RFC 1123): lowercase labels separated by dots.

Use ``fullmatch()``.
"""

NAME_SEGMENT_PATTERN = re.compile(r"([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9]")
"""A Kubernetes qualified name: alphanumeric at both ends, with ``-``, ``_`` and ``.`` between. Use ``fullmatch()``."""

AnnotationsMap = dict[str, str]
"""A resource's annotations: string keys mapped to string values, as in Kubernetes."""

AnnotationsInput = Union[None, str, dict[str, object], list[dict[str, object]]]
"""What :func:`normalize_annotations` accepts.

A map, the legacy list of one-key maps, either of them as a JSON string, or ``None``.
"""


def split_annotation_key(key: str) -> tuple[str | None, str]:
    """
    Split an annotation key into its prefix and its name.

    The prefix is everything before the first slash. A key without a slash has no prefix.

    .. code-block:: python

        split_annotation_key("acme.com/crm/account-id")  # ("acme.com", "crm/account-id")
        split_annotation_key("owner")  # (None, "owner")

    :param key: The annotation key.
    :type key: str
    :returns: The prefix, or None, and the name.
    :rtype: tuple[str | None, str]
    """
    if "/" in key:
        prefix, name = key.split("/", 1)
        return prefix, name
    return None, key


def validate_annotation_key(key: str) -> str:
    """
    Validate an annotation key, and return it.

    A key is ``[prefix/]name``. The prefix, when present, is a lowercase DNS subdomain of at most
    253 characters. The name is one or more segments separated by slashes. Each segment is at most
    63 characters, alphanumeric at both ends, with ``-``, ``_`` and ``.`` between. The whole key
    is at most 317 characters.

    .. code-block:: python

        validate_annotation_key("acme.com/crm-account-id")  # "acme.com/crm-account-id"
        validate_annotation_key("Acme.com/x")  # raises SmarterTypesValueError

    :param key: The annotation key.
    :type key: str
    :raises SmarterTypesValueError: If the key is not a non-empty string, or is not valid.
    :returns: The key.
    :rtype: str
    """
    if not isinstance(key, str) or not key:
        raise SmarterTypesValueError(f"Annotation keys must be non-empty strings, got {key!r}.")
    if len(key) > ANNOTATION_KEY_MAX_LENGTH:
        raise SmarterTypesValueError(
            f"Annotation key {key!r} is {len(key)} characters long. The limit is {ANNOTATION_KEY_MAX_LENGTH}."
        )
    prefix, name = split_annotation_key(key)
    if prefix is not None:
        if len(prefix) > ANNOTATION_KEY_PREFIX_MAX_LENGTH or not DNS_SUBDOMAIN_PATTERN.fullmatch(prefix):
            raise SmarterTypesValueError(
                f"Annotation key {key!r} has an invalid prefix {prefix!r}. A prefix must be a lowercase DNS "
                f"subdomain of at most {ANNOTATION_KEY_PREFIX_MAX_LENGTH} characters, e.g. 'acme.com'."
            )
    for segment in name.split("/"):
        if len(segment) > ANNOTATION_KEY_SEGMENT_MAX_LENGTH or not NAME_SEGMENT_PATTERN.fullmatch(segment):
            raise SmarterTypesValueError(
                f"Annotation key {key!r} has an invalid name segment {segment!r}. Each part of the name between "
                f"slashes must be 1 to {ANNOTATION_KEY_SEGMENT_MAX_LENGTH} characters, begin and end with a letter "
                "or digit, and contain only letters, digits, '-', '_' and '.'."
            )
    return key


def coerce_annotation_value(key: str, value: object, lenient: bool = False) -> str:
    """
    Return an annotation's value as a string.

    Annotation values are strings, as in Kubernetes. YAML parses unquoted scalars such as ``true``,
    ``42`` or ``2026-10-28`` as other types, so they are converted to the string that was written:
    booleans to ``"true"`` or ``"false"``, numbers and uuids with ``str()``, dates and datetimes to
    ISO 8601, UTF-8 bytes to their text, and None to ``""``.

    :param key: The annotation's key, for the error message.
    :type key: str
    :param value: The value.
    :type value: object
    :param lenient: Encode lists and dicts as JSON instead of rejecting them. Only for migrating
        legacy data.
    :type lenient: bool
    :raises SmarterTypesValueError: If the value is a list, a dict, bytes that aren't UTF-8, or any
        other type.
    :returns: The value as a string.
    :rtype: str
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, decimal.Decimal, uuid.UUID)):
        return str(value)
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError as e:
            raise SmarterTypesValueError(f"Annotation {key!r} has a bytes value that is not UTF-8.") from e
    if isinstance(value, (list, dict)) and lenient:
        return json.dumps(value, default=str)
    raise SmarterTypesValueError(
        f"Annotation {key!r} has a {type(value).__name__} value. Annotation values are strings: "
        "to store structured data, quote it as a JSON string."
    )


def annotations_size(annotations: AnnotationsMap) -> int:
    """
    Return the size of a resource's annotations in bytes: every key and value, UTF-8 encoded.

    :param annotations: The annotations.
    :type annotations: AnnotationsMap
    :returns: The size in bytes, which :data:`ANNOTATIONS_TOTAL_MAX_BYTES` limits.
    :rtype: int
    """
    return sum(len(key.encode("utf-8")) + len(value.encode("utf-8")) for key, value in annotations.items())


def normalize_annotations(value: AnnotationsInput, lenient: bool = False) -> AnnotationsMap:
    """
    Return annotations in any accepted shape as a validated map of strings to strings.

    Accepts the Kubernetes map, ``{"acme.com/crm-id": "42"}``, and the list of one-key maps that
    older SAM manifests use, ``[{"acme.com/crm-id": "42"}]``, or either one as a JSON string.
    Each key is checked with :func:`validate_annotation_key`, and each value converted with
    :func:`coerce_annotation_value`.

    .. code-block:: python

        normalize_annotations([{"acme.com/active": True}])  # {"acme.com/active": "true"}

    :param value: The annotations.
    :type value: AnnotationsInput
    :param lenient: Only for migrating legacy data: skip invalid keys and list items that aren't
        maps, keep the last value of a duplicate key, encode lists and dicts as JSON, and don't
        enforce the size limit.
    :type lenient: bool
    :raises SmarterTypesValueError: If the JSON can't be parsed, the shape is not a map or a list
        of maps, a key or value is invalid, a key appears twice, or the annotations are larger than
        :data:`ANNOTATIONS_TOTAL_MAX_BYTES`.
    :returns: The annotations, in their original order; empty for None or ``""``.
    :rtype: AnnotationsMap
    """
    if value is None or value == "":
        return {}
    parsed: object = value
    if isinstance(parsed, str):
        try:
            parsed = json.loads(parsed)
        except json.JSONDecodeError as e:
            raise SmarterTypesValueError(f"Annotations could not be parsed as JSON: {e}") from e
    pairs: list[tuple[object, object]]
    if isinstance(parsed, dict):
        pairs = list(parsed.items())
    elif isinstance(parsed, list):
        pairs = []
        for item in parsed:
            if not isinstance(item, dict):
                if lenient:
                    continue
                raise SmarterTypesValueError(
                    f"Each item of a list of annotations must be a key-value map, got {type(item).__name__}: {item!r}"
                )
            pairs.extend(item.items())
    else:
        raise SmarterTypesValueError(f"Annotations must be a map of keys to values, got {type(parsed).__name__}.")

    retval: AnnotationsMap = {}
    for key, item_value in pairs:
        try:
            valid_key = validate_annotation_key(key)  # type: ignore[arg-type]
            if valid_key in retval and not lenient:
                raise SmarterTypesValueError(f"Annotation key {valid_key!r} appears more than once.")
            retval[valid_key] = coerce_annotation_value(valid_key, item_value, lenient=lenient)
        except SmarterTypesValueError:
            if not lenient:
                raise
    if not lenient and annotations_size(retval) > ANNOTATIONS_TOTAL_MAX_BYTES:
        raise SmarterTypesValueError(
            f"Annotations are {annotations_size(retval)} bytes. The limit is {ANNOTATIONS_TOTAL_MAX_BYTES} bytes."
        )
    return retval


def prefix_matches(prefix: str | None, owner: str) -> bool:
    """
    Return whether a key's prefix is ``owner`` or one of its subdomains.

    .. code-block:: python

        prefix_matches("crm.acme.com", "acme.com")  # True
        prefix_matches("notacme.com", "acme.com")  # False

    :param prefix: A key's prefix, from :func:`split_annotation_key`.
    :type prefix: str | None
    :param owner: A DNS domain, e.g. ``acme.com``.
    :type owner: str
    :returns: True if the prefix belongs to the owner; False for no prefix.
    :rtype: bool
    """
    if not prefix:
        return False
    return prefix == owner or prefix.endswith("." + owner)


def is_reserved_annotation_key(key: str) -> bool:
    """
    Return whether a key belongs to the Smarter platform: its prefix is ``smarter.sh`` or one of its subdomains.

    :param key: The annotation key.
    :type key: str
    :returns: True if the key's prefix is one of :data:`RESERVED_ANNOTATION_PREFIXES`, or a subdomain of one.
    :rtype: bool
    """
    prefix, _ = split_annotation_key(key)
    return any(prefix_matches(prefix, reserved) for reserved in RESERVED_ANNOTATION_PREFIXES)


class AnnotationOperator(SmarterEnumAbstract):
    """How an :class:`AnnotationRequirement` tests a resource's annotation."""

    EXISTS = "exists"
    """The resource has the key, with any value: ``key``."""

    NOT_EXISTS = "not_exists"
    """The resource doesn't have the key: ``!key``."""

    EQUALS = "equals"
    """The resource has the key, with the value: ``key=value``."""

    NOT_EQUALS = "not_equals"
    """The resource doesn't have the key, or has another value: ``key!=value``, as in Kubernetes."""


@dataclass(frozen=True)
class AnnotationRequirement:
    """
    One requirement of an annotation selector, in the syntax of Kubernetes label selectors.

    ============================  ==============================================
    Selector                      Matches resources whose annotation
    ============================  ==============================================
    ``acme.com/crm-id``           ``acme.com/crm-id`` exists, with any value
    ``!acme.com/crm-id``          ``acme.com/crm-id`` doesn't exist
    ``acme.com/crm-id=A-10042``   ``acme.com/crm-id`` is ``A-10042``
    ``acme.com/crm-id!=A-10042``  ``acme.com/crm-id`` is missing, or isn't ``A-10042``
    ============================  ==============================================

    ``str()`` of a requirement is the selector text it is parsed from, so it can be sent as the
    :data:`ANNOTATION_SELECTOR_PARAM` query parameter.

    :param key: The annotation key.
    :type key: str
    :param operator: How the annotation is tested.
    :type operator: AnnotationOperator
    :param value: The value, for :attr:`AnnotationOperator.EQUALS` and
        :attr:`AnnotationOperator.NOT_EQUALS`; otherwise None.
    :type value: str | None
    """

    key: str
    operator: AnnotationOperator
    value: str | None = None

    def __str__(self) -> str:
        """Return the requirement as selector text, e.g. ``acme.com/crm-id!=A-10042``."""
        if self.operator is AnnotationOperator.EXISTS:
            return self.key
        if self.operator is AnnotationOperator.NOT_EXISTS:
            return "!" + self.key
        if self.operator is AnnotationOperator.EQUALS:
            return f"{self.key}={self.value}"
        return f"{self.key}!={self.value}"


AnnotationSelector = Union[None, str, Iterable[Union[str, AnnotationRequirement]]]
"""What :func:`parse_annotation_selector` accepts: one requirement, a list of them, or ``None`` for none."""


def parse_annotation_requirement(requirement: str) -> AnnotationRequirement:
    """
    Parse one requirement of an annotation selector, e.g. ``acme.com/crm-id=A-10042``.

    The text is stripped of surrounding whitespace, and so is the key. The value is everything
    after the first ``=``, and may itself contain ``=``, ``!`` and commas. ``key==value`` is the
    same as ``key=value``.

    .. code-block:: python

        parse_annotation_requirement("!acme.com/archived")
        # AnnotationRequirement(key="acme.com/archived", operator=AnnotationOperator.NOT_EXISTS, value=None)

    :param requirement: ``key``, ``!key``, ``key=value``, ``key==value`` or ``key!=value``.
    :type requirement: str
    :raises SmarterTypesValueError: If the requirement is empty, or its key is invalid.
    :returns: The requirement.
    :rtype: AnnotationRequirement
    """
    text = requirement.strip()
    if not text:
        raise SmarterTypesValueError("An annotation selector requirement can't be empty.")
    if text.startswith("!"):
        return AnnotationRequirement(
            key=validate_annotation_key(text[1:].strip()), operator=AnnotationOperator.NOT_EXISTS
        )
    equals = text.find("=")
    if equals < 0:
        return AnnotationRequirement(key=validate_annotation_key(text), operator=AnnotationOperator.EXISTS)
    value_start = equals + 1
    value = text[value_start:]
    if equals > 0 and text[equals - 1] == "!":
        return AnnotationRequirement(
            key=validate_annotation_key(text[: equals - 1].strip()), operator=AnnotationOperator.NOT_EQUALS, value=value
        )
    if value.startswith("="):
        value = value[1:]
    return AnnotationRequirement(
        key=validate_annotation_key(text[:equals].strip()), operator=AnnotationOperator.EQUALS, value=value
    )


def parse_annotation_selector(selector: AnnotationSelector) -> list[AnnotationRequirement]:
    """
    Parse an annotation selector into its requirements, all of which a resource must match.

    Values are free text and may contain commas, so a selector is a list of requirements, not one
    comma-separated string. Blank strings in the list are skipped.

    :param selector: One requirement, a list of requirements as text or as
        :class:`AnnotationRequirement`, or None.
    :type selector: AnnotationSelector
    :raises SmarterTypesValueError: If a requirement is invalid.
    :returns: The requirements; empty for None.
    :rtype: list[AnnotationRequirement]
    """
    if selector is None:
        return []
    if isinstance(selector, str):
        selector = [selector]
    return [
        item if isinstance(item, AnnotationRequirement) else parse_annotation_requirement(item)
        for item in selector
        if isinstance(item, AnnotationRequirement) or (isinstance(item, str) and item.strip())
    ]


__all__ = [
    "ANNOTATIONS_TOTAL_MAX_BYTES",
    "ANNOTATION_KEY_MAX_LENGTH",
    "ANNOTATION_KEY_PREFIX_MAX_LENGTH",
    "ANNOTATION_KEY_SEGMENT_MAX_LENGTH",
    "ANNOTATION_SELECTOR_PARAM",
    "DNS_SUBDOMAIN_PATTERN",
    "NAME_SEGMENT_PATTERN",
    "RESERVED_ANNOTATION_PREFIXES",
    "AnnotationOperator",
    "AnnotationRequirement",
    "AnnotationSelector",
    "AnnotationsInput",
    "AnnotationsMap",
    "annotations_size",
    "coerce_annotation_value",
    "is_reserved_annotation_key",
    "normalize_annotations",
    "parse_annotation_requirement",
    "parse_annotation_selector",
    "prefix_matches",
    "split_annotation_key",
    "validate_annotation_key",
]
