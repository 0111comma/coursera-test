#!/bin/bash
# レンダリングの見張り付き実行(ループ㊻)。
# VOICEVOXが落ちるとレンダリングは黙って死ぬ。3時間気づかなかった事故を受けて、
# 生存確認 → 落ちていたら再起動 → 最大3回まで再試行する。進捗は progress.txt に追記。
#
# 使い方: bash production/render_guarded.sh <video-dir-name>
#   ログの出力先は RENDER_LOG_DIR で変更できる(既定 /tmp/render-logs)
cd /home/user/coursera-test
LOGROOT="${RENDER_LOG_DIR:-/tmp/render-logs}"
V="$1"; ID="${V%%-*}"
LOG="$LOGROOT"; mkdir -p "$LOG"
for attempt in 1 2 3; do
  # VOICEVOXの生存確認。落ちていたら起動し直す
  if ! curl -s -m 5 http://127.0.0.1:50021/version >/dev/null 2>&1; then
    echo "$(date +%H:%M:%S) VOICEVOX再起動 (試行$attempt) $V" >> "$LOG/progress.txt"
    bash production/setup_voicevox.sh >/dev/null 2>&1
    sleep 5
  fi
  echo "$(date +%H:%M:%S) START $V (試行$attempt)" >> "$LOG/progress.txt"
  if python3 "videos/$V/render.py" > "$LOG/$V.log" 2>&1; then
    echo "$(date +%H:%M:%S) OK   $V" >> "$LOG/progress.txt"
    echo "$(date +%H:%M:%S) worker done: $V" >> "$LOG/progress.txt"
    exit 0
  fi
  echo "$(date +%H:%M:%S) FAIL $V (試行$attempt) — $(tail -1 "$LOG/$V.log" | cut -c1-120)" >> "$LOG/progress.txt"
done
echo "$(date +%H:%M:%S) GIVEUP $V" >> "$LOG/progress.txt"
echo "$(date +%H:%M:%S) worker done: $V" >> "$LOG/progress.txt"
