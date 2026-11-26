"""QC Engine — Spec sections 32-33
ตรวจคุณภาพก่อน Publish: ข้อความ สื่อ ลิงก์ ข้อเท็จจริง"""

from datetime import datetime, timezone

_counter = 0

QC_RULES = {
    "text_not_empty": lambda c: bool(c.get("text", "").strip()),
    "text_min_length": lambda c: len(c.get("text", "")) >= 10,
    "has_product_link": lambda c: bool(c.get("product_link")),
    "link_not_broken": lambda c: c.get("link_status") != "BROKEN",
    "no_banned_words": lambda c: not _has_banned(c.get("text", "")),
    "media_present": lambda c: bool(c.get("media_ids")),
    "fact_checked": lambda c: c.get("fact_check_status") == "PASSED",
}

BANNED_WORDS = [
    "guaranteed", "100%", "make money fast", "get rich",
    "รวยเร็ว", "การันตี", "รับรองผล",
]


def _has_banned(text):
    lower = text.lower()
    return any(w.lower() in lower for w in BANNED_WORDS)


def _next_id():
    global _counter
    _counter += 1
    return f"QC-{_counter:06d}"


class QCResult:
    def __init__(self, qc_id, content_id, passed, failures, warnings):
        self.qc_id = qc_id
        self.content_id = content_id
        self.passed = passed
        self.failures = failures
        self.warnings = warnings
        self.checked_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "qc_id": self.qc_id,
            "content_id": self.content_id,
            "passed": self.passed,
            "failures": self.failures,
            "warnings": self.warnings,
            "checked_at": self.checked_at,
        }


def check(content, rules=None, warn_rules=None):
    """Run QC on content dict.

    rules: list of rule names from QC_RULES to enforce (fail = block)
    warn_rules: list of rule names that produce warnings only
    """
    if rules is None:
        rules = ["text_not_empty", "text_min_length", "no_banned_words"]
    if warn_rules is None:
        warn_rules = ["has_product_link", "media_present"]

    failures = []
    warnings = []

    for rule_name in rules:
        fn = QC_RULES.get(rule_name)
        if fn and not fn(content):
            failures.append(rule_name)

    for rule_name in warn_rules:
        fn = QC_RULES.get(rule_name)
        if fn and not fn(content):
            warnings.append(rule_name)

    qc_id = _next_id()
    passed = len(failures) == 0

    return QCResult(
        qc_id=qc_id,
        content_id=content.get("id", "UNKNOWN"),
        passed=passed,
        failures=failures,
        warnings=warnings,
    )


def check_before_publish(content):
    """Full QC check required before any publish action."""
    return check(
        content,
        rules=["text_not_empty", "text_min_length", "no_banned_words",
               "has_product_link", "link_not_broken"],
        warn_rules=["media_present", "fact_checked"],
    )


def reset():
    global _counter
    _counter = 0
