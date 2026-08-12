---
name: produce-video
description: 台本済みの動画(videos/<ID>-<slug>/script.md)からmp4をレンダリングする。動画IDを引数で指定。VOICEVOXのセットアップ、render.pyの作成、フレームの目視確認、mp4生成までを行う。
---

# 動画制作(/produce-video)

台本を 1080x1920・30fps のショート動画(mp4)にレンダリングする。

## 前提セットアップ(セッションごとに1回)

1. `ffmpeg` がなければ `apt-get update && apt-get install -y ffmpeg`
2. Pythonライブラリ: `pip3 install matplotlib pillow`
3. VOICEVOX: `bash production/setup_voicevox.sh`(ダウンロード済みなら起動のみ。約2GB)
   - 起動確認: `curl -s 127.0.0.1:50021/version`
   - VOICEVOXが使えない環境では Open JTalk にフォールバックする(shortlibが自動判定)

## 手順

1. 対象の `videos/<ID>-<slug>/script.md` と `plan.md` を読む
2. `verify.py` を実行し、台本の数値と一致することを確認する(不一致なら制作を止めて報告)
3. `videos/<ID>-<slug>/render.py` を書く(既存の `videos/S001-tsumitate-fukuri/render.py` が参考実装):
   - `production/shortlib.py` の `Unit` / `render_video` を使う
   - 台本の表の1行 ≒ 1ユニット(長い行は文単位に分割してよい。字幕は15字で折り返される)
   - シーン(画面指示)ごとに描画関数を書く。数値は台本からコピーせず、verify.pyと同じ式で計算して `assert` で照合する
   - グラフの配色は shortlib のトークン(SERIES_1, SERIES_2, INK, ...)のみ使う(検証済みパレット)
4. `python3 videos/<ID>-<slug>/render.py` でレンダリングする
5. **フレームを目視確認する**: `output/work/frame_*.png` をReadで開き、文字の重なり・はみ出し・字幕の変な折り返しがないかチェック。問題があれば直して再レンダリング
6. 音量を確認する: `ffmpeg -i output/<ID>.mp4 -af volumedetect -f null -`(mean が -20〜-14dB 程度)
7. 完成したmp4をユーザーに送付し、`plan.md` と `ideas/backlog.md` のステータスを「制作済み」に更新する

## 守ること

- 尺: ショートは60秒以内(ナレーション合計+間で55秒目安)
- 音声のクレジット: VOICEVOX使用時は概要欄に「VOICEVOX:<キャラクター名>」を必ず入れる(既定は speaker=2 四国めたん)
- Shortsのセーフエリア: 重要情報は画面の左右8%・上部12%・下部20%を避ける(shortlibのヘルパを使えば自動で収まる)
- 動画内の数値は必ず verify.py と同じ計算式から生成する(手打ちコピーしない)
