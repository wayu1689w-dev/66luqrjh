"""Tests — ทดสอบระบบ AI Affiliate Guardian"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestStateMachine(unittest.TestCase):
    def test_valid_transition(self):
        from ai_affiliate_guardian.core.state_machine import (
            ProductState, PRODUCT_TRANSITIONS, can_transition
        )
        self.assertTrue(can_transition(
            ProductState.INTAKE, ProductState.ELIGIBLE, PRODUCT_TRANSITIONS
        ))

    def test_invalid_transition(self):
        from ai_affiliate_guardian.core.state_machine import (
            ProductState, PRODUCT_TRANSITIONS, can_transition
        )
        self.assertFalse(can_transition(
            ProductState.INTAKE, ProductState.PUBLISHED, PRODUCT_TRANSITIONS
        ))


class TestClaimGuard(unittest.TestCase):
    def test_clean_script(self):
        from ai_affiliate_guardian.content.claim_guard import check_claims
        ok, msg = check_claims("สินค้านี้อร่อยมาก ลองแล้วชอบ")
        self.assertTrue(ok)

    def test_forbidden_claim(self):
        from ai_affiliate_guardian.content.claim_guard import check_claims
        ok, msg = check_claims("สินค้านี้รักษาโรคได้")
        self.assertFalse(ok)


class TestChannelIsolation(unittest.TestCase):
    def test_cross_channel_forbidden(self):
        from ai_affiliate_guardian.channels.channel_isolation import check_cross_channel
        ok, msg = check_cross_channel("cnt_1", "ch_monster_great", "ch_suea2992")
        self.assertFalse(ok)

    def test_same_channel_ok(self):
        from ai_affiliate_guardian.channels.channel_isolation import check_cross_channel
        ok, msg = check_cross_channel("cnt_1", "ch_monster_great", "ch_monster_great")
        self.assertTrue(ok)


class TestProductIntake(unittest.TestCase):
    def test_valid_product(self):
        from ai_affiliate_guardian.products.intake import intake_product
        product = {
            "product_name": "ขนมปัง",
            "commission_rate": 10,
            "product_category": "อาหาร",
            "source_platform": "TikTok Shop",
        }
        result = intake_product(product)
        self.assertTrue(result["accepted"])

    def test_missing_fields(self):
        from ai_affiliate_guardian.products.intake import intake_product
        result = intake_product({"product_name": "ขนมปัง"})
        self.assertFalse(result["accepted"])


class TestEvidence(unittest.TestCase):
    def test_unknown_not_zero(self):
        from ai_affiliate_guardian.governance.evidence import validate_evidence_claim
        ok, msg = validate_evidence_claim("unknown", "zero")
        self.assertFalse(ok)

    def test_confirmed_ok(self):
        from ai_affiliate_guardian.governance.evidence import validate_evidence_claim
        ok, msg = validate_evidence_claim("confirmed", "confirmed")
        self.assertTrue(ok)


class TestMoneyState(unittest.TestCase):
    def test_unknown_amount(self):
        from ai_affiliate_guardian.performance.money_state import classify_money, MoneyState
        state, msg = classify_money(None, "unknown")
        self.assertEqual(state, MoneyState.UNKNOWN)

    def test_confirmed_amount(self):
        from ai_affiliate_guardian.performance.money_state import classify_money, MoneyState
        state, msg = classify_money(500, "confirmed")
        self.assertEqual(state, MoneyState.CONFIRMED)


class TestPermissions(unittest.TestCase):
    def test_read_auto(self):
        from ai_affiliate_guardian.governance.permissions import check_permission
        ok, msg = check_permission("READ")
        self.assertTrue(ok)

    def test_high_impact_blocked(self):
        from ai_affiliate_guardian.governance.permissions import check_permission
        ok, msg = check_permission("HIGH_IMPACT")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
