"""Content QC — ตรวจคุณภาพสคริปต์"""

import yaml
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "config" / "qc_rules.yaml"


def _load_rules():
    with open(RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_script(script_text):
    rules = _load_rules()["content_qc"]
    issues = []
    if len(script_text) < rules["min_script_length"]:
        issues.append(f"สั้นเกินไป ({len(script_text)} ตัวอักษร, ต้องการ {rules['min_script_length']})")
    if len(script_text) > rules["max_script_length"]:
        issues.append(f"ยาวเกินไป ({len(script_text)} ตัวอักษร, สูงสุด {rules['max_script_length']})")
    if issues:
        return False, issues
    return True, []
