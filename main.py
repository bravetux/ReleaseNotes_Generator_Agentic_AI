"""CLI shim — delegates to release_notes_agent.cli.app.

Usage:
    uv run python main.py generate --srs ... --sample ...
    uv run python main.py chat
"""

from release_notes_agent.cli.app import main

if __name__ == "__main__":
    main()
