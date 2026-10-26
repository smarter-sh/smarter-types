"""Test smarter_types.enum: SmarterEnumAbstract."""

import logging

import pytest

from smarter_types import SmarterEnumAbstract


class Colors(SmarterEnumAbstract):
    """An enumeration to test with."""

    RED = "Red"
    LIGHT_BLUE = "LightBlue"


def test_all_and_list_all():
    """The values, as a list and as one string."""
    assert Colors.all() == ["Red", "LightBlue"]
    assert Colors.list_all() == "Red, LightBlue"


def test_slugs():
    """Slugs are the values in lower case, singular then plural."""
    assert Colors.singular_slugs() == ["red", "lightblue"]
    assert Colors.plural_slugs() == ["reds", "lightblues"]
    assert Colors.all_slugs() == ["red", "lightblue", "reds", "lightblues"]


def test_str():
    """A member's str() is its value."""
    assert str(Colors.LIGHT_BLUE) == "LightBlue"


@pytest.mark.parametrize(
    ("url", "slug"),
    [
        ("http://localhost:9357/api/v1/cli/get/LightBlues/", "lightblues"),
        (b"http://localhost:9357/api/v1/cli/describe/red/", "red"),
        ("http://localhost:9357/red/", None),
        ("http://localhost:9357/api/v1/cli/whoami/red/", None),
        ("http://localhost:9357/api/v1/cli/status/", None),
        ("http://localhost:9357/api/v1/cli/version/", None),
    ],
)
def test_from_url(url, slug):
    """The first slug of an api url that is one of the enumeration's, except for whoami, status and version."""
    assert Colors.from_url(url) == slug


def test_from_url_without_slug(caplog):
    """An api url without a slug is None, and a warning."""
    with caplog.at_level(logging.WARNING, logger="smarter_types.enum"):
        assert Colors.from_url("http://localhost:9357/api/v1/cli/get/green/") is None
    assert "Colors.from_url()" in caplog.text
