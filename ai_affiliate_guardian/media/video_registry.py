"""Video Registry — จัดการวิดีโอ"""


def validate_video(file_path, min_resolution=720, max_size_mb=500):
    checks = []
    checks.append(("file_exists", True))
    checks.append(("min_resolution", min_resolution))
    checks.append(("max_size_mb", max_size_mb))
    return {
        "file_path": file_path,
        "checks": checks,
        "note": "ต้องตรวจจริงผ่าน ffprobe",
    }
