"""Unit tests for todo.py"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Patch DATA_FILE before importing todo so tests use a temp file
import tempfile
import os

TMP_DIR = tempfile.mkdtemp()
TEST_DATA_FILE = Path(TMP_DIR) / "test_todo_items.json"

# Patch at module level before import
import importlib
import todo as todo_module

todo_module.DATA_FILE = TEST_DATA_FILE


class TodoTestBase(unittest.TestCase):
    def setUp(self):
        # Reset data file before each test
        if TEST_DATA_FILE.exists():
            TEST_DATA_FILE.unlink()
        todo_module.DATA_FILE = TEST_DATA_FILE


class TestAdd(TodoTestBase):
    def test_add_single_item(self):
        todo_module.cmd_add("Buy milk")
        items = todo_module.load()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "Buy milk")
        self.assertFalse(items[0]["done"])

    def test_add_multiple_items(self):
        todo_module.cmd_add("Item one")
        todo_module.cmd_add("Item two")
        todo_module.cmd_add("Item three")
        items = todo_module.load()
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["text"], "Item one")
        self.assertEqual(items[2]["text"], "Item three")

    def test_add_item_is_not_done(self):
        todo_module.cmd_add("Fresh task")
        items = todo_module.load()
        self.assertFalse(items[0]["done"])


class TestList(TodoTestBase):
    def test_list_empty(self, capsys=None):
        # Just ensure it runs without error on empty list
        todo_module.cmd_list()

    def test_list_shows_items(self):
        todo_module.cmd_add("Walk dog")
        todo_module.cmd_add("Read book")
        items = todo_module.load()
        self.assertEqual(len(items), 2)

    def test_list_output_format(self):
        todo_module.cmd_add("Task A")
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            todo_module.cmd_list()
        output = buf.getvalue()
        self.assertIn("Task A", output)
        self.assertIn("[ ]", output)

    def test_list_shows_done_status(self):
        todo_module.cmd_add("Done task")
        todo_module.cmd_done(0)
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            todo_module.cmd_list()
        output = buf.getvalue()
        self.assertIn("[x]", output)


class TestDone(TodoTestBase):
    def test_mark_done(self):
        todo_module.cmd_add("Finish report")
        todo_module.cmd_done(0)
        items = todo_module.load()
        self.assertTrue(items[0]["done"])

    def test_done_preserves_text(self):
        todo_module.cmd_add("Original text")
        todo_module.cmd_done(0)
        items = todo_module.load()
        self.assertEqual(items[0]["text"], "Original text")

    def test_done_out_of_range_exits(self):
        todo_module.cmd_add("Only item")
        with self.assertRaises(SystemExit):
            todo_module.cmd_done(5)

    def test_done_negative_index_exits(self):
        todo_module.cmd_add("Only item")
        with self.assertRaises(SystemExit):
            todo_module.cmd_done(-1)

    def test_done_specific_index(self):
        todo_module.cmd_add("Task 0")
        todo_module.cmd_add("Task 1")
        todo_module.cmd_add("Task 2")
        todo_module.cmd_done(1)
        items = todo_module.load()
        self.assertFalse(items[0]["done"])
        self.assertTrue(items[1]["done"])
        self.assertFalse(items[2]["done"])


class TestRemove(TodoTestBase):
    def test_remove_item(self):
        todo_module.cmd_add("To remove")
        todo_module.cmd_remove(0)
        items = todo_module.load()
        self.assertEqual(len(items), 0)

    def test_remove_correct_item(self):
        todo_module.cmd_add("Keep this")
        todo_module.cmd_add("Remove this")
        todo_module.cmd_add("Keep this too")
        todo_module.cmd_remove(1)
        items = todo_module.load()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["text"], "Keep this")
        self.assertEqual(items[1]["text"], "Keep this too")

    def test_remove_out_of_range_exits(self):
        todo_module.cmd_add("Only item")
        with self.assertRaises(SystemExit):
            todo_module.cmd_remove(99)

    def test_remove_negative_index_exits(self):
        todo_module.cmd_add("Only item")
        with self.assertRaises(SystemExit):
            todo_module.cmd_remove(-1)

    def test_remove_from_empty_exits(self):
        with self.assertRaises(SystemExit):
            todo_module.cmd_remove(0)


if __name__ == "__main__":
    unittest.main()
