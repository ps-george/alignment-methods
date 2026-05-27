#!/usr/bin/env python3
"""TODO CLI tool — add, list, done, remove."""

import argparse
import json
import sys
from pathlib import Path

TODO_FILE = Path.home() / ".todo.json"


def load_todos() -> list[dict]:
    if TODO_FILE.exists():
        with TODO_FILE.open() as f:
            return json.load(f)
    return []


def save_todos(todos: list[dict]) -> None:
    with TODO_FILE.open("w") as f:
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
    if todos[index]["done"]:
        print(f"Item {index} is already marked done.")
        return
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Simple TODO list manager.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add a new TODO item.")
    add_p.add_argument("text", help="Text of the TODO item.")

    sub.add_parser("list", help="List all TODO items.")

    done_p = sub.add_parser("done", help="Mark a TODO item complete.")
    done_p.add_argument("index", type=int, help="Index of the item.")

    remove_p = sub.add_parser("remove", help="Remove a TODO item.")
    remove_p.add_argument("index", type=int, help="Index of the item.")

    return parser


def main() -> None:
    parser = build_parser()
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
