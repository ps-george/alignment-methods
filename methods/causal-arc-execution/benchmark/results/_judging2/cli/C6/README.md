# TODO CLI

A simple command-line TODO manager written in Python. State is persisted to `~/.todo_cli.json`.

## Requirements

Python 3.9+. No third-party dependencies.

## Usage

```bash
python todo.py <command> [arguments]
```

### Commands

| Command | Description |
|---|---|
| `add <text>` | Add a new TODO item |
| `list` | List all items with index and status |
| `done <index>` | Mark item at `<index>` as complete |
| `remove <index>` | Remove item at `<index>` |

### Examples

```bash
# Add items
python todo.py add "Buy groceries"
python todo.py add "Write unit tests"

# List all items
python todo.py list
# [ ] 0  Buy groceries
# [ ] 1  Write unit tests

# Mark item 0 as done
python todo.py done 0
python todo.py list
# [x] 0  Buy groceries
# [ ] 1  Write unit tests

# Remove item 1
python todo.py remove 1
python todo.py list
# [x] 0  Buy groceries
```

## Running tests

```bash
python -m pytest test_todo.py -v
# or without pytest:
python -m unittest test_todo -v
```
