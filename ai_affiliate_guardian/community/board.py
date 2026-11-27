"""Community Board — Spec v008 Area 5
สมาชิก, โปรไฟล์, หมวดหมู่, กระทู้, คอมเมนต์, ถูกใจ, ค้นหา, แจ้งเตือน, รายงาน"""

from datetime import datetime, timezone

_counter = 0


def _next_id(prefix: str = "THR") -> str:
    global _counter
    _counter += 1
    return f"{prefix}-{_counter:06d}"


class Category:
    def __init__(self, name: str, description: str = ""):
        self.id = _next_id("CAT")
        self.name = name
        self.description = description


class Thread:
    def __init__(self, title: str, body: str, author_id: str, category_id: str):
        self.id = _next_id("THR")
        self.title = title
        self.body = body
        self.author_id = author_id
        self.category_id = category_id
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.comments: list[dict] = []
        self.likes: set = set()
        self.is_pinned = False
        self.is_locked = False
        self.reports: list[dict] = []

    def add_comment(self, author_id: str, text: str) -> dict:
        comment = {
            "id": _next_id("CMT"),
            "author_id": author_id,
            "text": text,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "likes": set(),
        }
        self.comments.append(comment)
        return comment

    def toggle_like(self, user_id: str) -> bool:
        if user_id in self.likes:
            self.likes.discard(user_id)
            return False
        self.likes.add(user_id)
        return True

    def report(self, reporter_id: str, reason: str) -> dict:
        r = {
            "id": _next_id("RPT"),
            "reporter_id": reporter_id,
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        self.reports.append(r)
        return r

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "author_id": self.author_id,
            "category_id": self.category_id,
            "created_at": self.created_at,
            "comment_count": len(self.comments),
            "like_count": len(self.likes),
            "is_pinned": self.is_pinned,
            "is_locked": self.is_locked,
            "report_count": len(self.reports),
        }


class Board:
    def __init__(self):
        self.categories: dict[str, Category] = {}
        self.threads: dict[str, Thread] = {}
        self.members: dict[str, dict] = {}
        self.notifications: list[dict] = []

    def add_category(self, name: str, description: str = "") -> Category:
        cat = Category(name, description)
        self.categories[cat.id] = cat
        return cat

    def register_member(self, user_id: str, display_name: str,
                        role: str = "member") -> dict:
        member = {
            "user_id": user_id,
            "display_name": display_name,
            "role": role,
            "joined_at": datetime.now(timezone.utc).isoformat(),
        }
        self.members[user_id] = member
        return member

    def create_thread(self, title: str, body: str, author_id: str,
                      category_id: str) -> Thread:
        if author_id not in self.members:
            raise ValueError("ต้องเป็นสมาชิกก่อนสร้างกระทู้")
        if category_id not in self.categories:
            raise ValueError(f"ไม่พบหมวดหมู่ {category_id}")
        thread = Thread(title, body, author_id, category_id)
        self.threads[thread.id] = thread
        return thread

    def search_threads(self, query: str) -> list[dict]:
        q = query.lower()
        return [
            t.to_dict() for t in self.threads.values()
            if q in t.title.lower() or q in t.body.lower()
        ]

    def get_threads_by_category(self, category_id: str) -> list[dict]:
        return [
            t.to_dict() for t in self.threads.values()
            if t.category_id == category_id
        ]

    def notify(self, user_id: str, message: str, thread_id: str = ""):
        self.notifications.append({
            "user_id": user_id,
            "message": message,
            "thread_id": thread_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "read": False,
        })

    def get_notifications(self, user_id: str, unread_only: bool = True):
        return [
            n for n in self.notifications
            if n["user_id"] == user_id and (not unread_only or not n["read"])
        ]


class SpamFilter:
    BLOCKED_WORDS = ["spam", "scam", "viagra", "casino", "เว็บพนัน", "สล็อต"]

    @classmethod
    def check(cls, text: str) -> tuple[bool, str]:
        lower = text.lower()
        for word in cls.BLOCKED_WORDS:
            if word in lower:
                return False, f"ตรวจพบคำต้องห้าม: {word}"
        return True, "ผ่าน"


class Moderator:
    @staticmethod
    def pin_thread(thread: Thread):
        thread.is_pinned = True

    @staticmethod
    def lock_thread(thread: Thread):
        thread.is_locked = True

    @staticmethod
    def resolve_report(report: dict, action: str = "dismissed"):
        report["status"] = action
        report["resolved_at"] = datetime.now(timezone.utc).isoformat()


def reset():
    global _counter
    _counter = 0
