# TODO CLI

A minimal command-line TODO list manager written in Python. State persists to `~/.todo.json`.

## Requirements

Python 3.8+. No third-party dependencies.

## Usage

```
python todo.py <command> [args]
```

### Commands

| Command | Description |
|---|---|
| `add <text>` | Add a new TODO item |
| `list` | List all items with index and status |
| `done <index>` | Mark an item complete |
| `remove <index>` | Remove an item |

### Examples

```bash
# Add items
python todo.py add "Buy groceries"
python todo.py add "Write unit tests"

# List items
python todo.py list
# [ ] 0  Buy groceries
# [ ] 1  Write unit tests

# Mark done
python todo.py done 0
# Marked done: Buy groceries

python todo.py list
# [x] 0  Buy groceries
# [ ] 1  Write unit tests

# Remove an item
python todo.py remove 1
# Removed: Write unit tests
```

## Running tests

```bash
python -m pytest test_todo.py -v
```

12 tests cover add, list, done, and remove including edge cases (out-of-range index, already-done idempotency, empty list).
