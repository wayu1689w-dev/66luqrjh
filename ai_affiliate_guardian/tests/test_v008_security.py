"""Tests — v008 Security: Auth, RBAC, Secret Policy, Data Integrity"""

import unittest

from ai_affiliate_guardian.security.auth import (
    hash_password, verify_password, create_session, validate_session,
    revoke_session, clear_expired, active_session_count, _sessions,
)
from ai_affiliate_guardian.security.rbac import (
    get_permissions, has_permission, check_access, role_level,
    intersect_permissions, can_escalate,
)
from ai_affiliate_guardian.security.secret_policy import (
    scan_text, is_safe_to_store, redact, validate_audit_entry,
)
from ai_affiliate_guardian.security.data_integrity import (
    compute_hash, sign_record, verify_record, compute_batch_hash,
)


class TestAuth(unittest.TestCase):
    def setUp(self):
        _sessions.clear()

    def test_hash_and_verify(self):
        h, salt = hash_password("mypassword")
        self.assertTrue(verify_password("mypassword", h, salt))
        self.assertFalse(verify_password("wrong", h, salt))

    def test_create_and_validate_session(self):
        s = create_session("user1", "editor")
        ok, info = validate_session(s["token"])
        self.assertTrue(ok)
        self.assertEqual(info["user_id"], "user1")
        self.assertEqual(info["role"], "editor")

    def test_invalid_session(self):
        ok, msg = validate_session("fake-token")
        self.assertFalse(ok)
        self.assertEqual(msg, "SESSION_NOT_FOUND")

    def test_revoke_session(self):
        s = create_session("user1")
        self.assertTrue(revoke_session(s["token"]))
        ok, _ = validate_session(s["token"])
        self.assertFalse(ok)

    def test_session_count(self):
        create_session("a")
        create_session("b")
        self.assertEqual(active_session_count(), 2)


class TestRBAC(unittest.TestCase):
    def test_owner_has_all(self):
        perms = get_permissions("owner")
        self.assertIn("admin", perms)
        self.assertIn("kill_switch", perms)

    def test_viewer_read_only(self):
        self.assertTrue(has_permission("viewer", "read"))
        self.assertFalse(has_permission("viewer", "write"))

    def test_check_access(self):
        ok, _ = check_access("editor", "write")
        self.assertTrue(ok)
        ok, _ = check_access("viewer", "delete")
        self.assertFalse(ok)

    def test_role_level(self):
        self.assertGreater(role_level("owner"), role_level("admin"))
        self.assertGreater(role_level("admin"), role_level("viewer"))

    def test_intersect_permissions(self):
        result = intersect_permissions(
            ["read", "write"], ["read", "write", "delete"], ["read"]
        )
        self.assertEqual(result, ["read"])

    def test_can_escalate(self):
        self.assertTrue(can_escalate("owner", "viewer"))
        self.assertFalse(can_escalate("viewer", "owner"))


class TestSecretPolicy(unittest.TestCase):
    def test_detect_api_key(self):
        text = 'api_key = "sk_live_abc123def456"'
        findings = scan_text(text)
        self.assertGreater(len(findings), 0)

    def test_clean_text(self):
        findings = scan_text("hello world no secrets here")
        self.assertEqual(len(findings), 0)

    def test_is_safe_to_store(self):
        self.assertFalse(is_safe_to_store("password"))
        self.assertFalse(is_safe_to_store("API_KEY"))
        self.assertTrue(is_safe_to_store("username"))

    def test_redact(self):
        text = 'secret_key = "abcdef12345678"'
        result = redact(text)
        self.assertIn("[REDACTED]", result)

    def test_validate_audit_entry(self):
        ok, _ = validate_audit_entry({"action": "login", "user": "test"})
        self.assertTrue(ok)
        ok, _ = validate_audit_entry({"password": "secret123"})
        self.assertFalse(ok)


class TestDataIntegrity(unittest.TestCase):
    def test_compute_hash(self):
        h = compute_hash("hello")
        self.assertEqual(len(h), 64)
        self.assertEqual(h, compute_hash("hello"))

    def test_sign_and_verify(self):
        record = {"name": "test", "value": 42}
        signed = sign_record(record)
        self.assertIn("_hash", signed)
        ok, _ = verify_record(signed)
        self.assertTrue(ok)

    def test_tampered_record(self):
        record = {"name": "test", "value": 42}
        signed = sign_record(record)
        signed["value"] = 999
        ok, msg = verify_record(signed)
        self.assertFalse(ok)
        self.assertIn("แก้ไข", msg)

    def test_unsigned_record(self):
        ok, msg = verify_record({"name": "no hash"})
        self.assertFalse(ok)

    def test_batch_hash(self):
        records = [{"a": 1}, {"b": 2}]
        h = compute_batch_hash(records)
        self.assertEqual(len(h), 64)


if __name__ == "__main__":
    unittest.main()
