"""Final QC — ตรวจรวมทุกด้านก่อนส่งอนุมัติ"""

from .content_qc import check_script
from .affiliate_qc import check_affiliate_link
from ..content.claim_guard import check_claims


def run_final_qc(content):
    results = []
    script = content.get("script", "")
    link = content.get("affiliate_link", "")

    ok, issues = check_script(script)
    results.append({"check": "content_qc", "passed": ok, "issues": issues})

    ok, msg = check_claims(script)
    results.append({"check": "claim_guard", "passed": ok, "issues": [msg] if not ok else []})

    ok, msg = check_affiliate_link(link)
    results.append({"check": "affiliate_qc", "passed": ok, "issues": [msg] if not ok else []})

    all_passed = all(r["passed"] for r in results)
    return {
        "passed": all_passed,
        "results": results,
        "action": "approve" if all_passed else "hold_for_review",
    }
