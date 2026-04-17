"""Example tools demonstrating the Strands @tool decorator pattern."""

from strands import tool


@tool
def greet(name: str) -> str:
    """Greet a person by name.

    Args:
        name: The name of the person to greet.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}! Welcome to release-notes-agent."


@tool
def add_numbers(a: float, b: float) -> dict:
    """Add two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        A dict with the inputs, result, and operation performed.
    """
    try:
        result = a + b
        return {"a": a, "b": b, "result": result, "operation": "addition"}
    except Exception as e:
        return {"error": str(e)}
