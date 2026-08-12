#!/bin/bash
# VOICEVOXエンジン(CPU版)のセットアップと起動。
# このリポジトリの作業環境(コンテナ)は使い捨てなので、新しいセッションで
# 動画を作るときは最初に一度これを実行する。
#   bash production/setup_voicevox.sh          # 未導入ならDL+展開してから起動
# 起動確認: curl -s 127.0.0.1:50021/version
#
# 音声を動画で使う場合は概要欄に「VOICEVOX:<キャラクター名>」のクレジットが必要。
# 話者ID一覧: curl -s 127.0.0.1:50021/speakers | python3 -m json.tool
set -euo pipefail

VERSION="0.25.2"
DIR="/opt/voicevox"
ENGINE="$DIR/linux-cpu-x64"

if [ ! -x "$ENGINE/run" ]; then
  mkdir -p "$DIR"
  cd "$DIR"
  echo "downloading VOICEVOX engine $VERSION ..."
  curl -sL --retry 3 -o engine.7z.001 \
    "https://github.com/VOICEVOX/voicevox_engine/releases/download/$VERSION/voicevox_engine-linux-cpu-x64-$VERSION.7z.001"
  command -v 7z >/dev/null || apt-get install -y p7zip-full
  7z x -y -bso0 -bsp0 engine.7z.001
  rm engine.7z.001
fi

if curl -s --max-time 3 127.0.0.1:50021/version >/dev/null 2>&1; then
  echo "engine already running"
else
  echo "starting engine on 127.0.0.1:50021 (initial startup takes ~60s)"
  cd "$ENGINE"
  nohup ./run --host 127.0.0.1 --port 50021 > /tmp/voicevox.log 2>&1 &
  for i in $(seq 1 60); do
    sleep 2
    if curl -s --max-time 3 127.0.0.1:50021/version >/dev/null 2>&1; then
      echo "engine up: $(curl -s 127.0.0.1:50021/version)"
      exit 0
    fi
  done
  echo "engine failed to start; see /tmp/voicevox.log" >&2
  exit 1
fi
