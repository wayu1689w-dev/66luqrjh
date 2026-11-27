"""Tests — v008 Database Store"""

import shutil
import unittest
from pathlib import Path

from ai_affiliate_guardian.database.store import Store, STORAGE_ROOT


class TestStore(unittest.TestCase):
    COLLECTION = "_test_v008_db"

    def setUp(self):
        self.store = Store(self.COLLECTION)
        self.store._save([])

    def tearDown(self):
        if self.store.path.exists():
            self.store.path.unlink()

    def test_insert_and_find(self):
        self.store.insert({"name": "เสือ", "type": "admin"})
        result = self.store.find(name="เสือ")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "เสือ")

    def test_find_one(self):
        self.store.insert({"name": "แมว"})
        r = self.store.find_one(name="แมว")
        self.assertIsNotNone(r)
        self.assertIsNone(self.store.find_one(name="ไม่มี"))

    def test_count(self):
        self.store.insert({"x": 1})
        self.store.insert({"x": 2})
        self.assertEqual(self.store.count(), 2)

    def test_delete(self):
        self.store.insert({"name": "del"})
        deleted = self.store.delete(name="del")
        self.assertEqual(deleted, 1)
        self.assertEqual(self.store.count(), 0)

    def test_update(self):
        self.store.insert({"name": "old"})
        updated = self.store.update({"name": "old"}, {"name": "new"})
        self.assertEqual(updated, 1)
        r = self.store.find_one(name="new")
        self.assertIsNotNone(r)

    def test_backup(self):
        self.store.insert({"data": "test"})
        path = self.store.backup()
        self.assertTrue(Path(path).exists())
        Path(path).unlink()

    def test_integrity_check_clean(self):
        failures = self.store.integrity_check()
        self.assertEqual(len(failures), 0)


if __name__ == "__main__":
    unittest.main()
