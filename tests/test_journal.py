"""Test smarter_types.journal: the Smarter Journal's enumerations."""

import logging

import pytest

from smarter_types import SAMKinds, SmarterJournalCliCommands, SmarterJournalThings


def test_every_kind_is_a_thing():
    """Each SAM kind is a thing with the same value, and ChatConfig is the only thing that isn't a kind."""
    things = set(SmarterJournalThings.all())
    assert set(SAMKinds.all()) <= things
    assert things - set(SAMKinds.all()) == {SmarterJournalThings.PROMPT_CONFIG.value}


def test_thing_lookup():
    """A thing is looked up by its value."""
    assert SmarterJournalThings("Plugin") is SmarterJournalThings.STATIC_PLUGIN
    assert SmarterJournalThings.MCPCLIENT.value == SAMKinds.MCP_CLIENT.value


def test_things_choices():
    """The model choices are (value, value) pairs of things, without the LLMHost kinds."""
    choices = SmarterJournalThings.choices()
    assert all(value == label for value, label in choices)
    assert set(SmarterJournalThings.all()) - {value for value, _ in choices} == {"LLMHost", "LLMHostCompute"}


def test_commands_choices_and_past_tense():
    """Every command is a choice, and has a past tense."""
    commands = set(SmarterJournalCliCommands.all())
    assert {value for value, _ in SmarterJournalCliCommands.choices()} == commands
    assert set(SmarterJournalCliCommands.past_tense()) == commands


@pytest.mark.parametrize(
    ("url", "command"),
    [
        ("http://localhost:9357/api/v1/cli/example_manifest/Account/", "example_manifest"),
        (b"http://localhost:9357/api/v1/cli/apply/", "apply"),
        ("https://platform.example.com/api/v1/cli/whoami/", "whoami"),
        ("http://localhost:9357/dashboard/", None),
    ],
)
def test_command_from_url(url, command):
    """The command is the first slug that is one, of an api url."""
    assert SmarterJournalCliCommands.from_url(url) == command


def test_command_from_url_without_command(caplog):
    """An api url without a command is None, and a warning."""
    with caplog.at_level(logging.WARNING, logger="smarter_types.journal"):
        assert SmarterJournalCliCommands.from_url("http://localhost:9357/api/v1/cli/nothing/") is None
    assert "could not extract a command" in caplog.text
