# Play33 Alert Bot

Play33 예약 페이지를 날짜별로 비교해서, 목표 날짜의 새 예약 가능 시간을 텔레그램으로 알려주는 봇입니다.

## 구조
- `target-date`: 감시할 날짜
- `reference-date`: 비교 기준 날짜
- `branch`: 매장 번호

예를 들어 `2026-06-03`과 `2026-06-02`를 비교하면, 6월 3일에만 새로 열린 시간대를 찾습니다.

## 설치
```bash
cd ~/Play33_alert_bot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```

## 환경 변수
`.env.example`을 `.env`로 복사한 뒤 값을 넣습니다.

필수:
- `TARGET_DATE`
- `REFERENCE_DATE`
- `BRANCH`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

선택:
- `POLL_INTERVAL_SECONDS`
- `BASE_URL`
- `USER_AGENT`
- `LOG_LEVEL`

## 실행
```bash
python -m play33_alert_bot
```

## 한 번만 비교
```bash
python -m play33_alert_bot.play33 --target-date 2026-06-03 --reference-date 2026-06-02 --branch 4
```

## 알림 방식
- 목표 날짜에서 새로 열린 시간이 있으면 텔레그램 전송
- 기본적으로 매 폴링마다 다시 비교
