"""Tests for example tools.

Uses .__wrapped__() to call the underlying function, bypassing the @tool decorator.
"""

from release_notes_agent.tools.example_tools import add_numbers, greet


class TestGreet:
    def test_greet_returns_greeting(self):
        result = greet.__wrapped__(name="World")
        assert "Hello, World!" in result

    def test_greet_with_empty_name(self):
        result = greet.__wrapped__(name="")
        assert "Hello, !" in result


class TestAddNumbers:
    def test_add_positive_numbers(self):
        result = add_numbers.__wrapped__(a=2.0, b=3.0)
        assert result["result"] == 5.0
        assert result["operation"] == "addition"

    def test_add_negative_numbers(self):
        result = add_numbers.__wrapped__(a=-1.0, b=-2.0)
        assert result["result"] == -3.0

    def test_add_zero(self):
        result = add_numbers.__wrapped__(a=0.0, b=0.0)
        assert result["result"] == 0.0
