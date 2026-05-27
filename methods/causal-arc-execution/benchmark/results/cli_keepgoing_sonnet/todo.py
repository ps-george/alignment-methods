#!/usr/bin/env python3
"""TODO CLI tool — add, list, done, remove."""

import json
import sys
from pathlib import Path

DATA_FILE = Path.home() / ".todo_items.json"


def load() -> list[dict]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def save(items: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(items, indent=2))


def cmd_add(text: str) -> None:
    items = load()
    items.append({"text": text, "done": False})
    save(items)
    print(f"Added: {text}")


def cmd_list() -> None:
    items = load()
    if not items:
        print("No TODO items.")
        return
    for i, item in enumerate(items):
        status = "x" if item["done"] else " "
        print(f"[{status}] {i}  {item['text']}")


def cmd_done(index: int) -> None:
    items = load()
    if index < 0 or index >= len(items):
        print(f"Error: index {index} out of range.")
        sys.exit(1)
    items[index]["done"] = True
    save(items)
    print(f"Marked done: {items[index]['text']}")


def cmd_remove(index: int) -> None:
    items = load()
    if index < 0 or index >= len(items):
        print(f"Error: index {index} out of range.")
        sys.exit(1)
    removed = items.pop(index)
    save(items)
    print(f"Removed: {removed['text']}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: todo.py <add|list|done|remove> [args]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: todo.py add <text>")
            sys.exit(1)
        cmd_add(" ".join(sys.argv[2:]))

    elif command == "list":
        cmd_list()

    elif command == "done":
        if len(sys.argv) < 3:
            print("Usage: todo.py done <index>")
            sys.exit(1)
        try:
            cmd_done(int(sys.argv[2]))
        except ValueError:
            print("Error: index must be an integer.")
            sys.exit(1)

    elif command == "remove":
        if len(sys.argv) < 3:
            print("Usage: todo.py remove <index>")
            sys.exit(1)
        try:
            cmd_remove(int(sys.argv[2]))
        except ValueError:
            print("Error: index must be an integer.")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
