#!/usr/bin/env python3
"""S034: 60代で年金をもらいながら働く人へ。減りはじめる額が今年4月に上がった。

2026-08-31 知識ゼロ3人テスト(理解度 4.4/6.0)を受けた**3度目の全面書き直し**。
前の版は「誰の話か」を1カット目に置いたが、**仕組みの芯を渡していなかった**:

- Q6(何が減るのか・なぜ減るのか)が **0/3**。3人とも「そういうルールとして
  丸呑みした」と書いた。前の版の1文目は「厚生年金が減るから」と**減ることを
  既知として飛ばし**、51万円が誰の決めた額かも、なぜ半分かも一度も言わなかった
  → **幕1〜幕2を「足す → 国の決めた額と比べる → 超えた分の半分だけ減る」の
    5カットに作り直した。**動画の中でいちばん長い区間をここに割いている
- Q4(自分でできるか)は3人とも「最初の一歩で止まる」。自分の厚生年金の額の
  在りかも、給料にボーナスを足すことも、概要欄に落としていて声に無かった
  → **締めを「ねんきん定期便 → 給料を足す → ボーナスは12で割る → 65万円以下?」
    の5カット**にした。判定だけ渡して終わらせない
- Q1 は2/3。「60代」と閉じて58歳をはじき、対象条件が「抑えてる?」という
  疑問形に埋もれていた
  → **1文目を「60代。もらってる年金、働くと減る?」**にした。
    「もらってる」で受給者の話だと確定させ、行動(抑える)を条件から外す
- Q2 は3人とも「いつの話か」でつまずいた。「2026年4月」と過去形で言ったあとに
  「4月からは」と未来の言い方をしていた
  → **「実は今年4月、法律が変わった」「もう月65万円」**と、現在形で言い切る

**捨てたもの**(60秒に全部は入らない。**足すのではなく捨てて厚くした**):
- 「基礎年金は減らない」の1カット。3人全員がここで置いていかれた
  (「基礎年金って何ですか?」)。判定式に基礎年金は出てこないので、
  視聴後の決定を1ミリも変えない。**画面(幕1の図)だけに残し、声から外した**
- 9万5000円 → 2万5000円 の落差と、7万円。3人とも「9万5000円がどこから
  出たか分からないまま書き取った」と書いた。**規則を再適用して見せる尺が
  無い数字は、出さないほうがよい**。給料60万円の人には「4月からも
  月2万5000円減る」と「減るのは超えた分の半分だけ」を渡す
- 「あなたは?」「あなたも?」の呼びかけ2つ。手順を渡す前に自己適用を
  求めていたので、3人とも答えられなかった。**二人称は締めに一本化**
- 制度名「在職老齢年金」・年24万円。概要欄と固定コメントに置いた

数の扱い:
- 「基本月額」「総報酬月額相当額」は使わない。「厚生年金」「給料」と言う
- 10万円・45万円・60万円は**この動画の中だけの仮定**。plan §10 の前提表に明記
- 声に出す数はすべて verify.py の出力か plan.md の前提表の中にある
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

# 常設ヘッダーは本編の問いを先出ししない(kotoba-rules K1)。主題の名乗りだけ。
# バッジの「基準額」はナレーションに一度も出てこない役所言葉だったので、
# 本編と同じ呼び名(年金が減りはじめる額)に揃えた。
TITLE = "働くと減る年金"
BADGE = "※ 2026年8月時点。減りはじめる額は毎年4月に変わります"
F.use_fp_theme(TITLE, speaker=108, badge=BADGE)      # 東北きりたん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

# 台本に出す値は verify.py と一致していること
assert V.LIMIT_OLD == 510_000 and V.LIMIT_NEW == 650_000
assert V.BASIC == 100_000 and V.SALARY == 450_000 and V.TOTAL == 550_000
assert V.STOP_OLD == 20_000 and V.STOP_NEW == 0
assert V.OVER_OLD == 40_000 and V.TOTAL_HIGH == 700_000
assert V.suspended(V.BASIC, 600_000, V.LIMIT_NEW) == 25_000

# 境目の呼び名は**1つに固定する**(旧版は「線」「減りはじめる合計」「この額」
# 「基準額」の4通りが混在し、指す先が分からないという指摘を受けた)。
_COVER_HOOK = "年金が減りはじめる額が"

SCENES = {
    # ---- カバー(キャラ 1/4)
    # 1フレーム目で**誰の話か**を名乗る。
    # 赤=いまの額(既知)/ 緑=4月からの額(伏せる)の非対称は残す
    "toi": sf.person("03_troubled", height=0.46),
    "toi__cover": sf.cover("60代。働くと年金が減る?", _COVER_HOOK, "51万円",
                           name="03_troubled",
                           main_lab="いままで",
                           alt_val="6?万円", alt_lab="いまは",
                           disclaimer="※ 2026年8月時点の制度です。"),

    # ---- 幕1: 年金は2つあって、減るのは片方だけ
    # **図だけが持つ情報**: 減らないほうの名前(声では言わない)
    "uchi": sf.hero("基礎年金", "減らないほう", name=None,
                    role="gain", count=False, size="reference"),

    # ---- 幕2: 仕組みの芯。足す → 国の決めた額と比べる → 超えた分の半分
    "tasu": sf.formula("厚生年金 + 給料", name=None,
                       answer="この合計", title="まず足す2つ"),
    "kijun": sf.hero("51万円", "国が決めた額", name=None, role="loss"),
    # **図だけが持つ情報**: 判定は毎月やり直すこと(声では言えなかった)
    "koeta": sf.formula("合計 − 51万円", name=None,
                        answer="超えた分", title="超えた月だけ"),
    "hanbun": sf.hero("半分", "超えた分の", name=None,
                      role="loss", count=False, size="reference"),

    # ---- 幕3: 例(キャラ 2/4)。**合計が動く前に、いま減っている額を見せる**
    "rei": sf.person_bubble("01_base", "厚生年金10万円"),
    "rei_q": sf.formula("10万円 + 45万円", name=None,
                        answer="合計は?", title="足してみる"),
    "rei_a": sf.hero("55万円", "足した合計", name=None,
                     role="neutral", size="reference"),
    "koeru": sf.formula("55万円 − 51万円", name=None, answer="4万円",
                        title="超えている分"),
    "tomaru": sf.hero("月2万円", "4万円の半分", name=None, role="loss"),

    # ---- 幕4: 転回。**いつの話かを画面でも声でも確定させる**
    "kaisei": sf.hero("今年4月", "法律が変わった", name=None,
                      role="neutral", count=False, size="reference"),
    "sa": sf.arrow("51万円", "65万円", "いままで", "いまは",
                   title="年金が減りはじめる額", role="gain"),
    "zero": sf.hero("0円", "この人の減る額", name=None,
                    role="gain", count=False),

    # ---- 幕5: 正直に言う(キャラ 3/4)。全員が0円になるわけではない
    "rei2": sf.person_bubble("03_troubled", "給料60万円"),
    "koeru2": sf.formula("10万円 + 60万円", name=None,
                         answer="70万円", title="もう一人の合計"),
    "koeru3": sf.formula("70万円 − 65万円", name=None,
                         answer="超えた分", title="4月からの超過"),
    "mada": sf.hero("月2万5000円", "その半分", name=None, role="loss"),

    # ---- 幕6: 自分でやる(キャラ 4/4)。判定だけでなく**入手先と足し方**を渡す
    "anata": sf.person_bubble("01_base", "いくらだっけ?"),
    "teikibin": sf.hero("ねんきん定期便", "厚生年金の額はここ", name=None,
                        role="neutral", count=False, size="reference"),
    # 図だけが持つ情報: 足すのは**2つだけ**(基礎年金は入れない)
    "bonus": sf.formula("厚生年金 + 給料", name=None,
                        answer="あなたの合計", title="足すのは2つだけ"),
    # 比較そのものを絵にする(formula の2段組は着地後に動きが止まり、
    # 答えを長くすると「=」と重なる。design M1 / check_overlap)
    "tashizan": sf.compare("厚生年金+給料", "65万円", "あなたの合計",
                           "この額以下?", title="あなたの位置", role="neutral"),
    "cta": sf.cta("", "02_point", show_comment=True, bubble="足すだけ"),
}

# 免責は、合計の話が画面に出るまで先頭の一文だけにする
for _k in ("toi", "uchi", "tasu", "kijun"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# ナレーション: 23ユニット。
# 幕の並びは「誰の話か → 仕組み → 例で痛みを見せる → 額が上がる → 正直 → 自分でやる」。
#
# 工程E(段落ごと書き直す)で、幕1〜幕6をすべて入れ替えている。1行パッチはしていない。
# 前の版から残したのは「動詞は最後まで減るで通す」「例(幕3)を転回(幕4)より
# 前に置く」の2つの方針だけで、23文すべて書き直した。
UNITS = [
    # 1文目で**年齢・受給者であること・行動の理由**を名乗る。
    # 「もらってる」の5文字が、いま振り込まれている年金の話だと確定させる
    Unit("toi", "60代。もらってる年金、働くと減る?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),

    # --- 幕1 年金は1つではない。減る相手を厚生年金に限定する
    Unit("uchi", "年金のうち減るのは厚生年金だけ。", anim=1.0, speed=1.05,
         chara="none"),

    # --- 幕2 仕組みの芯。ここが3人とも0点だった区間
    Unit("tasu", "まず厚生年金と給料を合計する。", anim=1.0,
         speed=1.0, intonation=1.15, chara="none"),
    Unit("kijun", "合計が国の決めた月【51万円】を超える?", anim=1.0, se="don",
         speed=1.0, intonation=1.2, chara="none"),
    Unit("koeta", "すると超えた月だけ厚生年金が減る。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hanbun", "厚生年金は超えた分の【半分】だけ減る。", anim=1.0,
         speed=1.0, intonation=1.2, chara="none"),

    # --- 幕3 例。合計を出し、いま減っている額まで一気に降ろす
    Unit("rei", "たとえば厚生年金が月【10万円】。", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("rei_q", "もし給料が月【45万円】なら?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("rei_a", "給料と足して合計【55万円】。", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("koeru", "合計は51万円を【4万円】超え。", anim=1.0, speed=1.05,
         intonation=1.1, chara="none"),
    Unit("tomaru", "その半分は?月【2万円】減っていた。", anim=1.0, se="impact",
         se_at=0.1, speed=1.0, intonation=1.25, chara="none"),

    # --- 幕4 転回。**現在形で言い切る**(「もう」で施行済みを渡す)
    Unit("kaisei", "実は今年4月、法律が変わった。", anim=1.0, speed=1.0,
         intonation=1.15, chara="none"),
    Unit("sa", "法律で51万円が、もう月【65万円】。", anim=1.2, se="don",
         speed=1.0, intonation=1.25, chara="none"),
    Unit("zero", "この人は超えない。減る額【0円】。", anim=1.2, se="don",
         speed=1.0, intonation=1.3, pad=0.35, chara="none"),

    # --- 幕5 正直に言う。全員が0円になるわけではない
    Unit("rei2", "もし給料が月【60万円】なら?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("koeru2", "給料と足して合計【70万円】。", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("koeru3", "合計は65万円超え。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("mada", "すると超えた分の半分、月【2万5000円】減る。", anim=1.0,
         speed=1.05, intonation=1.2, pad=0.3, chara="none"),

    # --- 幕6 自分でやる。**足す数の在りかと足し方**を声で渡す
    Unit("anata", "では、あなたの厚生年金は?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("teikibin", "厚生年金はねんきん定期便に。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("bonus", "そこにボーナスを12で割った給料を足す。", anim=1.0,
         speed=1.05, chara="none"),
    Unit("tashizan", "合計が月【65万円】以下なら減らない。", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("cta", "年金のために働く時間を抑えなくていい。", anim=1.0, speed=1.0,
         intonation=1.2, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S034.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
