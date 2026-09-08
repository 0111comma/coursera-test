#!/bin/bash
# 焼きの見張りつき起動(2026-09-08 ユーザー「止まらないようにするにはどうするべき?
# なぜ止まっても感知できずに私から今何してるのと聞かれて動き出すの?」)。
#
# それまでの焼き方は `nohup python3 render.py &` だった。これだと:
#   1. render.py は正常時に何も出さないので、**ログが0バイトのとき
#      「順調」と「死んだ」が区別できない**
#   2. VOICEVOX が落ちると TTS がそこで止まり、誰も気づかない
#   3. 終了を待つ仕掛けを付けずにターンを終えていたので、
#      ユーザーに聞かれるまで結果を見に行かなかった
#
# このスクリプトは:
#   - VOICEVOX が応答するまで起こしてから焼き始める
#   - shortlib の [tts]/[draw] の進捗行が STALL 秒増えなければ**固まったと見なす**
#     (プロセスが生きていても止まりは止まり)
#   - 固まったら殺して VOICEVOX を起こし直し、**フレームを残したまま再開**する
#     (render.py の [resume] 機構。描いた分は捨てない)
#   - 最大 RETRY 回まで。それでも駄目なら**非0で終わる**(黙って終わらない)
#
#   bash production/bake.sh videos/Z002-yotei-hitotsu /path/to/bake.log
#
# 呼ぶ側は必ず Bash(run_in_background) か Monitor で終了を待つこと。
# 待たずにターンを終えると、また「今何してるの」と聞かれる側に戻る。
set -u
VDIR="${1:?使い方: bash production/bake.sh videos/<ID>-<slug> [ログ]}"
LOG="${2:-/tmp/bake_$(basename "$VDIR").log}"
HERE="$(cd "$(dirname "$0")" && pwd)"
STALL="${BAKE_STALL_SEC:-420}"     # 進捗行が増えない上限(描画1カットは数十秒かかる)
RETRY="${BAKE_RETRY:-3}"
POLL=30

wake_voicevox() {
  for _ in $(seq 1 10); do
    curl -s -m 5 http://127.0.0.1:50021/version >/dev/null 2>&1 && return 0
    echo "[bake] VOICEVOX が応答しない。起こす" >> "$LOG"
    bash "$HERE/setup_voicevox.sh" >> "$LOG" 2>&1
    sleep 15
  done
  curl -s -m 5 http://127.0.0.1:50021/version >/dev/null 2>&1
}

for attempt in $(seq 1 "$RETRY"); do
  wake_voicevox || { echo "[bake] VOICEVOX を起こせない" >> "$LOG"; exit 3; }
  echo "[bake] $(date -Is) 開始 (試行 $attempt/$RETRY) $VDIR" >> "$LOG"
  python3 -u "$VDIR/render.py" >> "$LOG" 2>&1 &
  PID=$!
  last_count=-1; last_move=$(date +%s)
  while kill -0 "$PID" 2>/dev/null; do
    sleep "$POLL"
    now=$(date +%s)
    count=$(grep -c '^\[\(tts\|draw\)\]' "$LOG" 2>/dev/null || echo 0)
    if [ "$count" != "$last_count" ]; then
      last_count=$count; last_move=$now
    elif [ $((now - last_move)) -ge "$STALL" ]; then
      echo "[bake] $(date -Is) ${STALL}秒 進捗が止まった。殺して再開する" >> "$LOG"
      kill -9 "$PID" 2>/dev/null
      wait "$PID" 2>/dev/null
      break
    fi
  done
  wait "$PID" 2>/dev/null; rc=$?
  MP4=$(ls "$VDIR"/output/*.mp4 2>/dev/null | head -1)
  if [ "$rc" = 0 ] && [ -n "$MP4" ]; then
    echo "[bake] $(date -Is) 完了 $MP4" >> "$LOG"
    exit 0
  fi
  echo "[bake] $(date -Is) 失敗 rc=$rc。フレームを残したまま再開する" >> "$LOG"
done
echo "[bake] $(date -Is) ${RETRY}回とも駄目だった。人が見る番" >> "$LOG"
exit 1
