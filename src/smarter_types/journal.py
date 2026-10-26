"""
The enumerations of the Smarter Journal: the record of every request to the Smarter api.

Each journal entry records the *thing* that a request was about, from :class:`SmarterJournalThings`,
and the *command* that it ran, from :class:`SmarterJournalCliCommands`. Every SAM kind is a thing,
so :class:`SmarterJournalThings` takes its kinds from :class:`~smarter_types.kinds.SAMKinds`.
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

from .enum import SmarterEnumAbstract
from .kinds import SAMKinds

logger = logging.getLogger(__name__)


class SmarterJournalApiResponseKeys:
    """The keys of a journaled response of the Smarter api."""

    API = "api"
    THING = "thing"
    METADATA = "metadata"
    DATA = "data"
    ERROR = "error"
    MESSAGE = "message"


class SmarterJournalApiResponseErrorKeys:
    """The keys of the ``error`` of a journaled response of the Smarter api."""

    ERROR_CLASS = "errorClass"
    STACK_TRACE = "stacktrace"
    DESCRIPTION = "description"
    STATUS = "status"
    ARGS = "args"
    CAUSE = "cause"
    CONTEXT = "context"
    THING = "thing"
    COMMAND = "command"


class SCLIResponseMetadata:
    """The keys of the ``metadata`` of a journaled response of the cli api's ``get`` command."""

    KEY = "key"
    COMMAND = "command"


class SmarterJournalThings(SmarterEnumAbstract):
    """
    The kinds of objects ("things") that the Smarter Journal records requests about.

    Every SAM kind is a thing, with the same value. The one thing that is not a SAM kind is
    :attr:`PROMPT_CONFIG`, a chat's configuration, which the platform generates on request.

    .. code-block:: python

        thing = SmarterJournalThings("Plugin")
        assert thing == SmarterJournalThings.STATIC_PLUGIN
        assert thing.value == SAMKinds.STATIC_PLUGIN.value
    """

    ACCOUNT = SAMKinds.ACCOUNT.value
    API_PLUGIN = SAMKinds.API_PLUGIN.value
    AUTH_TOKEN = SAMKinds.AUTH_TOKEN.value
    API_CONNECTION = SAMKinds.API_CONNECTION.value
    BUDGET = SAMKinds.BUDGET.value
    CUSTOM_DOMAIN = SAMKinds.CUSTOM_DOMAIN.value
    GUARDRAIL = SAMKinds.GUARDRAIL.value
    IMAGE_SEARCH_PLUGIN = SAMKinds.IMAGE_SEARCH_PLUGIN.value
    LLM_CLIENT = SAMKinds.LLM_CLIENT.value
    LLMHOST = SAMKinds.LLM_HOST.value
    LLMHOST_COMPUTE = SAMKinds.LLM_HOST_COMPUTE.value
    MCPCLIENT = SAMKinds.MCP_CLIENT.value
    ORCHESTRATOR = SAMKinds.ORCHESTRATOR.value
    PROMPT = SAMKinds.PROMPT.value
    PROVIDER = SAMKinds.PROVIDER.value
    PROXY = SAMKinds.PROXY.value
    SECRET = SAMKinds.SECRET.value
    SQL_CONNECTION = SAMKinds.SQL_CONNECTION.value
    SKILL_PLUGIN = SAMKinds.SKILL_PLUGIN.value
    SQL_PLUGIN = SAMKinds.SQL_PLUGIN.value
    STATIC_PLUGIN = SAMKinds.STATIC_PLUGIN.value
    USER = SAMKinds.USER.value
    VECTORSEARCH = SAMKinds.VECTORSEARCH.value
    VECTORSTORE = SAMKinds.VECTORSTORE.value
    WEBSEARCH_PLUGIN = SAMKinds.WEBSEARCH_PLUGIN.value

    PROMPT_CONFIG = "ChatConfig"
    """A chat's configuration: a JSON object that the platform generates on request.

    Not a SAM kind.
    """

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """
        Return the choices of the platform's journal model's ``thing`` field, as Django expects them.

        The list is part of the platform's database migrations, so it changes only with a migration.
        It doesn't have ``LLMHost`` or ``LLMHostCompute``.

        :returns: ``(value, label)`` pairs.
        :rtype: list[tuple[str, str]]
        """
        return [
            (cls.ACCOUNT.value, cls.ACCOUNT.value),
            (cls.API_CONNECTION.value, cls.API_CONNECTION.value),
            (cls.API_PLUGIN.value, cls.API_PLUGIN.value),
            (cls.AUTH_TOKEN.value, cls.AUTH_TOKEN.value),
            (cls.BUDGET.value, cls.BUDGET.value),
            (cls.CUSTOM_DOMAIN.value, cls.CUSTOM_DOMAIN.value),
            (cls.GUARDRAIL.value, cls.GUARDRAIL.value),
            (cls.IMAGE_SEARCH_PLUGIN.value, cls.IMAGE_SEARCH_PLUGIN.value),
            (cls.LLM_CLIENT.value, cls.LLM_CLIENT.value),
            (cls.MCPCLIENT.value, cls.MCPCLIENT.value),
            (cls.ORCHESTRATOR.value, cls.ORCHESTRATOR.value),
            (cls.PROMPT.value, cls.PROMPT.value),
            (cls.PROMPT_CONFIG.value, cls.PROMPT_CONFIG.value),
            (cls.PROXY.value, cls.PROXY.value),
            (cls.PROVIDER.value, cls.PROVIDER.value),
            (cls.SECRET.value, cls.SECRET.value),
            (cls.SKILL_PLUGIN.value, cls.SKILL_PLUGIN.value),
            (cls.SQL_CONNECTION.value, cls.SQL_CONNECTION.value),
            (cls.SQL_PLUGIN.value, cls.SQL_PLUGIN.value),
            (cls.STATIC_PLUGIN.value, cls.STATIC_PLUGIN.value),
            (cls.USER.value, cls.USER.value),
            (cls.VECTORSEARCH.value, cls.VECTORSEARCH.value),
            (cls.VECTORSTORE.value, cls.VECTORSTORE.value),
            (cls.WEBSEARCH_PLUGIN.value, cls.WEBSEARCH_PLUGIN.value),
        ]


class SmarterJournalCliCommands(SmarterEnumAbstract):
    """
    The commands of the Smarter api's ``/api/v1/cli/`` endpoints, which the journal records.

    .. code-block:: python

        command = SmarterJournalCliCommands("apply")
        assert command == SmarterJournalCliCommands.APPLY
    """

    APPLY = "apply"
    DELETE = "delete"
    DEPLOY = "deploy"
    DESCRIBE = "describe"
    ENABLE_JOURNAL = "journal"  # FIXNOTE: THIS IS AMBIGUOUS
    GET = "get"
    JSON_SCHEMA = "json_schema"
    LOGS = "logs"  # FIXNOTE: THIS IS AMBIGUOUS
    MANIFEST_EXAMPLE = "example_manifest"
    PROMPT = "prompt"
    PROMPT_CONFIG = "chat_config"
    STATUS = "status"
    UNDEPLOY = "undeploy"
    VALIDATE = "validate"
    VERSION = "version"
    WHOAMI = "whoami"
    RESOURCES = "resources"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """
        Return the choices of the platform's journal model's ``command`` field, as Django expects them.

        The list is part of the platform's database migrations, so it changes only with a migration.

        :returns: ``(value, label)`` pairs.
        :rtype: list[tuple[str, str]]
        """
        return [
            (cls.APPLY.value, cls.APPLY.value),
            (cls.PROMPT.value, cls.PROMPT.value),
            (cls.PROMPT_CONFIG.value, cls.PROMPT_CONFIG.value),
            (cls.DELETE.value, cls.DELETE.value),
            (cls.DEPLOY.value, cls.DEPLOY.value),
            (cls.DESCRIBE.value, cls.DESCRIBE.value),
            (cls.GET.value, cls.GET.value),
            (cls.ENABLE_JOURNAL.value, cls.ENABLE_JOURNAL.value),
            (cls.LOGS.value, cls.LOGS.value),
            (cls.MANIFEST_EXAMPLE.value, cls.MANIFEST_EXAMPLE.value),
            (cls.STATUS.value, cls.STATUS.value),
            (cls.JSON_SCHEMA.value, cls.JSON_SCHEMA.value),
            (cls.VERSION.value, cls.VERSION.value),
            (cls.UNDEPLOY.value, cls.UNDEPLOY.value),
            (cls.VALIDATE.value, cls.VALIDATE.value),
            (cls.WHOAMI.value, cls.WHOAMI.value),
            (cls.RESOURCES.value, cls.RESOURCES.value),
        ]

    @classmethod
    def past_tense(cls) -> dict[str, str]:
        """
        Return the past tense of each command, for the messages of journaled responses.

        :returns: The past tense, by command value, e.g. ``{"apply": "applied", ...}``.
        :rtype: dict[str, str]
        """
        return {
            cls.APPLY.value: "applied",
            cls.PROMPT.value: "prompted",
            cls.PROMPT_CONFIG.value: "fetched chat_config",
            cls.DELETE.value: "deleted",
            cls.DEPLOY.value: "deployed",
            cls.DESCRIBE.value: "described",
            cls.GET.value: "got",
            cls.ENABLE_JOURNAL.value: "journaled",
            cls.LOGS.value: "logged",
            cls.MANIFEST_EXAMPLE.value: "fetched example manifest",
            cls.STATUS.value: "fetched status",
            cls.JSON_SCHEMA.value: "fetched json schema",
            cls.VERSION.value: "fetched version",
            cls.UNDEPLOY.value: "undeployed",
            cls.VALIDATE.value: "validated",
            cls.WHOAMI.value: "fetched identity",
            cls.RESOURCES.value: "fetched resources",
        }

    @classmethod
    def from_url(cls, url: str | bytes) -> str | None:
        """
        Return the command of a Smarter api url.

        .. code-block:: python

            SmarterJournalCliCommands.from_url("http://localhost:9357/api/v1/cli/example_manifest/Account/")
            # "example_manifest"

        :param url: The url.
        :type url: str | bytes
        :returns: The first slug of the url's path that is a command, or None for a url that is not
            an api url, or that has no command.
        :rtype: str | None
        """
        if isinstance(url, bytes):
            url = url.decode("utf-8")
        slugs = urlparse(url).path.split("/")
        if "api" not in slugs:
            return None
        commands = cls.all()
        for slug in slugs:
            this_slug = str(slug).lower()
            if this_slug in commands:
                return this_slug
        logger.warning("SmarterJournalCliCommands.from_url() could not extract a command from URL: %s", url)
        return None


__all__ = [
    "SCLIResponseMetadata",
    "SmarterJournalApiResponseErrorKeys",
    "SmarterJournalApiResponseKeys",
    "SmarterJournalCliCommands",
    "SmarterJournalThings",
]
