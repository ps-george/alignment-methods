"""Unit tests for the TODO CLI tool."""
import json
import os
import tempfile
import unittest
from pathlib import Path

import todo


class TodoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.tmp.close()
        self.path = Path(self.tmp.name)
        # start empty
        if self.path.exists():
            self.path.unlink()

    def tearDown(self):
        if self.path.exists():
            self.path.unlink()

    def test_add(self):
        msg = todo.add_item("buy milk", self.path)
        self.assertIn("buy milk", msg)
        state = todo.load_state(self.path)
        self.assertEqual(len(state["items"]), 1)
        self.assertEqual(state["items"][0]["text"], "buy milk")
        self.assertFalse(state["items"][0]["done"])

    def test_list_empty(self):
        self.assertEqual(todo.list_items(self.path), "No TODO items.")

    def test_list_with_items(self):
        todo.add_item("a", self.path)
        todo.add_item("b", self.path)
        todo.done_item(0, self.path)
        output = todo.list_items(self.path)
        self.assertIn("0: [x] a", output)
        self.assertIn("1: [ ] b", output)

    def test_done(self):
        todo.add_item("task", self.path)
        todo.done_item(0, self.path)
        state = todo.load_state(self.path)
        self.assertTrue(state["items"][0]["done"])

    def test_done_bad_index(self):
        with self.assertRaises(IndexError):
            todo.done_item(5, self.path)

    def test_remove(self):
        todo.add_item("a", self.path)
        todo.add_item("b", self.path)
        todo.remove_item(0, self.path)
        state = todo.load_state(self.path)
        self.assertEqual(len(state["items"]), 1)
        self.assertEqual(state["items"][0]["text"], "b")

    def test_remove_bad_index(self):
        with self.assertRaises(IndexError):
            todo.remove_item(0, self.path)

    def test_persistence(self):
        todo.add_item("persisted", self.path)
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(data["items"][0]["text"], "persisted")


if __name__ == "__main__":
    unittest.main()
