#!/bin/bash
# VOICEVOX エンジンの番人。**落ちたら立て直す。**
#
# 2026-09-07: エンジンが焼きの途中で2回落ち、そのたびに render.py が静かに止まった。
# render.py は正常時に何も出さないので、**ログが0バイトでは「順調」と「死んでいる」の
# 区別がつかない**。焼きは1本1時間かかるので、黙って死ぬのがいちばん高くつく。
#
#   bash production/voicevox_keepalive.sh &     # 番人を常駐させる
#
# 30秒ごとに /version を叩き、応答が無ければ setup_voicevox.sh で起こし直す。
# 起こし直した回数は $LOG に残す(焼きが中断した原因を後から数えられるように)。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="${VV_KEEPALIVE_LOG:-/tmp/vv_keepalive.log}"
while true; do
  if ! curl -s -m 5 http://127.0.0.1:50021/version >/dev/null 2>&1; then
    echo "$(date -Is) エンジンが応答しない。起こし直す" >> "$LOG"
    bash "$HERE/setup_voicevox.sh" >> "$LOG" 2>&1
    sleep 20
  fi
  sleep 30
done
