# TODO CLI

A simple command-line TODO manager written in Python. State is persisted to `~/.todo_items.json`.

## Usage

```
python todo.py <command> [args]
```

### Commands

| Command | Description |
|---|---|
| `add <text>` | Add a new TODO item |
| `list` | List all items with their index and status |
| `done <index>` | Mark an item as complete |
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

# Mark item 0 as done
python todo.py done 0
# [x] 0  Buy groceries
# [ ] 1  Write unit tests

# Remove item 1
python todo.py remove 1
```

## Running Tests

```bash
python -m pytest test_todo.py -v
```

Requires `pytest` (`pip install pytest`). The tests cover all four commands and use a temporary file so they do not touch `~/.todo_items.json`.
