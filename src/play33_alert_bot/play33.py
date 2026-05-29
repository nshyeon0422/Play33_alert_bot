from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)
DEFAULT_BASE_URL = "https://play33.kr/reservation"
TIME_RE = re.compile(r"\d{2}:\d{2}")


@dataclass(frozen=True)
class Play33Slot:
    time: str
    enabled: bool
    label: str
    class_name: str
    hidden_data: Optional[dict[str, object]]


@dataclass(frozen=True)
class Play33Snapshot:
    url: str
    branch: Optional[int]
    date: Optional[str]
    slots: tuple[Play33Slot, ...]

    @property
    def open_times(self) -> tuple[str, ...]:
        return tuple(slot.time for slot in self.slots if slot.enabled)

    @property
    def closed_times(self) -> tuple[str, ...]:
        return tuple(slot.time for slot in self.slots if not slot.enabled)


@dataclass(frozen=True)
class Play33Diff:
    target: Play33Snapshot
    reference: Play33Snapshot
    newly_open_times: tuple[str, ...]
    newly_closed_times: tuple[str, ...]


def build_reservation_url(branch: int, date: str, base_url: str = DEFAULT_BASE_URL) -> str:
    return f"{base_url}?branch={branch}&date={date}#content"


def fetch_html(url: str, user_agent: str = "Mozilla/5.0") -> str:
    with requests.Session() as session:
        response = session.get(url, headers={"User-Agent": user_agent}, timeout=20)
        response.raise_for_status()
        return response.text


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _extract_time(button, hidden_data: Optional[dict[str, object]]) -> str:
    if hidden_data:
        time_value = hidden_data.get("time")
        if isinstance(time_value, str) and time_value.strip():
            return time_value.strip()

    span = button.find("span")
    if span:
        match = TIME_RE.search(span.get_text(" ", strip=True))
        if match:
            return match.group(0)

    text = _normalize_text(button.get_text(" ", strip=True))
    match = TIME_RE.search(text)
    if match:
        return match.group(0)

    return text


def parse_snapshot(html: str, url: str) -> Play33Snapshot:
    soup = BeautifulSoup(html, "html.parser")
    slots: list[Play33Slot] = []

    for button in soup.select("button"):
        class_name = " ".join(button.get("class", []))
        button_text = _normalize_text(button.get_text(" ", strip=True))
        hidden = button.select_one(".eveHiddenData")
        hidden_data: Optional[dict[str, object]] = None
        if hidden:
            raw_hidden = _normalize_text(hidden.get_text(" ", strip=True))
            try:
                hidden_data = json.loads(raw_hidden)
            except json.JSONDecodeError:
                hidden_data = None

        time_value = _extract_time(button, hidden_data)
        if not time_value:
            continue

        if not (button_text.startswith("예약") or hidden_data is not None or "eveReservationButton" in class_name):
            continue

        enabled = not button.has_attr("disabled") and ("eveReservationButton" in class_name or button_text.startswith("예약 가능"))
        slots.append(
            Play33Slot(
                time=time_value,
                enabled=enabled,
                label=button_text,
                class_name=class_name,
                hidden_data=hidden_data,
            )
        )

    branch: Optional[int] = None
    date: Optional[str] = None
    first_hidden = next((slot.hidden_data for slot in slots if slot.hidden_data), None)
    if first_hidden:
        branch_value = first_hidden.get("branch")
        date_value = first_hidden.get("date")
        if isinstance(branch_value, int):
            branch = branch_value
        elif isinstance(branch_value, str) and branch_value.isdigit():
            branch = int(branch_value)
        if isinstance(date_value, str):
            date = date_value

    return Play33Snapshot(url=url, branch=branch, date=date, slots=tuple(slots))


def compare_snapshots(target: Play33Snapshot, reference: Play33Snapshot) -> Play33Diff:
    target_open = set(target.open_times)
    reference_open = set(reference.open_times)
    return Play33Diff(
        target=target,
        reference=reference,
        newly_open_times=tuple(sorted(target_open - reference_open)),
        newly_closed_times=tuple(sorted(reference_open - target_open)),
    )


def fetch_snapshot(url: str, user_agent: str = "Mozilla/5.0") -> Play33Snapshot:
    return parse_snapshot(fetch_html(url, user_agent=user_agent), url=url)


def main() -> None:
    parser = argparse.ArgumentParser(description="Play33 reservation comparer")
    parser.add_argument("--branch", type=int, default=4, help="Branch number (default: 4)")
    parser.add_argument("--target-date", required=True, help="Target date in YYYY-MM-DD")
    parser.add_argument("--reference-date", help="Reference date in YYYY-MM-DD")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base reservation URL")
    parser.add_argument("--user-agent", default="Mozilla/5.0", help="User-Agent for requests")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    target_url = build_reservation_url(args.branch, args.target_date, base_url=args.base_url)
    target_snapshot = fetch_snapshot(target_url, user_agent=args.user_agent)
    LOGGER.info("Target URL: %s", target_url)
    LOGGER.info("Open times: %s", ", ".join(target_snapshot.open_times) or "-")

    if args.reference_date:
        reference_url = build_reservation_url(args.branch, args.reference_date, base_url=args.base_url)
        reference_snapshot = fetch_snapshot(reference_url, user_agent=args.user_agent)
        diff = compare_snapshots(target_snapshot, reference_snapshot)
        LOGGER.info("Reference URL: %s", reference_url)
        LOGGER.info("Reference open times: %s", ", ".join(reference_snapshot.open_times) or "-")
        LOGGER.info("Newly open times: %s", ", ".join(diff.newly_open_times) or "-")
        LOGGER.info("Newly closed times: %s", ", ".join(diff.newly_closed_times) or "-")


if __name__ == "__main__":
    main()
