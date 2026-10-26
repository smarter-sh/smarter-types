"""The base class of Smarter's enumerations."""

from __future__ import annotations

import logging
from enum import Enum
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SmarterEnumAbstract(Enum):
    """
    The base class of Smarter's enumerations, whose values are strings.

    It adds class methods that list the values, and the url slugs made from them. ``str()`` of a
    member is its value.

    .. code-block:: python

        from smarter_types import SAMKinds

        SAMKinds.all()  # ["Plugin", "ApiPlugin", ...]
        str(SAMKinds.SECRET)  # "Secret"
    """

    @classmethod
    def all(cls) -> list[str]:
        """
        Return every member's value.

        :returns: The values, in the order in which the members are defined.
        :rtype: list[str]
        """
        return [member.value for name, member in cls.__members__.items() if not name.startswith("_")]

    @classmethod
    def list_all(cls) -> str:
        """
        Return every member's value, as one comma-separated string, e.g. for an error message.

        :returns: The values, separated by ``", "``.
        :rtype: str
        """
        return ", ".join(cls.all())

    @classmethod
    def all_slugs(cls) -> list[str]:
        """
        Return the url slugs of every value, singular and plural.

        :returns: :meth:`singular_slugs`, then :meth:`plural_slugs`.
        :rtype: list[str]
        """
        return cls.singular_slugs() + cls.plural_slugs()

    @classmethod
    def singular_slugs(cls) -> list[str]:
        """
        Return the singular url slug of every value: the value, in lower case.

        :returns: The slugs, e.g. ``["plugin", "apiplugin", ...]``.
        :rtype: list[str]
        """
        return [slug.lower() for slug in cls.all()]

    @classmethod
    def plural_slugs(cls) -> list[str]:
        """
        Return the plural url slug of every value: the value, in lower case, with an ``s``.

        :returns: The slugs, e.g. ``["plugins", "apiplugins", ...]``.
        :rtype: list[str]
        """
        return [f"{slug.lower()}s" for slug in cls.all()]

    @classmethod
    def from_url(cls, url: str | bytes) -> str | None:
        """
        Return the first slug of a Smarter api url that is one of this enumeration's slugs.

        .. code-block:: python

            SAMKinds.from_url("http://localhost:9357/api/v1/cli/example_manifest/Account/")  # "account"
            SAMKinds.from_url("http://localhost:9357/api/v1/cli/whoami/")  # None

        :param url: The url.
        :type url: str | bytes
        :returns: The slug, in lower case, or None for a url that is not an api url, that is the
            ``whoami``, ``status`` or ``version`` endpoint, or that has none of the slugs.
        :rtype: str | None
        """
        if isinstance(url, bytes):
            url = url.decode("utf-8")
        slugs = urlparse(url).path.split("/")
        if "api" not in slugs:
            return None
        if "whoami" in slugs or "status" in slugs or "version" in slugs:
            return None
        all_slugs = cls.all_slugs()
        for slug in slugs:
            this_slug = str(slug).lower()
            if this_slug in all_slugs:
                return this_slug
        logger.warning("%s.from_url() could not extract manifest kind from URL: %s", cls.__name__, url)
        return None

    def __str__(self) -> str:
        """Return the member's value."""
        return str(self.value)


__all__ = ["SmarterEnumAbstract"]
