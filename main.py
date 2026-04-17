"""CLI entry point for release-notes-agent.

Usage:
    uv run python main.py "Your query here"
    uv run python main.py  # interactive mode
"""

import sys

from release_notes_agent.agents.orchestrator import create_orchestrator


def main() -> None:
    agent = create_orchestrator()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        response = agent(query)
        print(response)
    else:
        print("release-notes-agent — Interactive Mode (type 'exit' to quit)")
        print("-" * 60)
        while True:
            try:
                query = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if not query or query.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            response = agent(query)
            print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()
