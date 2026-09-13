# STOCK02 — 借金でオルカンを買った結果

金融ショートのストック2。完成45.03秒／1080×1920／30fps。VOICEVOXずんだもん・四国めたん。

## 再現

1. この専用ブランチを取得し、Pythonに`numpy scipy Pillow fonttools`、システムに`ffmpeg`と`ffprobe`を用意する。
2. `assets/audio/README.md`の公式BGMを取得する。台詞のFLACと発音情報は`output/`に保存済み。
3. `python retime.py`で保存されたFLACから動画用のWAV・タイムラインを作成する。
4. `python render.py --preview`、`python audio_design.py`、`python render.py`、`python finalize.py`、`python verify.py`、`python package_docs.py`の順に実行する。
5. `../deliverables/`に投稿動画・スマホ版・投稿文・字幕等ができる。サムネイルの完成JPEGは別途納品している。

`assets/*.webp`はPNG原画からピクセルを変えずに圧縮した画像。描画コードはPNGがない場合にWebPを読む。原画PNGとWebPのRGBA画素が一致することを確認済み。数字用フォントのサブセットは必要な数字・記号のみに限定。日本語用RocknRollOneはリポジトリ内の既存フォントを継承。

## 音声を変える場合

VOICEVOX Engine 0.25.2をlocalhost:50021で起動し、`script.json`を更新して`python synthesize.py`。原音WAVをFLACへ変換した後に上記の再現手順を行う。GitHub Actionsを使う場合は、このブランチで音声の入力変更をコミットし、コミットメッセージに`[stock02-audio]`を含める。新しい発音情報も保存する。完成済み映像を部分的に継ぎ足さず、全編を再描画する。

## 制作上の確認

- 100万円＋借入200万円の架空の投資。10％下落・売却で270万円、借入を差し引いた自己資金70万円。利息等は別。
- オルカン自体が3倍型の商品だとは説明しない。強制決済や追証の仕組みは持ち込まない。
- 全文字幕の初出と切替を発音情報に合わせ、口は最終音声の音量に同期。
- 画面下360pxは背景のみ。右専用の余白なし。左めたん・右ずんだもん、向きは内向き。
- 正確な額はカウントダウン途中値を表示せず、発音時点に確定値で出す。

詳しい企画と一次資料は`research.md`、視聴維持対策は`retention-rules.md`、機械検査は`output/verification.json`。一般の視聴者による実聴・面白さ・維持率改善を技術検査で実証したとはしない。

## クレジット

音声：VOICEVOX：ずんだもん／四国めたん。立ち絵：坂本アヒル。既存FZ030Rの制作済み立ち絵と元の口差分を継承。元PSD等の素材一式を再配布するものではない。
背景・サムネイル：本作品用AI生成画像。効果音：本作品用に合成。
Fluffing a Duck / Kevin MacLeod (incompetech.com), CC BY 4.0。
https://creativecommons.org/licenses/by/4.0/
https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100768
音楽原音源・音楽単独ステムはリポジトリへ含めない。ライセンスと公式取得先を参照する。
