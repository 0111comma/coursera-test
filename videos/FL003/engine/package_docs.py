from pathlib import Path
import os,json
from calculations import calculate
R=Path(os.environ['FINANCE_PROJECT']);D=R/'deliverables';O=R/'output'
C=json.loads((R/'project.json').read_text());S=json.loads((O/'timeline.json').read_text());P=json.loads((O/'caption-pages.json').read_text());V=json.loads((O/'verification.json').read_text())
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(D/'FL003-subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(p['start_frame']/30)} --> {stamp((p['end_frame']+1)/30)}\n{p['text']}" for i,p in enumerate(P))+'\n')
script=f"# {C['title']}\n\n完成尺：{V['duration_seconds']:.2f}秒。\n\n|開始秒|話者|セリフ|演技|\n|---:|---|---|---|\n"
for s in S:script+=f"|{s['start']:.2f}|{'ずんだもん' if s['speaker']==3 else '四国めたん'}|{s['text']}|{s['emotion']}|\n"
(D/'FL003-script.md').write_text(script)
description='''送料500円を払いたくなくて、1,000円の置物を追加したずんだもん。
送料無料にはなったけれど、支払う合計額は……？

【今回の買い物例】
架空のお店で、税込5,000円以上の購入なら送料無料という設定です。
購入予定の商品：4,000円
送料：500円
買う予定のなかった置物：1,000円

商品だけ買う：4,000円＋送料500円＝4,500円
置物を追加する：4,000円＋1,000円＋送料0円＝5,000円
差額：5,000円−4,500円＝500円

送料は0円になっても、不要な物を追加すると支出は500円増えます。
もともと買う予定の物を追加するなら、まとめ買いが合理的な場合もあります。今回は不要な物を買い足す場合の比較です。
送料無料の条件だけでなく、商品の必要性と支払総額を確認しましょう。
実際の店舗・キャンペーンの案内ではありません。金額は上記の設定に基づく独自計算です。

音声：VOICEVOX：ずんだもん／四国めたん
立ち絵：坂本アヒル（既存の正規立ち絵・口差分を継承）
背景・置物・サムネイル：本動画用に新規AI生成
効果音：本動画用に制作

"Fluffing a Duck" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0
https://creativecommons.org/licenses/by/4.0/
https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100768
音楽は尺に合わせたカット、音量調整、ダッキング、フェードを行っています。

#ずんだもん #送料無料 #家計管理 #お金の勉強 #節約 #shorts
'''
(D/'FL003-description.txt').write_text(description)
tags='ずんだもん,四国めたん,送料無料,家計管理,金融リテラシー,お金の勉強,節約,ネットショッピング,買い物,shorts'
comment='送料無料にするために、買う予定のなかった物を追加したことはありますか？ 今回は不要な置物を買い足した例です。もともと必要な物のまとめ買いとは分けて考えてみてください。'
kit=f'''# FL003 投稿セット

投稿用動画：FL003-free-shipping.mp4（1080×1920／30fps／{V['duration_seconds']:.2f}秒）
スマホ確認版：FL003-mobile.mp4
サムネイル：FL003-thumbnail.png

## タイトル

{C['title']}

## 概要欄（コピー用）

```text
{description}```

## タグ

{tags}

## 固定コメント案

{comment}

## 投稿設定

カテゴリ：教育
言語：日本語
対象：一般向け金融教育（子ども向けではない）
公開日時：未設定。ユーザーが手動で投稿。
全文字幕は映像に焼き込み済み。別途FL003-subtitles.srtを添付。

## 公開後の確認

冒頭の視聴継続率と平均視聴率を分けて確認。金額比較、短い驚き、弱く落とす結末で離脱がどう変わるかを見る。現時点で維持率改善を測定したものではありません。
'''
(D/'FL003-posting-kit.md').write_text(kit)
record=f'''# FL003 制作記録

{C['title']}

完成尺：{V['duration_seconds']:.2f}秒。{V['frames']}フレーム。1080×1920、30fps。
字幕：全文{V['caption_pages']}ページ、音声の演技区間に同期。数字はVOICEVOXの発音開始時刻を参照。
キャラクター：左が四国めたん、右がずんだもん。既存の坂本アヒル立ち絵と口差分。声量で口パクを同期。
声：ツンツンの不満→得意げ→一度だけ驚き→ヘロヘロの小声。説明は速度1.08〜1.14中心。
音楽：Fluffing a Duck / Kevin MacLeod、122 BPM。全編でBGMを継続し、驚きと小声では音量を下げる。
新規画像：背景2枚、置物1枚、サムネイル1枚。imagegenによる生成。背景全面、下360pxは背景のみ。

## 計算

```json
{json.dumps(calculate(),ensure_ascii=False,indent=2)}
```

## 検証

投稿版・スマホ版を全編デコード。映像時刻、全文字幕一致、切替前後{V['boundary_frames_compared']}フレームを描画元と照合。下360pxに字幕や立ち絵がないことを全フレームで検査。完成映像から切り出した各字幕ページを目視。
機械検査を、人による実聴や視聴維持率改善の実証とは扱っていません。

```json
{json.dumps(V['files'],ensure_ascii=False,indent=2)}
```

## 制作元

GitHub: 0111comma/coursera-test / codex/fl003-free-shipping-20260914
台本とVOICEVOX音声・発音時刻は同ブランチに保存。
'''
(D/'FL003-production-record.md').write_text(record)
print('FL003 posting kit, captions, script and record ready')
