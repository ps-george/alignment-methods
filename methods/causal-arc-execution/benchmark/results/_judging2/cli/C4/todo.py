#!/usr/bin/env python3
"""A simple TODO CLI tool that persists items to a JSON file."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any


DEFAULT_STORE = Path.home() / ".todo_cli.json"


def get_store_path() -> Path:
    """Return the path to the JSON store, honoring TODO_CLI_STORE env var."""
    override = os.environ.get("TODO_CLI_STORE")
    if override:
        return Path(override)
    return DEFAULT_STORE


def load_items(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def save_items(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def cmd_add(text: str, path: Path) -> str:
    items = load_items(path)
    items.append({"text": text, "done": False})
    save_items(path, items)
    return f"Added: {text}"


def cmd_list(path: Path) -> str:
    items = load_items(path)
    if not items:
        return "(no TODO items)"
    lines = []
    for i, item in enumerate(items):
        mark = "x" if item.get("done") else " "
        lines.append(f"{i}: [{mark}] {item.get('text', '')}")
    return "\n".join(lines)


def cmd_done(index: int, path: Path) -> str:
    items = load_items(path)
    if index < 0 or index >= len(items):
        raise IndexError(f"No item at index {index}")
    items[index]["done"] = True
    save_items(path, items)
    return f"Marked done: {items[index]['text']}"


def cmd_remove(index: int, path: Path) -> str:
    items = load_items(path)
    if index < 0 or index >= len(items):
        raise IndexError(f"No item at index {index}")
    removed = items.pop(index)
    save_items(path, items)
    return f"Removed: {removed['text']}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="A simple TODO CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new TODO item")
    p_add.add_argument("text", nargs="+", help="Text of the TODO item")

    sub.add_parser("list", help="List all TODO items")

    p_done = sub.add_parser("done", help="Mark an item complete")
    p_done.add_argument("index", type=int)

    p_remove = sub.add_parser("remove", help="Remove an item")
    p_remove.add_argument("index", type=int)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = get_store_path()

    try:
        if args.command == "add":
            print(cmd_add(" ".join(args.text), path))
        elif args.command == "list":
            print(cmd_list(path))
        elif args.command == "done":
            print(cmd_done(args.index, path))
        elif args.command == "remove":
            print(cmd_remove(args.index, path))
    except IndexError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
