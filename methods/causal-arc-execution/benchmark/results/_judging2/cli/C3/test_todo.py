"""Unit tests for the TODO CLI."""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import todo


class TodoCoreTests(unittest.TestCase):
    def test_add_appends_item(self):
        items = []
        msg = todo.cmd_add(items, "buy milk")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], {"text": "buy milk", "done": False})
        self.assertIn("buy milk", msg)

    def test_add_rejects_empty(self):
        with self.assertRaises(ValueError):
            todo.cmd_add([], "   ")

    def test_list_empty_and_populated(self):
        self.assertIn("no TODO", todo.cmd_list([]))
        items = [{"text": "a", "done": False}, {"text": "b", "done": True}]
        out = todo.cmd_list(items)
        self.assertIn("0. [ ] a", out)
        self.assertIn("1. [x] b", out)

    def test_done_marks_complete(self):
        items = [{"text": "a", "done": False}]
        todo.cmd_done(items, 0)
        self.assertTrue(items[0]["done"])

    def test_done_invalid_index(self):
        with self.assertRaises(IndexError):
            todo.cmd_done([], 0)
        with self.assertRaises(IndexError):
            todo.cmd_done([{"text": "a", "done": False}], 5)

    def test_remove_pops_item(self):
        items = [{"text": "a", "done": False}, {"text": "b", "done": False}]
        todo.cmd_remove(items, 0)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "b")

    def test_remove_invalid_index(self):
        with self.assertRaises(IndexError):
            todo.cmd_remove([], 0)


class TodoCLIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.store = Path(self.tmp.name) / "store.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *args):
        return todo.main(["--store", str(self.store), *args])

    def test_full_cycle(self):
        self.assertEqual(self._run("add", "write", "report"), 0)
        self.assertEqual(self._run("add", "ship", "it"), 0)
        data = json.loads(self.store.read_text())
        self.assertEqual([d["text"] for d in data], ["write report", "ship it"])
        self.assertEqual([d["done"] for d in data], [False, False])

        self.assertEqual(self._run("done", "0"), 0)
        data = json.loads(self.store.read_text())
        self.assertTrue(data[0]["done"])
        self.assertFalse(data[1]["done"])

        self.assertEqual(self._run("remove", "0"), 0)
        data = json.loads(self.store.read_text())
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["text"], "ship it")

        self.assertEqual(self._run("list"), 0)

    def test_list_with_no_store(self):
        self.assertEqual(self._run("list"), 0)

    def test_bad_index_returns_nonzero(self):
        self.assertEqual(self._run("done", "9"), 1)
        self.assertEqual(self._run("remove", "9"), 1)

    def test_load_handles_corrupt_file(self):
        self.store.write_text("not json{{")
        self.assertEqual(todo.load(self.store), [])

    def test_load_handles_non_list(self):
        self.store.write_text('{"text": "x"}')
        self.assertEqual(todo.load(self.store), [])


if __name__ == "__main__":
    unittest.main()
