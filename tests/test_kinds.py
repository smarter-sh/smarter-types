"""Test smarter_types.kinds: SAMKinds and the order in which manifests are applied."""

import pytest

from smarter_types import SAMKinds, SmarterTypesValueError


def test_values_are_unique():
    """No two members share a value."""
    assert len(SAMKinds.all()) == len(set(SAMKinds.all())) == len(SAMKinds)


def test_lookup_by_value():
    """A member is looked up by its value, and its str() is its value."""
    assert SAMKinds("Secret") is SAMKinds.SECRET
    assert SAMKinds("Plugin") is SAMKinds.STATIC_PLUGIN
    assert SAMKinds("SmarterAuthToken") is SAMKinds.AUTH_TOKEN
    assert str(SAMKinds.LLM_CLIENT) == "LLMClient"


@pytest.mark.parametrize(
    ("text", "kind"),
    [("sqlplugin", "SqlPlugin"), ("LLMCLIENT", "LLMClient"), (b"secret", "Secret"), ("Plugin", "Plugin")],
)
def test_str_to_kind(text, kind):
    """A kind is found in any case, from str or bytes."""
    assert SAMKinds.str_to_kind(text) == kind


def test_str_to_kind_invalid():
    """A string that isn't a kind is an error, and anything that isn't a string is None."""
    with pytest.raises(SmarterTypesValueError, match="NoSuchKind"):
        SAMKinds.str_to_kind("NoSuchKind")
    with pytest.raises(ValueError):
        SAMKinds.str_to_kind("NoSuchKind")
    assert SAMKinds.str_to_kind(None) is None


@pytest.mark.parametrize(
    ("kind", "plural"),
    [
        (SAMKinds.API_CONNECTION, "ApiConnections"),
        ("vectorsearch", "Vectorsearches"),
        ("LLMClient", "LLMClients"),
        ("Proxy", "Proxies"),
        ("SmarterAuthToken", "SmarterAuthTokens"),
    ],
)
def test_plural(kind, plural):
    """Only a kind's last word is pluralized."""
    assert SAMKinds.plural(kind) == plural


def test_plural_invalid():
    """A value that isn't a kind has no plural."""
    with pytest.raises(SmarterTypesValueError):
        SAMKinds.plural("NoSuchKind")
    with pytest.raises(SmarterTypesValueError):
        SAMKinds.plural(None)


def test_plugins_and_connections():
    """The plugins and connections are the members whose kinds end in Plugin and Connection."""
    assert {kind.value for kind in SAMKinds.all_plugins()} == {
        kind for kind in SAMKinds.all() if kind.endswith("Plugin")
    }
    assert {kind.value for kind in SAMKinds.all_connections()} == {
        kind for kind in SAMKinds.all() if kind.endswith("Connection")
    }


def test_every_kind_has_a_place_in_the_order():
    """Each kind is in the apply order, once, so that a new kind gets a deliberate place."""
    assert sorted(SAMKinds.apply_order()) == sorted(SAMKinds.all())


@pytest.mark.parametrize(
    ("dependency", "dependent"),
    [
        ("Account", "User"),
        ("User", "SmarterAuthToken"),
        ("SmarterAuthToken", "LLMClient"),
        ("Secret", "Provider"),
        ("Secret", "SqlConnection"),
        ("Secret", "ApiConnection"),
        ("Secret", "MCPClient"),
        ("Provider", "Proxy"),
        ("Provider", "Guardrail"),
        ("Provider", "Vectorstore"),
        ("LLMHostCompute", "LLMHost"),
        ("SqlConnection", "SqlPlugin"),
        ("ApiConnection", "ApiPlugin"),
        ("Vectorstore", "Vectorsearch"),
        ("SqlPlugin", "LLMClient"),
        ("ApiPlugin", "LLMClient"),
        ("MCPClient", "LLMClient"),
        ("Guardrail", "LLMClient"),
        ("CustomDomain", "LLMClient"),
        ("LLMClient", "Prompt"),
        ("LLMClient", "Orchestrator"),
        ("LLMClient", "Budget"),
    ],
)
def test_dependencies_come_first(dependency, dependent):
    """Each kind comes after the kinds that its manifests name."""
    assert SAMKinds.apply_rank(dependency) < SAMKinds.apply_rank(dependent)


def test_budget_is_last():
    """A Budget can name nearly any kind, so it is applied last."""
    assert SAMKinds.apply_order()[-1] == SAMKinds.BUDGET.value


def test_apply_rank():
    """A kind is a member or its value, in any case; any other kind is applied last."""
    assert SAMKinds.apply_rank(SAMKinds.SECRET) == SAMKinds.apply_order().index("Secret")
    assert SAMKinds.apply_rank("secret") == SAMKinds.apply_rank("Secret")
    assert SAMKinds.apply_rank("NoSuchKind") == len(SAMKinds.apply_order())


def test_sorting_manifests():
    """Manifests sort into the apply order, with unknown kinds last."""
    manifests = [{"kind": kind} for kind in ("Budget", "LLMClient", "NoSuchKind", "SqlPlugin", "Secret")]
    ordered = sorted(manifests, key=lambda m: SAMKinds.apply_rank(m["kind"]))
    assert [m["kind"] for m in ordered] == ["Secret", "SqlPlugin", "LLMClient", "Budget", "NoSuchKind"]
