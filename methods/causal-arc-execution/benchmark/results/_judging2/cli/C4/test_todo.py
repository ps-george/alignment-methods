"""Unit tests for the todo CLI."""
import json
import os
import tempfile
import unittest
from pathlib import Path

import todo


class TodoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "store.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_add(self):
        msg = todo.cmd_add("buy milk", self.path)
        self.assertIn("buy milk", msg)
        items = todo.load_items(self.path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "buy milk")
        self.assertFalse(items[0]["done"])

    def test_add_multiple_persists(self):
        todo.cmd_add("a", self.path)
        todo.cmd_add("b", self.path)
        items = todo.load_items(self.path)
        self.assertEqual([i["text"] for i in items], ["a", "b"])

    def test_list_empty(self):
        out = todo.cmd_list(self.path)
        self.assertIn("no TODO", out)

    def test_list_shows_indices_and_status(self):
        todo.cmd_add("first", self.path)
        todo.cmd_add("second", self.path)
        todo.cmd_done(0, self.path)
        out = todo.cmd_list(self.path)
        self.assertIn("0: [x] first", out)
        self.assertIn("1: [ ] second", out)

    def test_done_marks_complete(self):
        todo.cmd_add("task", self.path)
        todo.cmd_done(0, self.path)
        items = todo.load_items(self.path)
        self.assertTrue(items[0]["done"])

    def test_done_out_of_range(self):
        with self.assertRaises(IndexError):
            todo.cmd_done(5, self.path)

    def test_remove(self):
        todo.cmd_add("a", self.path)
        todo.cmd_add("b", self.path)
        todo.cmd_remove(0, self.path)
        items = todo.load_items(self.path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "b")

    def test_remove_out_of_range(self):
        with self.assertRaises(IndexError):
            todo.cmd_remove(0, self.path)

    def test_persistence_roundtrip(self):
        todo.cmd_add("persist", self.path)
        with self.path.open() as f:
            data = json.load(f)
        self.assertEqual(data[0]["text"], "persist")


class MainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "store.json"
        os.environ["TODO_CLI_STORE"] = str(self.path)

    def tearDown(self):
        os.environ.pop("TODO_CLI_STORE", None)
        self.tmp.cleanup()

    def test_main_add_and_list(self):
        self.assertEqual(todo.main(["add", "hello", "world"]), 0)
        items = todo.load_items(self.path)
        self.assertEqual(items[0]["text"], "hello world")

    def test_main_done_invalid_returns_1(self):
        self.assertEqual(todo.main(["done", "99"]), 1)


if __name__ == "__main__":
    unittest.main()
