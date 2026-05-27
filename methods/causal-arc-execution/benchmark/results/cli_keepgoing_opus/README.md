# todo CLI

A small TODO list manager written in Python. Items are persisted to a JSON
file in your home directory (`~/.todo_cli.json` by default).

## Requirements

Python 3.8+. No third-party dependencies.

## Usage

```
python todo.py add <text>      # add a new TODO item
python todo.py list            # list all items with indices and status
python todo.py done <index>    # mark item at <index> complete
python todo.py remove <index>  # remove the item at <index>
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

By default state is saved to `~/.todo_cli.json`. You can override the location
by setting the environment variable `TODO_CLI_STORE` to any file path. This
is useful for testing and for keeping multiple lists.

## Running the tests

```
python -m unittest test_todo.py -v
```
