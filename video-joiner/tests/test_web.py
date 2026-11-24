import time, unittest
from videojoiner import web


class ReapTest(unittest.TestCase):
    def test_old_finished_jobs_removed_running_kept(self):
        old = time.time() - web.TTL - 5
        for jid, st in (("old", "done"), ("busy", "running")):
            (web.ROOT / jid).mkdir()
            web.JOBS[jid] = {"status": st, "progress": 1.0, "created": old}
        web._reap()
        self.assertNotIn("old", web.JOBS)
        self.assertFalse((web.ROOT / "old").exists())
        self.assertIn("busy", web.JOBS)
        web.JOBS.pop("busy"); (web.ROOT / "busy").rmdir()


if __name__ == "__main__":
    unittest.main()
