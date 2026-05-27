#!/usr/bin/env python3
"""A simple TODO CLI tool."""
import argparse
import json
import os
import sys
from pathlib import Path

DEFAULT_STATE_PATH = Path.home() / ".todo_cli.json"


def load_state(path=DEFAULT_STATE_PATH):
    path = Path(path)
    if not path.exists():
        return {"items": []}
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "items" not in data:
            return {"items": []}
        return data
    except (json.JSONDecodeError, OSError):
        return {"items": []}


def save_state(state, path=DEFAULT_STATE_PATH):
    path = Path(path)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def add_item(text, path=DEFAULT_STATE_PATH):
    state = load_state(path)
    state["items"].append({"text": text, "done": False})
    save_state(state, path)
    return f"Added: {text}"


def list_items(path=DEFAULT_STATE_PATH):
    state = load_state(path)
    if not state["items"]:
        return "No TODO items."
    lines = []
    for i, item in enumerate(state["items"]):
        status = "[x]" if item["done"] else "[ ]"
        lines.append(f"{i}: {status} {item['text']}")
    return "\n".join(lines)


def done_item(index, path=DEFAULT_STATE_PATH):
    state = load_state(path)
    if index < 0 or index >= len(state["items"]):
        raise IndexError(f"Index {index} out of range")
    state["items"][index]["done"] = True
    save_state(state, path)
    return f"Marked done: {state['items'][index]['text']}"


def remove_item(index, path=DEFAULT_STATE_PATH):
    state = load_state(path)
    if index < 0 or index >= len(state["items"]):
        raise IndexError(f"Index {index} out of range")
    removed = state["items"].pop(index)
    save_state(state, path)
    return f"Removed: {removed['text']}"


def build_parser():
    parser = argparse.ArgumentParser(description="A simple TODO CLI tool.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new TODO item")
    p_add.add_argument("text", nargs="+", help="Text of the TODO item")

    sub.add_parser("list", help="List all TODO items")

    p_done = sub.add_parser("done", help="Mark an item complete")
    p_done.add_argument("index", type=int)

    p_remove = sub.add_parser("remove", help="Remove an item")
    p_remove.add_argument("index", type=int)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "add":
            print(add_item(" ".join(args.text)))
        elif args.command == "list":
            print(list_items())
        elif args.command == "done":
            print(done_item(args.index))
        elif args.command == "remove":
            print(remove_item(args.index))
    except IndexError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
