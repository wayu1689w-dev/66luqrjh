"""Voice Registry — จัดการเสียงพากย์"""


VOICE_RULES = {
    "allowed_sources": ["owner", "ai_with_consent", "licensed"],
    "forbidden": ["impersonation", "deepfake_without_consent"],
}


def check_voice(source, has_consent=False):
    if source in ("owner",):
        return True, "เสียงเจ้าของ"
    if source == "ai_with_consent" and has_consent:
        return True, "AI voice — มีความยินยอม"
    if source == "licensed":
        return True, "เสียงมีลิขสิทธิ์ใช้งาน"
    return False, f"เสียง {source} — ต้องมีความยินยอม"
