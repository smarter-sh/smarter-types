"""
The kinds of Smarter Application Manifest (SAM).

:class:`SAMKinds` is the single definition of which kinds exist. The Smarter platform, its Python
SDK and every other enumeration of kinds, such as
:class:`~smarter_types.journal.SmarterJournalThings`, take their kinds from it.
"""

from __future__ import annotations

import re

import inflection

from .enum import SmarterEnumAbstract
from .exceptions import SmarterTypesValueError


class SAMKinds(SmarterEnumAbstract):
    """
    Every Smarter Application Manifest (SAM) kind, as it appears in a manifest's ``kind``.

    Each value is the name of a kind of resource that a manifest declares, and that the platform
    validates, applies and routes to the kind's broker. The members' names are the kinds' names in
    upper snake case, except that a static plugin's kind is ``Plugin``, and an api key's is
    ``SmarterAuthToken``.

    .. code-block:: python

        from smarter_types import SAMKinds

        SAMKinds.LLM_CLIENT.value  # "LLMClient"
        SAMKinds("Secret") is SAMKinds.SECRET  # True
        SAMKinds.str_to_kind("sqlplugin")  # "SqlPlugin"

    A new kind is added here first, with a deliberate place in :meth:`apply_order`, and the tests fail
    until it has one.
    """

    # plugins
    STATIC_PLUGIN = "Plugin"
    """A static plugin: a tool whose results are fixed in its manifest."""

    API_PLUGIN = "ApiPlugin"
    """A plugin that calls a web api through an ApiConnection."""

    SKILL_PLUGIN = "SkillPlugin"
    """A plugin that gives the LLM a skill: instructions and files that it loads when it needs them."""

    SQL_PLUGIN = "SqlPlugin"
    """A plugin that queries a database through a SqlConnection."""

    WEBSEARCH_PLUGIN = "WebsearchPlugin"
    """A plugin that searches the web.

    Experimental.
    """

    IMAGE_SEARCH_PLUGIN = "ImageSearchPlugin"
    """A plugin that searches for images.

    Experimental.
    """

    # connections
    API_CONNECTION = "ApiConnection"
    """The url and credentials of a web api, which ApiPlugins call."""

    SQL_CONNECTION = "SqlConnection"
    """The address and credentials of a database, which SqlPlugins query."""

    # account resources
    ACCOUNT = "Account"
    """An account: the owner of every other resource."""

    AUTH_TOKEN = "SmarterAuthToken"
    """A Smarter api key."""

    BUDGET = "Budget"
    """Spending limits, enforced on the resources that it lists."""

    USER = "User"
    """A user, a member of an account."""

    SECRET = "Secret"
    """An encrypted value, such as a password or an api key, that other resources name."""

    GUARDRAIL = "Guardrail"
    """Rules that an LLMClient's prompts and responses are checked against."""

    # prompt resources
    PROMPT = "Prompt"
    """A chat session with an LLMClient."""

    LLM_CLIENT = "LLMClient"
    """An LLM application: its provider, model, system prompt, tools and guardrails."""

    CUSTOM_DOMAIN = "CustomDomain"
    """A domain that serves LLMClients."""

    LLM_HOST = "LLMHost"
    """A self-hosted model."""

    LLM_HOST_COMPUTE = "LLMHostCompute"
    """A kind of node, and its node group, that LLMHosts run on."""

    MCP_CLIENT = "MCPClient"
    """A connection to an MCP server, whose tools LLMClients may call."""

    ORCHESTRATOR = "Orchestrator"
    """A workflow of LLMClients."""

    # provider and proxy resources
    PROVIDER = "Provider"
    """An LLM provider, and the Secret that holds its api key."""

    PROXY = "Proxy"
    """A proxy to an LLM provider's own api."""

    # vectorstore resources
    VECTORSEARCH = "Vectorsearch"
    """A search of a Vectorstore."""

    VECTORSTORE = "Vectorstore"
    """A vector database, and the provider of its embeddings."""

    @classmethod
    def str_to_kind(cls, kind_str: str | bytes) -> str | None:
        """
        Return the kind that a string names, in any case.

        .. code-block:: python

            SAMKinds.str_to_kind("sqlplugin")  # "SqlPlugin"

        :param kind_str: The kind's name, in any case.
        :type kind_str: str | bytes
        :returns: The kind's value, or None if ``kind_str`` is not a string.
        :rtype: str | None
        :raises SmarterTypesValueError: If the string is not a kind.
        """
        if isinstance(kind_str, bytes):
            kind_str = kind_str.decode("utf-8")
        if not isinstance(kind_str, str):
            return None
        for member in cls:
            if member.value.lower() == kind_str.lower():
                return member.value
        raise SmarterTypesValueError(f"Invalid SAMKinds value: {kind_str}.")

    @classmethod
    def plural(cls, kind: str | SAMKinds) -> str:
        """
        Return the plural of a kind, pluralizing only its final CamelCase word.

        .. code-block:: python

            SAMKinds.plural(SAMKinds.API_CONNECTION)  # "ApiConnections"
            SAMKinds.plural("vectorsearch")  # "Vectorsearches"

        :param kind: The kind, as a member or its value, in any case.
        :type kind: str | SAMKinds
        :returns: The plural.
        :rtype: str
        :raises SmarterTypesValueError: If it is not a kind.
        """
        singular = cls.str_to_kind(kind.value if isinstance(kind, SAMKinds) else kind)
        if singular is None:
            raise SmarterTypesValueError(f"Invalid SAMKinds value: {kind!r}.")
        tokens = re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", singular)
        tokens[-1] = inflection.pluralize(tokens[-1])
        return "".join(tokens)

    @classmethod
    def all_plugins(cls) -> list[SAMKinds]:
        """
        Return the kinds of plugin.

        :returns: The members.
        :rtype: list[SAMKinds]
        """
        return [
            cls.STATIC_PLUGIN,
            cls.API_PLUGIN,
            cls.SKILL_PLUGIN,
            cls.SQL_PLUGIN,
            cls.WEBSEARCH_PLUGIN,
            cls.IMAGE_SEARCH_PLUGIN,
        ]

    @classmethod
    def all_connections(cls) -> list[SAMKinds]:
        """
        Return the kinds of connection.

        :returns: The members.
        :rtype: list[SAMKinds]
        """
        return [cls.API_CONNECTION, cls.SQL_CONNECTION]

    @classmethod
    def apply_order(cls) -> tuple[str, ...]:
        """
        Return the order in which to apply manifests: each kind after the kinds that its manifests may name.

        SAM resources refer to one another **by name**. A SqlPlugin's ``spec.connection`` is the name of a
        SqlConnection, and a SqlConnection's ``password`` is the name of a Secret. A broker resolves each
        name when it applies the manifest, so the resource that is named must already exist. A set of
        manifests, e.g. a project such as `Stackademy <https://github.com/smarter-sh/stackademy>`__, can
        only be applied in an order where every resource comes after the resources that it names. This
        is that order, for every kind. It is part of the definition of SAM: a new kind needs a deliberate
        place in it, and the tests fail until it has one.

        The order, kind by kind, and why:

        #. **Account**. Every other resource belongs to an account, so the account comes first. It
           names nothing.
        #. **User**. A user is a member of an account, and owns the resources that it applies.
        #. **SmarterAuthToken**. An api key's ``spec.username`` names its User. It comes before the
           LLMClients, whose ``spec.apiKey`` may name one.
        #. **Secret**. A Secret holds a password or an api key, and names nothing, but nearly everything
           after it may name a Secret: Providers, Proxies, LLMHosts, Connections, MCPClients,
           Vectorsearches and the search plugins. So it comes before all of them.
        #. **Provider**. An LLM provider names the Secret that holds its api key. LLMClients,
           Guardrails, Proxies and Vectorstores name a Provider, so it comes before them.
        #. **Proxy**. ``spec.provider`` names a Provider, and ``spec.apiKey`` a Secret.
        #. **LLMHostCompute**. A kind of node, and its node group. It names nothing, but an LLMHost's
           ``spec.compute`` names one.
        #. **LLMHost**. A self-hosted model. ``spec.compute`` names an LLMHostCompute, and its
           ``tokenSecret`` and ``apiKeySecret`` name Secrets.
        #. **SqlConnection**. ``password`` and ``proxyPassword`` name Secrets. SqlPlugins name it.
        #. **ApiConnection**. ``apiKey`` and ``proxyPassword`` name Secrets. ApiPlugins name it.
        #. **Guardrail**. ``spec.config.provider`` names the Provider that its semantic, moderation and
           llm_judge strategies call. LLMClients name it in ``spec.guardrails``.
        #. **Vectorstore**. ``spec.provider`` names the Provider of its embeddings, and its database may
           name a Secret.
        #. **Vectorsearch**. ``vectorstore_name`` names a Vectorstore, so it comes after them, and
           ``auth_secret_name`` names a Secret.
        #. **MCPClient**. ``credentials`` names a Secret. LLMClients name it in ``spec.mcpClients``.
        #. **The plugins: Plugin, SqlPlugin, ApiPlugin, SkillPlugin, WebsearchPlugin and
           ImageSearchPlugin**. A SqlPlugin's ``spec.connection`` names a SqlConnection, an ApiPlugin's
           an ApiConnection, and a WebsearchPlugin's and an ImageSearchPlugin's ``apiKey`` a Secret. A
           static Plugin and a SkillPlugin name nothing. All of them come after the Connections and
           before the LLMClients, whose ``spec.plugins`` names them.
        #. **CustomDomain**. A domain that serves LLMClients. It names nothing, but an LLMClient's
           ``customDomain`` names its domain, so it comes before them.
        #. **LLMClient**. It names the most kinds: a Provider, and its Plugins, Guardrails, MCPClients,
           CustomDomain and SmarterAuthToken. It comes after all of them.
        #. **Prompt**. A chat session, whose ``spec.llmclient`` names the LLMClient that it talks to.
        #. **Orchestrator**. Each of ``spec.config.harnesses`` names an LLMClient, by ``llmClientName``.
        #. **Budget**. Last, because ``spec.resources`` can name nearly any kind of resource: Accounts,
           Users, Connections, LLMClients, LLMHosts, LLMHostComputes, MCPClients, Orchestrators,
           Providers, Proxies, Vectorsearches and every kind of plugin. Applied any earlier, a Budget
           could name a resource that doesn't exist yet.

        Kinds that name nothing in common (e.g. the plugins among themselves) may be applied in any
        order. :meth:`apply_rank` gives each kind's position, and a kind that is not listed, i.e. not a
        SAM kind, is applied last:

        .. code-block:: python

            sorted(manifests, key=lambda m: SAMKinds.apply_rank(m["kind"]))

        :returns: The kinds' values, in the order in which to apply them.
        :rtype: tuple[str, ...]
        """
        return (
            cls.ACCOUNT.value,
            cls.USER.value,
            cls.AUTH_TOKEN.value,
            cls.SECRET.value,
            cls.PROVIDER.value,
            cls.PROXY.value,
            cls.LLM_HOST_COMPUTE.value,
            cls.LLM_HOST.value,
            cls.SQL_CONNECTION.value,
            cls.API_CONNECTION.value,
            cls.GUARDRAIL.value,
            cls.VECTORSTORE.value,
            cls.VECTORSEARCH.value,
            cls.MCP_CLIENT.value,
            cls.STATIC_PLUGIN.value,
            cls.SQL_PLUGIN.value,
            cls.API_PLUGIN.value,
            cls.SKILL_PLUGIN.value,
            cls.WEBSEARCH_PLUGIN.value,
            cls.IMAGE_SEARCH_PLUGIN.value,
            cls.CUSTOM_DOMAIN.value,
            cls.LLM_CLIENT.value,
            cls.PROMPT.value,
            cls.ORCHESTRATOR.value,
            cls.BUDGET.value,
        )

    @classmethod
    def apply_rank(cls, kind: str | SAMKinds) -> int:
        """
        Return the position of a kind in :meth:`apply_order`, to sort manifests by.

        .. code-block:: python

            SAMKinds.apply_rank(SAMKinds.SECRET) < SAMKinds.apply_rank("SqlConnection")  # True
            SAMKinds.apply_rank("NoSuchKind") == len(SAMKinds.apply_order())  # True: applied last

        :param kind: The kind, as a member or its value, in any case.
        :type kind: str | SAMKinds
        :returns: The kind's position, or the length of :meth:`apply_order` for a kind that isn't a SAM
            kind, so that it is applied last.
        :rtype: int
        """
        value = (kind.value if isinstance(kind, SAMKinds) else str(kind)).lower()
        order = [item.lower() for item in cls.apply_order()]
        return order.index(value) if value in order else len(order)


__all__ = ["SAMKinds"]
