from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _parse_int(value: Optional[str], default: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Config:
    base_url: str
    branch: int
    target_date: str
    reference_date: Optional[str]
    poll_interval_seconds: int
    telegram_bot_token: str
    telegram_chat_id: str
    user_agent: str
    log_level: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            base_url=os.getenv("BASE_URL", "https://play33.kr/reservation").strip(),
            branch=_parse_int(os.getenv("BRANCH"), 4),
            target_date=os.getenv("TARGET_DATE", "").strip(),
            reference_date=os.getenv("REFERENCE_DATE") or None,
            poll_interval_seconds=_parse_int(os.getenv("POLL_INTERVAL_SECONDS"), 60),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
            user_agent=os.getenv("USER_AGENT", "Mozilla/5.0").strip(),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip(),
        )
