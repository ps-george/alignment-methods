#!/usr/bin/env python3
"""Simple TODO CLI tool with JSON persistence."""

import argparse
import json
import sys
from pathlib import Path

TODO_FILE = Path.home() / ".todo_cli.json"


def load_todos() -> list[dict]:
    if TODO_FILE.exists():
        with open(TODO_FILE) as f:
            return json.load(f)
    return []


def save_todos(todos: list[dict]) -> None:
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def cmd_add(text: str) -> None:
    todos = load_todos()
    todos.append({"text": text, "done": False})
    save_todos(todos)
    print(f"Added: {text}")


def cmd_list() -> None:
    todos = load_todos()
    if not todos:
        print("No TODO items.")
        return
    for i, item in enumerate(todos):
        status = "x" if item["done"] else " "
        print(f"[{status}] {i}  {item['text']}")


def cmd_done(index: int) -> None:
    todos = load_todos()
    if index < 0 or index >= len(todos):
        print(f"Error: index {index} out of range.", file=sys.stderr)
        sys.exit(1)
    todos[index]["done"] = True
    save_todos(todos)
    print(f"Marked done: {todos[index]['text']}")


def cmd_remove(index: int) -> None:
    todos = load_todos()
    if index < 0 or index >= len(todos):
        print(f"Error: index {index} out of range.", file=sys.stderr)
        sys.exit(1)
    removed = todos.pop(index)
    save_todos(todos)
    print(f"Removed: {removed['text']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple TODO CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new TODO item")
    add_parser.add_argument("text", help="Text of the TODO item")

    subparsers.add_parser("list", help="List all TODO items")

    done_parser = subparsers.add_parser("done", help="Mark an item complete")
    done_parser.add_argument("index", type=int, help="Index of the item")

    remove_parser = subparsers.add_parser("remove", help="Remove an item")
    remove_parser.add_argument("index", type=int, help="Index of the item")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args.text)
    elif args.command == "list":
        cmd_list()
    elif args.command == "done":
        cmd_done(args.index)
    elif args.command == "remove":
        cmd_remove(args.index)


if __name__ == "__main__":
    main()
