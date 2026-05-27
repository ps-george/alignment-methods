"""Unit tests for todo.py."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure the module under test is importable from the same directory.
sys.path.insert(0, str(Path(__file__).parent))

import todo


class TodoTestCase(unittest.TestCase):
    """Base class — redirects TODO_FILE to a temp path for each test."""

    def setUp(self):
        import tempfile
        self._tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self._tmp_path = Path(self._tmp.name)
        self._tmp.close()
        self._tmp_path.unlink()  # start without a file so load_todos returns []
        self._patcher = patch.object(todo, "TODO_FILE", self._tmp_path)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        if self._tmp_path.exists():
            self._tmp_path.unlink()

    def _read_raw(self):
        with self._tmp_path.open() as f:
            return json.load(f)


class TestAdd(TodoTestCase):
    def test_add_creates_item(self):
        todo.cmd_add("buy milk")
        items = self._read_raw()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "buy milk")
        self.assertFalse(items[0]["done"])

    def test_add_multiple_items(self):
        todo.cmd_add("first")
        todo.cmd_add("second")
        items = self._read_raw()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[1]["text"], "second")


class TestList(TodoTestCase):
    def test_list_empty(self, capsys=None):
        with patch("builtins.print") as mock_print:
            todo.cmd_list()
            mock_print.assert_called_once_with("No TODO items.")

    def test_list_shows_items(self):
        todo.cmd_add("task one")
        todo.cmd_add("task two")
        with patch("builtins.print") as mock_print:
            todo.cmd_list()
            calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertTrue(any("task one" in c for c in calls))
        self.assertTrue(any("task two" in c for c in calls))

    def test_list_shows_done_status(self):
        todo.cmd_add("finish report")
        todo.cmd_done(0)
        with patch("builtins.print") as mock_print:
            todo.cmd_list()
            output = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
        self.assertIn("[x]", output)


class TestDone(TodoTestCase):
    def test_mark_done(self):
        todo.cmd_add("exercise")
        todo.cmd_done(0)
        self.assertTrue(self._read_raw()[0]["done"])

    def test_already_done_is_idempotent(self):
        todo.cmd_add("exercise")
        todo.cmd_done(0)
        todo.cmd_done(0)  # should not raise
        self.assertTrue(self._read_raw()[0]["done"])

    def test_out_of_range_exits(self):
        todo.cmd_add("something")
        with self.assertRaises(SystemExit):
            todo.cmd_done(99)

    def test_negative_index_exits(self):
        with self.assertRaises(SystemExit):
            todo.cmd_done(-1)


class TestRemove(TodoTestCase):
    def test_remove_item(self):
        todo.cmd_add("alpha")
        todo.cmd_add("beta")
        todo.cmd_remove(0)
        items = self._read_raw()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "beta")

    def test_remove_out_of_range_exits(self):
        with self.assertRaises(SystemExit):
            todo.cmd_remove(0)

    def test_remove_all_items(self):
        todo.cmd_add("only")
        todo.cmd_remove(0)
        self.assertEqual(self._read_raw(), [])


if __name__ == "__main__":
    unittest.main()
