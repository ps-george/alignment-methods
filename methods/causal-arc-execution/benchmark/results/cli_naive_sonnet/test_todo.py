"""Unit tests for the TODO CLI tool."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure the module can be imported regardless of cwd
sys.path.insert(0, str(Path(__file__).parent))

import todo


class TestTodoCLI(unittest.TestCase):
    def setUp(self):
        """Point TODO_FILE at a temp path so tests are isolated."""
        self.tmp_file = Path(__file__).parent / ".todo_test.json"
        # Patch the module-level TODO_FILE
        self.patcher = patch.object(todo, "TODO_FILE", self.tmp_file)
        self.patcher.start()
        # Start each test with a clean slate
        if self.tmp_file.exists():
            self.tmp_file.unlink()

    def tearDown(self):
        self.patcher.stop()
        if self.tmp_file.exists():
            self.tmp_file.unlink()

    # --- add ---

    def test_add_creates_item(self):
        todo.cmd_add("Buy milk")
        items = todo.load_todos()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "Buy milk")
        self.assertFalse(items[0]["done"])

    def test_add_multiple_items(self):
        todo.cmd_add("First")
        todo.cmd_add("Second")
        items = todo.load_todos()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[1]["text"], "Second")

    # --- list ---

    def test_list_empty(self, capsys=None):
        # Should not raise; just prints "No TODO items."
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            todo.cmd_list()
        self.assertIn("No TODO items", buf.getvalue())

    def test_list_shows_items(self):
        todo.cmd_add("Task A")
        todo.cmd_add("Task B")
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            todo.cmd_list()
        output = buf.getvalue()
        self.assertIn("Task A", output)
        self.assertIn("Task B", output)
        self.assertIn("[ ]", output)  # not done marker

    # --- done ---

    def test_done_marks_item(self):
        todo.cmd_add("Finish report")
        todo.cmd_done(0)
        items = todo.load_todos()
        self.assertTrue(items[0]["done"])

    def test_done_invalid_index_exits(self):
        todo.cmd_add("Only item")
        with self.assertRaises(SystemExit):
            todo.cmd_done(5)

    def test_done_shows_in_list(self):
        todo.cmd_add("Done task")
        todo.cmd_done(0)
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            todo.cmd_list()
        self.assertIn("[x]", buf.getvalue())

    # --- remove ---

    def test_remove_deletes_item(self):
        todo.cmd_add("Temporary")
        todo.cmd_remove(0)
        items = todo.load_todos()
        self.assertEqual(len(items), 0)

    def test_remove_correct_item(self):
        todo.cmd_add("Keep me")
        todo.cmd_add("Delete me")
        todo.cmd_remove(1)
        items = todo.load_todos()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "Keep me")

    def test_remove_invalid_index_exits(self):
        with self.assertRaises(SystemExit):
            todo.cmd_remove(99)


if __name__ == "__main__":
    unittest.main()
