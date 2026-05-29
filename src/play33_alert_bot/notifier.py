from __future__ import annotations

import time
from dataclasses import dataclass

import requests


@dataclass
class TelegramNotifier:
    bot_token: str
    chat_id: str
    send_delay_seconds: int = 0

    def send_message(self, text: str) -> None:
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        response = requests.post(url, data=payload, timeout=20)
        response.raise_for_status()

        if self.send_delay_seconds > 0:
            time.sleep(self.send_delay_seconds)
