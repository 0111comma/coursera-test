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

1. 対象の `videos/<ID>-<slug>/script.md` と `plan.md` を読む。**制作ルールは docs/research/short-video-format.md(R1〜R14)**
2. `verify.py` を実行し、台本の数値と一致することを確認する(不一致なら制作を止めて報告)
3. `videos/<ID>-<slug>/render.py` を書く(既存の `videos/S001-tsumitate-fukuri/render.py` が参考実装):
   - `production/shortlib.py` の `Unit` / `render_video` を使う。台本のユニット表の1行=1 `Unit`
   - シーン描画関数は `painter(fig, t)`(tは0→1)。`anim` 秒数を指定してカウントアップ・バー成長・線描画などの動きを入れる(R2/R4: 3秒以上静止させない)
   - 字幕の【】強調はそのまま渡す(黄色になる)。数値は台本からコピーせず、verify.pyと同じ式で計算して `assert` で照合する
   - グラフの配色は shortlib のトークン(SERIES_1, SERIES_2, INK, ...)のみ。テロップ強調は EMPH
   - BGMは自動で合成ミックスされる(R14)。話者は既定でずんだもん・話速1.2(R13/R5)
4. `python3 videos/<ID>-<slug>/render.py` でレンダリングする
4b. `python3 production/check_video.py videos/<ID>-<slug>` を実行し **ALL PASS** を確認する(不合格なら直して再実行)
5. **フレームを目視確認する**: `output/work/frame_*.png` をReadで開き(アニメ途中・最終フレームの両方)、文字の重なり・はみ出し・字幕の変な折り返しがないかチェック。問題があれば直して再レンダリング
6. 音量を確認する: `ffmpeg -i output/<ID>.mp4 -af volumedetect -f null -`(mean が -20〜-14dB 程度)
7. 完成したmp4をユーザーに送付し、`plan.md` と `ideas/backlog.md` のステータスを「制作済み」に更新する

## 守ること

- 尺: ショートは30〜50秒(密度優先、水増し禁止)
- 音声のクレジット: VOICEVOX使用時は概要欄に「VOICEVOX:<キャラクター名>」を必ず入れる(既定は speaker=3 ずんだもん)
- Shortsのセーフエリア: 重要情報は画面の左右8%・上部12%・下部20%を避ける(shortlibのヘルパを使えば自動で収まる)
- 動画内の数値は必ず verify.py と同じ計算式から生成する(手打ちコピーしない)

## 画面の単調さ対策(ループ71。ユーザー「画面構成飽きてきた」)

1. **カテゴリ色**: render.py の import 直後に `shortlib.set_accent(<カテゴリ>)` を呼ぶ。
   invest=NISA・投資(緑) / tax=税・取られる系(珊瑚) / save=貯金・預金(青) /
   pension=年金・老後(紫) / default=時事・その他(黄)。
   公開済み動画(S001〜)は触らない。色は動画単位で固定し、途中で変えない
2. **図の型を1本で3種類以上使う**。card・bars2 だけの構成にしない。
   scenes_common には hero / stack(積み上げ) / band(帯) / 株価チャート(price_path)が
   すでにあるのに使っていなかった。テーマに合う型を判定表(figure-forms.md)から選ぶ
3. カードは全ユニットの半分以下(check_figure の「図が足りない」が最低線)
