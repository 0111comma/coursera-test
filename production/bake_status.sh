#!/bin/bash
# 焼きの現況を、記憶ではなく**ファイルとプロセスから**言う(2026-09-08 U19)。
#
# 「状況を教えて」に、私はログを見ずに「焼いています」と答えていた。
# ログが0バイトのとき順調と死亡が区別できなかったのが原因なので、
# **ユーザーに現況を報告する前に、必ずこれを走らせる**。
#
#   bash production/bake_status.sh            # videos/ 配下ぜんぶ
#   bash production/bake_status.sh videos/Z002-yotei-hitotsu
#
# 判定は3つの事実だけで決める(mp4 の有無だけで「完了」と言わない。
# 古い mp4 が残っている上に焼き直していることがあるため):
#   1. その render.py を回しているプロセスが居るか(pgrep -f。起動の仕方に依らない)
#   2. いちばん新しいフレームが何秒前か(進んでいるか固まっているか)
#   3. mp4 が最新フレームより新しいか(今回の焼きの成果物か)
set -u
now=$(date +%s)
if [ "$#" -gt 0 ]; then DIRS=("$@"); else mapfile -t DIRS < <(ls -d videos/*/ 2>/dev/null); fi
for VDIR in "${DIRS[@]}"; do
  VDIR="${VDIR%/}"; OUT="$VDIR/output"
  [ -d "$OUT" ] || continue
  MP4=$(ls -t "$OUT"/*.mp4 2>/dev/null | head -1)
  NEWEST=$(ls -t "$OUT"/work/frame_*.png 2>/dev/null | head -1)
  frames=$(ls "$OUT"/work/frame_*.png 2>/dev/null | wc -l)
  PID=$(pgrep -f "python3 -u $VDIR/render.py" | head -1)
  GATE=$(pgrep -f "check_all.py $VDIR" | head -1)
  age=""; [ -n "$NEWEST" ] && age=$(( now - $(date +%s -r "$NEWEST") ))

  if [ -n "$GATE" ]; then
    state="ゲートを通している(焼く前 pid=$GATE)"
  elif [ -n "$PID" ]; then
    if [ -z "$age" ]; then state="開始直後(まだフレームなし pid=$PID)"
    elif [ "$age" -ge 420 ]; then state="固まっている疑い(${age}秒 フレームが増えない pid=$PID)"
    else state="焼いている(${age}秒前にフレーム pid=$PID)"; fi
  elif [ -n "$NEWEST" ] && { [ -z "$MP4" ] || [ "$NEWEST" -nt "$MP4" ]; }; then
    state="落ちている(プロセスが居ないのに未完のフレームが残っている)"
  elif [ -n "$MP4" ]; then
    state="完了"
  else
    state="焼いていない"
  fi
  printf "%-34s %s / フレーム%s枚 / mp4=%s\n" "$(basename "$VDIR")" "$state" "$frames" "${MP4:-なし}"
done
