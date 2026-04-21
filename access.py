"""
Доступ к боту: заявка → уведомление админам → ручное одобрение (/approve).
Состояние хранится в data/access_state.json
"""

import json
import os
from typing import Optional
from pathlib import Path
from threading import Lock

_STATE_LOCK = Lock()
_STATE_PATH = Path(__file__).resolve().parent / "data" / "access_state.json"


def _require_approval_env() -> bool:
    v = os.getenv("ACCESS_REQUIRE_APPROVAL", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def admin_user_ids() -> list[int]:
    raw = os.getenv("ADMIN_USER_IDS", "")
    return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


def access_gate_enabled() -> bool:
    """Включён ли режим заявок и заданы ли админы (без админов режим отключается)."""
    if not _require_approval_env():
        return False
    if not admin_user_ids():
        return False
    return True


def approval_config_warning() -> Optional[str]:
    """Сообщение для лога, если в .env заявки включены без списка админов."""
    if _require_approval_env() and not admin_user_ids():
        return (
            "ACCESS_REQUIRE_APPROVAL включён, но ADMIN_USER_IDS пуст — "
            "режим заявок отключён, бот доступен всем."
        )
    return None


def _load() -> dict:
    if not _STATE_PATH.exists():
        return {"approved": [], "pending": []}
    try:
        with open(_STATE_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"approved": [], "pending": []}
    data.setdefault("approved", [])
    data.setdefault("pending", [])
    data["approved"] = [int(x) for x in data["approved"]]
    data["pending"] = [int(x) for x in data["pending"]]
    return data


def _save(data: dict) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _STATE_PATH.with_suffix(".tmp")
    with _STATE_LOCK:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(_STATE_PATH)


def user_has_access(user_id: int) -> bool:
    if not access_gate_enabled():
        return True
    if user_id in admin_user_ids():
        return True
    return user_id in _load()["approved"]


def is_admin(user_id: int) -> bool:
    return user_id in admin_user_ids()


def register_pending(user_id: int) -> bool:
    """
    Помечает пользователя как ожидающего доступа.
    Возвращает True, если это первый раз — нужно уведомить админов.
    """
    with _STATE_LOCK:
        data = _load()
        if user_id in data["approved"]:
            return False
        if user_id in data["pending"]:
            return False
        data["pending"].append(user_id)
        _save(data)
        return True


def approve_user(user_id: int) -> bool:
    """Одобрить заявку. True, если доступ выдан впервые (можно уведомить пользователя)."""
    with _STATE_LOCK:
        data = _load()
        if user_id in data["pending"]:
            data["pending"].remove(user_id)
        if user_id in data["approved"]:
            _save(data)
            return False
        data["approved"].append(user_id)
        _save(data)
        return True


def list_pending() -> list[int]:
    return list(_load()["pending"])


def revoke_user(user_id: int) -> bool:
    """Снять доступ (для /revoke)."""
    with _STATE_LOCK:
        data = _load()
        changed = False
        if user_id in data["approved"]:
            data["approved"].remove(user_id)
            changed = True
        if user_id in data["pending"]:
            data["pending"].remove(user_id)
            changed = True
        if changed:
            _save(data)
        return changed
