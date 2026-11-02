"""Spec-derived tests for the public role_line detector contract."""
import importlib.util
import os
from pathlib import Path

import pytest


SOURCE = Path(os.environ.get("ROLE_LINE_SOURCE", Path(__file__).with_name("role_line.py")))
SPEC = importlib.util.spec_from_file_location("role_line_under_test", SOURCE)
role_line = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(role_line)


def test_is_event_recognizes_event_after_leading_reminder():
    text = "<system-reminder>notice</system-reminder>\n<CROSS-SESSION-MESSAGE id='7'>ignored"
    assert role_line.is_event(text) is True


def test_clean_removes_wrappers_and_normalizes_line_endings():
    text = "\ufeffYou are working in C:\\work\r\n<system-reminder>x</system-reminder>\r\n<pasted_content>\u200bYou are Eagle Eyes.</pasted_content>"
    assert role_line.clean(text) == "You are Eagle Eyes."


def test_first_line_skips_empty_and_label_only_lines():
    assert role_line.first_line("\nTask:\n\n> You are Planner.\nYou are Later.") == "You are Planner."


def test_role_name_at_two_word_limit_resolves_known_spelling():
    assert role_line.role_line("You are eagle_eyes.", known=["Eagle Eyes"]) == "Eagle Eyes"


def test_one_word_role_below_two_word_limit_is_accepted():
    assert role_line.role_line("You are Builder.") == "Builder"


def test_three_word_role_above_two_word_limit_is_rejected():
    assert role_line.role_line("You are Senior Session Planner.", known=["Senior Session Planner"]) is None


def test_known_roles_reject_unknown_names():
    assert role_line.role_line("You are Builder.", known=["Planner"]) is None


def test_event_text_is_rejected_by_default_and_when_explicitly_allowed():
    event = "<task-notification> You are Builder."
    assert role_line.role_line(event) is None
    # Allowing event processing cannot make the event marker itself a role line.
    assert role_line.role_line(event, events=True) is None


def test_strict_requires_name_to_end_the_sentence():
    prompt = "You are Supervisor for this task"
    assert role_line.role_line(prompt, strict=False) == "Supervisor"
    assert role_line.role_line(prompt, strict=True) is None


def test_empty_and_malformed_inputs_have_no_role():
    assert role_line.role_line("") is None
    assert role_line.role_line("A quoted example: `You are Builder.`") is None
    assert role_line.role_line("Background only; no Task wrapper") is None


def test_string_conversion_error_propagates():
    class BrokenText:
        def __str__(self):
            raise RuntimeError("conversion failed")

    with pytest.raises(RuntimeError, match="conversion failed"):
        role_line.role_line(BrokenText())
