from __future__ import annotations

import logging
import time

from dotenv import load_dotenv

from .config import Config
from .notifier import TelegramNotifier
from .play33 import build_reservation_url, compare_snapshots, fetch_snapshot


def format_alert_message(config: Config, newly_open_times: tuple[str, ...], reference_open_times: tuple[str, ...]) -> str:
    target_url = build_reservation_url(config.branch, config.target_date, base_url=config.base_url)
    reference_url = build_reservation_url(config.branch, config.reference_date, base_url=config.base_url) if config.reference_date else "-"
    return (
        "Play33 예약 알림\n"
        f"매장: {config.branch}\n"
        f"대상 날짜: {config.target_date}\n"
        f"비교 기준: {config.reference_date or '-'}\n"
        f"대상 URL: {target_url}\n"
        f"기준 URL: {reference_url}\n"
        f"열린 시간: {', '.join(newly_open_times) or '-'}\n"
        f"기준 열린 시간: {', '.join(reference_open_times) or '-'}"
    )


def run_once(config: Config, notifier: TelegramNotifier) -> None:
    target_url = build_reservation_url(config.branch, config.target_date, base_url=config.base_url)
    target_snapshot = fetch_snapshot(target_url, user_agent=config.user_agent)

    if config.reference_date:
        reference_url = build_reservation_url(config.branch, config.reference_date, base_url=config.base_url)
        reference_snapshot = fetch_snapshot(reference_url, user_agent=config.user_agent)
        diff = compare_snapshots(target_snapshot, reference_snapshot)
        newly_open_times = diff.newly_open_times
        reference_open_times = reference_snapshot.open_times
    else:
        newly_open_times = target_snapshot.open_times
        reference_open_times = tuple()

    logging.info("Target open times: %s", ", ".join(target_snapshot.open_times) or "-")
    if newly_open_times:
        notifier.send_message(format_alert_message(config, newly_open_times, reference_open_times))
        logging.warning("Alert sent: %s", ", ".join(newly_open_times))
    else:
        logging.info("No newly open times")


def main() -> None:
    load_dotenv()
    config = Config.from_env()
    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO))

    if not config.target_date:
        raise ValueError("TARGET_DATE is required")
    if not config.telegram_bot_token or not config.telegram_chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")

    notifier = TelegramNotifier(config.telegram_bot_token, config.telegram_chat_id)

    while True:
        try:
            run_once(config, notifier)
        except Exception:  # noqa: BLE001
            logging.exception("Polling error")

        time.sleep(max(config.poll_interval_seconds, 5))


if __name__ == "__main__":
    main()
