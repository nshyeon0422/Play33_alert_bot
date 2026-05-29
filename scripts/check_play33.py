import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from play33_alert_bot.play33 import fetch_snapshot, build_reservation_url

BRANCH = 4
TARGET_DATE = '2026-06-03'
REFERENCE_DATE = '2026-06-02'

base_url = 'https://play33.kr/reservation'

def print_snapshot(url):
    snap = fetch_snapshot(url)
    print(f"URL: {url}")
    print("Open times:", ', '.join(snap.open_times) or '-')
    print("All slots:")
    for s in snap.slots:
        print(f" - {s.time} | enabled={s.enabled} | label={s.label} | class={s.class_name}")
    print()

if __name__ == '__main__':
    target_url = build_reservation_url(BRANCH, TARGET_DATE, base_url=base_url)
    reference_url = build_reservation_url(BRANCH, REFERENCE_DATE, base_url=base_url)
    print_snapshot(reference_url)
    print_snapshot(target_url)

    # comparison
    t = fetch_snapshot(target_url)
    r = fetch_snapshot(reference_url)
    new = sorted(set(t.open_times) - set(r.open_times))
    closed = sorted(set(r.open_times) - set(t.open_times))
    print('Newly open times:', new or '-')
    print('Newly closed times:', closed or '-')
