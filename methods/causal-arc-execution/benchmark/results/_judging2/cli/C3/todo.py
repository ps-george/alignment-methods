#!/usr/bin/env python3
"""Simple TODO CLI tool with JSON persistence."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any


DEFAULT_STORE = Path.home() / ".todo_cli.json"


def load(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return data


def save(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def cmd_add(items: List[Dict[str, Any]], text: str) -> str:
    text = text.strip()
    if not text:
        raise ValueError("TODO text must not be empty")
    items.append({"text": text, "done": False})
    return f"Added: {text}"


def cmd_list(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "(no TODO items)"
    lines = []
    for i, item in enumerate(items):
        mark = "x" if item.get("done") else " "
        lines.append(f"{i}. [{mark}] {item.get('text', '')}")
    return "\n".join(lines)


def _check_index(items: List[Dict[str, Any]], index: int) -> None:
    if index < 0 or index >= len(items):
        raise IndexError(f"Index {index} out of range (0..{len(items) - 1 if items else 'empty'})")


def cmd_done(items: List[Dict[str, Any]], index: int) -> str:
    _check_index(items, index)
    items[index]["done"] = True
    return f"Marked done: {items[index]['text']}"


def cmd_remove(items: List[Dict[str, Any]], index: int) -> str:
    _check_index(items, index)
    removed = items.pop(index)
    return f"Removed: {removed['text']}"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="todo", description="A minimal TODO CLI.")
    p.add_argument("--store", type=Path, default=None,
                   help=f"Path to JSON store (default: {DEFAULT_STORE})")
    sub = p.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a new TODO item")
    p_add.add_argument("text", nargs="+", help="TODO text")

    sub.add_parser("list", help="list all TODO items")

    p_done = sub.add_parser("done", help="mark an item complete")
    p_done.add_argument("index", type=int)

    p_rm = sub.add_parser("remove", help="remove an item")
    p_rm.add_argument("index", type=int)

    return p


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = args.store if args.store is not None else Path(
        os.environ.get("TODO_STORE", str(DEFAULT_STORE))
    )

    items = load(store)
    try:
        if args.command == "add":
            msg = cmd_add(items, " ".join(args.text))
        elif args.command == "list":
            msg = cmd_list(items)
        elif args.command == "done":
            msg = cmd_done(items, args.index)
        elif args.command == "remove":
            msg = cmd_remove(items, args.index)
        else:  # pragma: no cover
            parser.error(f"unknown command: {args.command}")
            return 2
    except (ValueError, IndexError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    save(store, items)
    print(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
