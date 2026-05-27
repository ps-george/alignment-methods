# todo — a minimal TODO CLI

A small command-line TODO manager written in Python. State is persisted as
JSON to `~/.todo_cli.json` in the user's home directory.

## Requirements

- Python 3.8+
- No third-party dependencies (standard library only).

## Usage

Run via the script directly:

```sh
python todo.py <command> [args]
```

### Commands

| Command           | Description                              |
| ----------------- | ---------------------------------------- |
| `add <text>`      | Add a new TODO item.                     |
| `list`            | List all TODO items with index + status. |
| `done <index>`    | Mark the item at `<index>` complete.     |
| `remove <index>`  | Remove the item at `<index>`.            |

Indices are zero-based and shown by `list`.

### Examples

```sh
$ python todo.py add buy milk
Added: buy milk

$ python todo.py add write report
Added: write report

$ python todo.py list
0. [ ] buy milk
1. [ ] write report

$ python todo.py done 0
Marked done: buy milk

$ python todo.py list
0. [x] buy milk
1. [ ] write report

$ python todo.py remove 0
Removed: buy milk
```

### Storage location

By default state is written to `~/.todo_cli.json`. Override with:

- `--store /path/to/file.json` (per-invocation flag), or
- `TODO_STORE=/path/to/file.json` (environment variable).

## Running the tests

```sh
python -m unittest test_todo.py -v
```

The test suite covers all four commands (both the pure functions and the
CLI entrypoint), including error paths for invalid indices, empty input,
and a corrupt store file.
