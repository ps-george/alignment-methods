# todo — A simple TODO CLI

A minimal command-line TODO manager written in Python. State persists to
`~/.todo_cli.json`.

## Requirements

- Python 3.7+

No third-party dependencies.

## Usage

```
python todo.py add <text>      # Add a new TODO item
python todo.py list            # List all items with index and status
python todo.py done <index>    # Mark item at <index> as complete
python todo.py remove <index>  # Remove item at <index>
```

### Examples

```
$ python todo.py add buy milk
Added: buy milk

$ python todo.py add write report
Added: write report

$ python todo.py list
0: [ ] buy milk
1: [ ] write report

$ python todo.py done 0
Marked done: buy milk

$ python todo.py list
0: [x] buy milk
1: [ ] write report

$ python todo.py remove 0
Removed: buy milk
```

## Storage

Items are stored as JSON in `~/.todo_cli.json` in the form:

```json
{
  "items": [
    {"text": "buy milk", "done": false}
  ]
}
```

## Tests

Run the unit tests with:

```
python -m unittest test_todo.py
```
