"""Test smarter_types.annotations: the rules of SAM annotations and annotation selectors."""

import datetime
import decimal
import uuid

import pytest

from smarter_types import (
    AnnotationOperator,
    AnnotationRequirement,
    SmarterTypesValueError,
    normalize_annotations,
    parse_annotation_requirement,
    parse_annotation_selector,
    validate_annotation_key,
)
from smarter_types.annotations import (
    ANNOTATION_KEY_MAX_LENGTH,
    ANNOTATION_KEY_PREFIX_MAX_LENGTH,
    ANNOTATION_KEY_SEGMENT_MAX_LENGTH,
    ANNOTATION_SELECTOR_PARAM,
    ANNOTATIONS_TOTAL_MAX_BYTES,
    RESERVED_ANNOTATION_PREFIXES,
    annotations_size,
    coerce_annotation_value,
    is_reserved_annotation_key,
    prefix_matches,
    split_annotation_key,
)

VALID_KEYS = (
    "owner",
    "acme.com/crm-account-id",
    "smarter.sh/llmclient/use-case",
    "smarter.sh/created_by",
    "app.kubernetes.io/name",
    "a/b.c_d-e",
    "x" * 63,
    "a" * 253 + "/" + "b" * 63,
    "1.2.3/4",
    "a/B",
)
INVALID_KEYS = (
    "",
    "/name",
    "acme.com/",
    "Acme.com/name",
    "acme_corp.com/name",
    "acme.com/-name",
    "acme.com/name-",
    "acme.com/a//b",
    "acme.com/has space",
    "acme.com/" + "x" * 64,
    "a" * 254 + "/name",
    "x" * (ANNOTATION_KEY_MAX_LENGTH + 1),
    "-acme.com/name",
    "acme..com/name",
    "acme.com/name/",
    "acme.com/name\n",
    "acme.com\n/name",
    "acme.com/na:me",
)


def test_limits():
    """The limits are Kubernetes', and the reserved prefix and query parameter are Smarter's."""
    assert ANNOTATION_KEY_PREFIX_MAX_LENGTH == 253
    assert ANNOTATION_KEY_SEGMENT_MAX_LENGTH == 63
    assert ANNOTATION_KEY_MAX_LENGTH == 317
    assert ANNOTATIONS_TOTAL_MAX_BYTES == 262144
    assert RESERVED_ANNOTATION_PREFIXES == ("smarter.sh",)
    assert ANNOTATION_SELECTOR_PARAM == "annotation"


@pytest.mark.parametrize("key", VALID_KEYS)
def test_valid_keys(key):
    """Every Kubernetes key, and Smarter's multi-segment keys, are valid."""
    assert validate_annotation_key(key) == key


@pytest.mark.parametrize("key", INVALID_KEYS)
def test_invalid_keys(key):
    """Malformed prefixes, segments, lengths and trailing newlines are rejected."""
    with pytest.raises(SmarterTypesValueError):
        validate_annotation_key(key)


@pytest.mark.parametrize("key", [42, None, b"acme.com/x"])
def test_non_string_key(key):
    """A key that isn't a string is rejected, as a ValueError too."""
    with pytest.raises(ValueError):
        validate_annotation_key(key)


def test_split_annotation_key():
    """The prefix is everything before the first slash."""
    assert split_annotation_key("acme.com/crm/id") == ("acme.com", "crm/id")
    assert split_annotation_key("owner") == (None, "owner")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("text", "text"),
        ("", ""),
        (True, "true"),
        (False, "false"),
        (42, "42"),
        (0, "0"),
        (1.5, "1.5"),
        (decimal.Decimal("4.00"), "4.00"),
        (datetime.date(2026, 10, 28), "2026-10-28"),
        (datetime.datetime(2026, 10, 28, 12, 30), "2026-10-28T12:30:00"),
        (uuid.UUID(int=1), "00000000-0000-0000-0000-000000000001"),
        (b"bytes", "bytes"),
        (None, ""),
    ],
)
def test_coerce_scalars(value, expected):
    """YAML's unquoted scalars become the strings that were written."""
    assert coerce_annotation_value("k", value) == expected


@pytest.mark.parametrize("value", [[1, 2], {"a": 1}, b"\xff", (1, 2), object()])
def test_coerce_rejects_structures(value):
    """Lists, dicts, non-UTF-8 bytes and other types are rejected."""
    with pytest.raises(SmarterTypesValueError):
        coerce_annotation_value("k", value)


def test_coerce_lenient():
    """Lenient coercion keeps lists and dicts as JSON, for legacy data."""
    assert coerce_annotation_value("k", [1, 2], lenient=True) == "[1, 2]"
    assert coerce_annotation_value("k", {"a": 1}, lenient=True) == '{"a": 1}'


@pytest.mark.parametrize(
    "value",
    [
        {"acme.com/id": "A-1", "acme.com/active": True},
        [{"acme.com/id": "A-1"}, {"acme.com/active": True}],
        [{"acme.com/id": "A-1", "acme.com/active": True}],
        '{"acme.com/id": "A-1", "acme.com/active": true}',
        '[{"acme.com/id": "A-1"}, {"acme.com/active": true}]',
    ],
)
def test_normalize_shapes(value):
    """A map, the legacy list of one-key maps, and their JSON are the same annotations."""
    assert normalize_annotations(value) == {"acme.com/id": "A-1", "acme.com/active": "true"}


def test_normalize_keeps_order():
    """Normalized annotations keep the order in which they were written."""
    assert list(normalize_annotations([{"b.com/x": "1"}, {"a.com/x": "2"}])) == ["b.com/x", "a.com/x"]


@pytest.mark.parametrize("value", [None, "", [], {}, "{}", "[]"])
def test_normalize_empty(value):
    """None, an empty string, list and map are no annotations."""
    assert normalize_annotations(value) == {}


@pytest.mark.parametrize(
    "value",
    [
        "not json",
        "42",
        42,
        ["not a map"],
        {"Bad Key": "x"},
        {42: "x"},
        [{"acme.com/id": "1"}, {"acme.com/id": "2"}],
        {"acme.com/id": ["a", "list"]},
        {"acme.com/id": {"a": "map"}},
    ],
)
def test_normalize_errors(value):
    """Bad JSON, shapes, keys, duplicates and values are rejected."""
    with pytest.raises(SmarterTypesValueError):
        normalize_annotations(value)


def test_normalize_lenient():
    """Legacy data keeps what it can: valid keys, the last duplicate, structures as JSON."""
    value = [{"acme.com/id": "1"}, {"acme.com/id": "2"}, {"Bad Key": "x"}, "junk", {"acme.com/list": [1]}]
    assert normalize_annotations(value, lenient=True) == {"acme.com/id": "2", "acme.com/list": "[1]"}


def test_size_limit():
    """All annotations together are limited to 256 KiB of UTF-8, as in Kubernetes."""
    too_big = {"acme.com/big": "x" * ANNOTATIONS_TOTAL_MAX_BYTES}
    with pytest.raises(SmarterTypesValueError):
        normalize_annotations(too_big)
    assert len(normalize_annotations(too_big, lenient=True)["acme.com/big"]) == ANNOTATIONS_TOTAL_MAX_BYTES
    just_fits = {"k": "x" * (ANNOTATIONS_TOTAL_MAX_BYTES - 1)}
    assert normalize_annotations(just_fits) == just_fits
    assert annotations_size({"ab": "cd"}) == 4
    assert annotations_size({"k": "é"}) == 3


def test_prefix_matches():
    """A prefix matches its domain and subdomains, and nothing else."""
    assert prefix_matches("acme.com", "acme.com")
    assert prefix_matches("crm.acme.com", "acme.com")
    assert not prefix_matches("notacme.com", "acme.com")
    assert not prefix_matches(None, "acme.com")
    assert not prefix_matches("", "acme.com")


def test_reserved_keys():
    """Keys with the prefix smarter.sh, or a subdomain of it, are reserved."""
    assert is_reserved_annotation_key("smarter.sh/llmclient/use-case")
    assert is_reserved_annotation_key("llmclient.smarter.sh/x")
    assert not is_reserved_annotation_key("acme.com/x")
    assert not is_reserved_annotation_key("smarter.sh")
    assert not is_reserved_annotation_key("notsmarter.sh/x")


def test_operator_values():
    """The operators' values are the platform's, so they are promises."""
    assert AnnotationOperator.all() == ["exists", "not_exists", "equals", "not_equals"]
    assert AnnotationOperator("not_equals") is AnnotationOperator.NOT_EQUALS


@pytest.mark.parametrize(
    ("text", "operator", "value"),
    [
        ("acme.com/id", AnnotationOperator.EXISTS, None),
        (" !acme.com/id ", AnnotationOperator.NOT_EXISTS, None),
        ("! acme.com/id", AnnotationOperator.NOT_EXISTS, None),
        ("acme.com/id=A=1, 2", AnnotationOperator.EQUALS, "A=1, 2"),
        ("acme.com/id==x", AnnotationOperator.EQUALS, "x"),
        ("acme.com/id!=!x", AnnotationOperator.NOT_EQUALS, "!x"),
        ("acme.com/id=", AnnotationOperator.EQUALS, ""),
        ("acme.com/id!=", AnnotationOperator.NOT_EQUALS, ""),
        ("acme.com/id = x", AnnotationOperator.EQUALS, " x"),
    ],
)
def test_parse(text, operator, value):
    """Each operator parses, and values may contain '=', '!', commas and spaces."""
    requirement = parse_annotation_requirement(text)
    assert (requirement.key, requirement.operator, requirement.value) == ("acme.com/id", operator, value)


@pytest.mark.parametrize("text", ["acme.com/id", "!acme.com/id", "acme.com/id=x", "acme.com/id!=x"])
def test_str_round_trips(text):
    """A requirement prints as the selector it was parsed from."""
    assert str(parse_annotation_requirement(text)) == text


@pytest.mark.parametrize("text", ["", "  ", "Bad Key=x", "!", "=x", "!=x", "!!acme.com/id"])
def test_parse_errors(text):
    """An empty requirement or an invalid key is rejected."""
    with pytest.raises(SmarterTypesValueError):
        parse_annotation_requirement(text)


def test_requirement_is_frozen():
    """A requirement is immutable, and equal to another with the same fields."""
    requirement = AnnotationRequirement(key="acme.com/id", operator=AnnotationOperator.EXISTS)
    assert requirement == parse_annotation_requirement("acme.com/id")
    with pytest.raises(AttributeError):
        requirement.key = "other"  # type: ignore[misc]


def test_parse_selector():
    """A selector is None, a string, or a list of strings and requirements, with blanks skipped."""
    requirement = AnnotationRequirement(key="acme.com/id", operator=AnnotationOperator.EXISTS)
    assert parse_annotation_selector(None) == []
    assert parse_annotation_selector("acme.com/id") == [requirement]
    assert parse_annotation_selector(["", requirement]) == [requirement]
    assert parse_annotation_selector(("acme.com/id=a,b", "  ", "!acme.com/x")) == [
        AnnotationRequirement(key="acme.com/id", operator=AnnotationOperator.EQUALS, value="a,b"),
        AnnotationRequirement(key="acme.com/x", operator=AnnotationOperator.NOT_EXISTS),
    ]
    with pytest.raises(SmarterTypesValueError):
        parse_annotation_selector(["acme.com/id", "Bad Key"])
