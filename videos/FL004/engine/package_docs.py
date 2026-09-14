from pathlib import Path
import os,json,shutil
from calculations import calculate
R=Path(os.environ['FINANCE_PROJECT']);D=R/'deliverables';O=R/'output'
C=json.loads((R/'project.json').read_text());S=json.loads((O/'timeline.json').read_text());P=json.loads((O/'caption-pages.json').read_text());V=json.loads((O/'verification.json').read_text());code=C['code']
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(D/f'{code}-subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(p['start_frame']/30)} --> {stamp((p['end_frame']+1)/30)}\n{p['text']}" for i,p in enumerate(P))+'\n')
script=f"# {C['title']}\n\n完成尺：{V['duration_seconds']:.2f}秒。\n\n|開始秒|話者|セリフ|演技|\n|---:|---|---|---|\n"
for s in S:script+=f"|{s['start']:.2f}|{'ずんだもん' if s['speaker']==3 else '四国めたん'}|{s['text']}|{s['emotion']}|\n"
(D/f'{code}-script.md').write_text(script)
if C['theme']=='fx':
 description='''「外貨預金で年利5％！」と喜んだずんだもん。
ドルでは増えたのに、円に戻したら元の100万円より少なくなっていた……？

【今回の仮の計算例】
元金：100万円
預け入れ時：1ドル150円
運用期間：1年間
利率：年利5％と仮定
引き出し時：1ドル135円と仮定
税金・為替手数料・実際の金融機関の端数処理は計算に含めません。
実在商品の金利紹介、実際に起きた値動き、将来の相場予測ではありません。

100万円 ÷ 150円 ＝ 約6,666.67ドル
正確な換算額に1年分の利息5％を加えると7,000ドル
7,000ドル × 135円 ＝ 945,000円
元の100万円との差：55,000円減
（計算途中ではドル残高を丸めずに計算しています）

利息でドル残高は5％増えても、1ドルの円換算額が150円から135円へ10％下がるため、円では元本割れする例です。
逆に円安なら円換算額が増えることもあります。外貨預金は、金利だけでなく為替変動や手数料を確認する必要があります。
また、外貨預金は日本の預金保険制度の保護対象外です。動画本編は為替リスクという1つの仕組みに絞っています。

【出典・確認日】2026年9月14日
三井住友銀行：外貨預金のメリットとデメリット
https://www.smbc.co.jp/kojin/money-viva/gaikayokin/0001/

'''
 tags='ずんだもん,四国めたん,外貨預金,為替リスク,円高,金利,元本割れ,金融リテラシー,お金の勉強,shorts'
 hashtags='#ずんだもん #外貨預金 #為替リスク #お金の勉強 #shorts'
 comment='「預金」という言葉だけで安心していませんか？ この動画は架空の条件です。ドルの残高と円での価値を分けて確認してみてください。'
 design='動画内は紺・シアン・金の両替ボードを維持。サムネは承認済みの明るいアニメ調と極太の縁取り文字に戻し、両替窓口でドルの貯金と円の残高に驚く大きなずんだもんを描く。'
else:
 description='''NISAで日本株の配当20万円をもらい、旅行に使うつもりのずんだもん。
ところが、銀行口座に入ったのは159,370円。なぜNISAなのに税金が引かれたのでしょう？

【今回の対象と仮の例】
NISA口座で保有する国内上場株式の配当金を、銀行口座で直接受け取る方法に設定していた場合の例です。大口株主等は対象外です。
配当金：200,000円
源泉徴収税率：20.315％（所得税等15.315％＋住民税5％）
源泉徴収額：40,630円
入金額：159,370円
タイトルとセリフの「4万円」は源泉徴収額の概数です。

【確認する設定】
国内上場株式等の配当をNISAで非課税にするには「株式数比例配分方式」で受け取る必要があります。証券会社の口座で受け取る方法です。
保有銘柄の配当基準日までに手続を終える必要があります。必要な日数や操作方法は証券会社で確認してください。
一度選択すると、他の証券会社や特定・一般口座の上場株式等にも同じ受取方式が適用されます。特別口座に株式がある場合など、利用できないケースもあります。
すでに課税で受け取った配当を、設定変更だけで遡ってNISA非課税にすることはできません。確定申告による配当控除等の扱いは、所得や申告方法により異なります。
通常の投資信託の分配金や外国株式の現地課税の説明ではありません。証券口座で受け取った後の銀行への振替・自動出金とも別の話です。

【出典・確認日】2026年9月14日
日本証券業協会：NISA口座における上場株式の配当金等受取方式に関する注意事項
https://www.jsda.or.jp/shijyo/seido/tax/nisahaitoukin.html
国税庁：NISA制度（No.1535）
https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1535.htm
国税庁：配当金を受け取ったとき（No.1330）
https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1330.htm

'''
 tags='ずんだもん,四国めたん,NISA,新NISA,日本株,配当金,株式数比例配分方式,税金,金融リテラシー,お金の勉強,shorts'
 hashtags='#ずんだもん #NISA #配当金 #お金の勉強 #shorts'
 comment='日本株をNISAで持っている人は、配当金の受取方法を確認してみてください。「株式数比例配分方式」が確認する設定です。手続きに必要な日数は証券会社によって異なります。'
 design='動画内は紙の配当明細の図解を維持。サムネは承認済みの明るいアニメ調と極太の縁取り文字に戻し、机で配当明細の税金に驚く大きなずんだもんと、受取設定を指摘するめたんを描く。'
description+=f'''音声：VOICEVOX：ずんだもん／四国めたん
立ち絵：坂本アヒル（既存の正規立ち絵・口差分を継承）
背景・サムネイル：本動画用に新規AI生成
効果音：本動画用に制作

"{C['bgm']}" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0
https://creativecommons.org/licenses/by/4.0/
{C['bgm_url']}
音楽は尺に合わせたカット、音量調整、ダッキング、フェードを行っています。

{hashtags}
'''
(D/f'{code}-description.txt').write_text(description)
kit=f'''# {code} 投稿セット

投稿用動画：{code}-{C['slug']}.mp4（1080×1920／30fps／{V['duration_seconds']:.2f}秒）
スマホ確認版：{code}-mobile.mp4
サムネイル：{code}-thumbnail.jpg

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
全文字幕は映像に焼き込み済み。別途{code}-subtitles.srtを添付。

## 公開後の確認

冒頭の視聴継続率と平均視聴率を分けて確認。数値の提示、驚き、設定やリスクの説明の各地点で離脱を確認する。現時点で視聴維持率改善を測定したものではありません。
'''
(D/f'{code}-posting-kit.md').write_text(kit)
record=f'''# {code} 制作記録

{C['title']}

完成尺：{V['duration_seconds']:.2f}秒、{V['frames']}フレーム。1080×1920、30fps。
字幕：全文{V['caption_pages']}ページ。VOICEVOXの演技区間と同期。数値の切り替えは発話区間の開始時刻を参照。
キャラクター：左が四国めたん、右がずんだもん。坂本アヒルの既存立ち絵と口差分を使用。声量で口パクを同期。
音声：喜び→一度の叫び→落胆。NISAを「ニーサ」、年利を「ねんり」、「名前、長っ」を「名前、ながっ」と読むよう調整。
音楽：{C['bgm']} / Kevin MacLeod、{C['bgm_bpm']} BPM。全編でBGMを継続し、驚きと小声では音量を下げる。

## デザインの修正

前作の構図を流用した初稿は不採用。その後の暗い／紙面主体の案も、従来の雰囲気が変わったとユーザーから指摘された。添付の承認済みサムネ2枚をスタイル参照に、明るいアニメ・大きな表情・太い文字を統一し、題材ごとの構図でサムネを作り直した。今回の変更はサムネのみで、動画本体は変更していない。
{design}
新規画像：背景2枚と採用サムネ1枚。imagegenの組み込みツールを使用。最終プロンプトは制作元の assets/image-prompts.json に保存。
図解と表情が重ならないよう、引きでは上、寄りでは左に図を置く。背景全面、下360pxは背景のみ。

## 数字の検証

```json
{json.dumps(calculate(C['theme']),ensure_ascii=False,indent=2)}
```

## 出力検証

投稿版・スマホ版を全編デコード。全文字幕とセリフの一致、映像の時刻、切替前後{V['boundary_frames_compared']}フレームを描画元と照合。下360pxに字幕や立ち絵がないことを全フレームで検査。完成動画から切り出した字幕ページを目視確認。
機械検査を人による実聴や視聴維持率改善の実証とは扱っていません。

```json
{json.dumps(V['files'],ensure_ascii=False,indent=2)}
```

## 制作元

GitHub: 0111comma/coursera-test / codex/fl004-fl005-20260914
台本、音声、発音時刻、描画プログラムを保存。画像生成プロンプトと素材は動画置き場の制作元にも保存。
'''
(D/f'{code}-production-record.md').write_text(record)
print(code,'posting kit, description, subtitles, script and record ready')
