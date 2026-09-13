from pathlib import Path
import json,math,shutil,hashlib,re
R=Path(__file__).resolve().parent;O=R/'output';D=R.parent/'deliverables';D.mkdir(exist_ok=True)
S=json.loads((O/'timeline.json').read_text());P=json.loads((O/'caption-pages.json').read_text());V=json.loads((O/'verification.json').read_text())
duration=V['duration_seconds']; frames=V['frames']; utterances=V['utterances']; pages=V['caption_pages']
loudness=json.loads(re.search(r'\{[\s\S]*\}',(O/'audio-loudness.txt').read_text()).group())
title='借金でオルカンを買い増したずんだもん、自己資金が３割消える'
description='''「世界中に投資してるから大丈夫！」
自分の100万円に、借りた200万円を上乗せしてオルカンを購入。
ところが10％下落。売却代金270万円を見て安心しかけたずんだもんですが……。

今回のポイントは、投資先を分散しても、借金で投資額を増やせば自己資金に対する損失も大きくなること。

【動画の計算／すべて架空の例】
自己資金100万円＋借入200万円＝投資額300万円
10％下落して売却：300万円×90％＝270万円
借入元本を差し引く：270万円−200万円＝70万円
自己資金は100万円から70万円へ。損失率は30％。
借入利息・手数料・税金等を除いた単純化した比較で、利息等を払えば残額はさらに少なくなります。

10％は損失の増え方を比較するための仮定です。期間は特定せず、実際の運用実績・将来予測・平均的な下落率を表していません。
ここでのレバレッジは「本人が借入で投資額を増やす」意味です。オルカン自体を3倍型の商品として扱う動画ではありません。特定の借入サービスを紹介・推奨するものでもありません。
投資信託の売却代金は注文と同時に入金されるものではないため、動画でも「売却・入金後」と時間を分けています。

【出典／確認日：2026年9月13日】
三菱UFJアセットマネジメント
eMAXIS Slim 全世界株式（オール・カントリー）
https://emaxis.am.mufg.jp/fund/253425.html
2026年7月月報
https://www.am.mufg.jp/pdf/geppou/253425/253425_202607.pdf
交付目論見書（2026年7月25日）
https://www.am.mufg.jp/pdf/seimokuromi/253425/253425_20260725.pdf

音声：VOICEVOX：ずんだもん／四国めたん
立ち絵：坂本アヒル（既存制作素材の正規立ち絵・口差分を継承）
背景・サムネイル：本動画用のAI生成画像
効果音：本動画用に制作

"Fluffing a Duck" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0
https://creativecommons.org/licenses/by/4.0/
https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100768
音楽は尺に合わせたカット・ループ・音量調整を行っています。

#オルカン #ずんだもん #レバレッジ #金融リテラシー #shorts
'''
tags='オルカン,オールカントリー,全世界株式,eMAXIS Slim,レバレッジ,借金投資,投資信託,投資の失敗,相場下落,狼狽売り,損失,資産形成,金融リテラシー,ずんだもん,四国めたん,VOICEVOX,ショート,shorts'
(D/'STOCK02-description.txt').write_text(description)
kit=f'''# STOCK02 投稿セット

## タイトル

{title}

## 概要欄

{description}
## タグ

{tags}

## 投稿設定

- 形式：縦1080×1920、30fps、{duration:.2f}秒
- 動画：STOCK02-orukan-leverage.mp4
- スマホ確認用：STOCK02-mobile.mp4（540×960）
- サムネイル：STOCK02-thumbnail.jpg
- 言語：日本語
- カテゴリ：教育
- 子ども向け：いいえ（成人の投資・借入を扱う内容）
- 公開状態：未投稿。公開・予約は行っていません。
- 固定コメント案：投資先を分散しても、借金は減らない。今回は自己資金100万円に借入200万円を加えた架空の例です。
'''
(D/'STOCK02-posting-kit.md').write_text(kit)
def tc(frame):
    ms=round(frame/30*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
(D/'STOCK02-subtitles.srt').write_text('\n'.join(f"{k+1}\n{tc(x['start_frame'])} --> {tc(x['end_frame']+1)}\n{x['text']}\n" for k,x in enumerate(P)))
md=['# STOCK02 確定台本','',f'{duration:.2f}秒／縦1080×1920／ストック2／未投稿','']
for x in S:
    md.append(f"- **{x['start']:.2f}秒：{x['title']}**"+(f"（{x['subtitle']}）" if x.get('subtitle') else '') if x.get('kind') else f"- {x['start']:.2f}秒　{'ずんだもん' if x['speaker']==3 else '四国めたん'}：{x['text']}")
(D/'STOCK02-script.md').write_text('\n'.join(md)+'\n')
record=f'''# STOCK02 制作記録

ユーザー指定：オルカン×レバレッジ。制作日：2026年9月13日。未投稿。

完成：{duration:.2f}秒、1080×1920、30fps、{frames:,}フレーム。スマホ版は540×960。
VOICEVOXずんだもん・四国めたん、{utterances}発話、{pages}ページの全文字幕。

## 引き継ぎと今回の変更

- FZ030R-production.zipの日本語修正版を取得し、保存時SHA-256と全98項目CRC一致を確認してから、既存の正規立ち絵・開口閉口差分・書体と画面ルールを継承。
- 新しい台本と音声、朝・下落時・売却後の３背景、作品専用サムネイルを制作。前作と別BGM、出来事に対応した12のSE。
- 音声生成はGitHub Actionsで成功。合成かなを全発話点検し、金額が続く発話だけ音程を変えずに減速。口は最終音声のフレームごとの音量に同期。
- 中間離脱対策：冒頭で借金による買い増しを示し、前半に下落、後半に売却代金と借入残高の差を発見する展開。具体的な反応と行動で終える。
- 字幕・数字・効果音を発音時刻へ同期。金額は発音時点で確定値を表示し、大きさや棒の長さを動かす演出を継承。
- 今回の修正：根拠のない期間指定を外し、10％下落の仮定に変更。売却270万円・借金控除後70万円・自己資金の損失30％に統一。締めは「お金の失敗を減らしたい人は、チャンネル登録を！」。
- 制作ソースと必要素材は[GitHubの専用ブランチ](https://github.com/0111comma/coursera-test/tree/codex/stock02-orukan-leverage-20260913/videos/STOCK02)に保存する。STOCK02の納品ファイルを修正版に更新する。

## 検査

- 投稿版・スマホ版の全編デコード成功。フレーム数{frames:,}、時刻は1/30秒刻み。
- {utterances}発話・全{pages}字幕ページで台本と表示全文が一致。完成MP4から全字幕ページを抽出して、文字欠け・語尾・行間・読みやすさを目視。
- 全{V['boundaries']}境界の前後最大3フレーム、合計{V['boundary_frames_compared']}フレームを完成MP4と描画元で比較。平均画素差の最大は{V['maximum_mean_pixel_error']:.3f}/255。
- 全フレームで下360pxへ前景を置かないことを描画時に検証。左右配置・内向き・全身・原画の口差分を確認。
- 300×90％=270、270−200=70、自己資金の損失率30％を検算。架空の下落例・利息等除外を画面に表示。
- 音声の実測：{loudness['input_i']} LUFS、真のピーク{loudness['input_tp']} dBFS。BGMは連続させ、原曲中の区切りを避けたループを使用。

## 確認の範囲

音声のかな、発音時刻、音量、口パク、完成映像の字幕・画面を確認。人間相当の実聴評価を実施済みとはしない。視聴維持率の改善やユーザーによる面白さの採用判定はまだ得られていない。

## 完成ファイル

|ファイル|バイト数|SHA-256|
|---|---:|---|
'''
for name,item in V['files'].items():record+=f"|{name}|{item['size']}|{item['sha256']}|\n"
(D/'STOCK02-production-record.md').write_text(record)
print('Posting kit, description, subtitles, script and production record prepared')
