#!/usr/bin/env python3
"""S034: 「老後は働けばいい」は成り立つか。年金をもらいながら働くと減る額の線。

2026-09-02 **主対象を60代から P-M(35歳・男性・会社員)へ立て直した5版。**
前の4版は「60代で年金をもらいながら働く人」に向けて書いていて、
docs/persona.md の「以後すべての企画は P-M から始める」を外していた
(ユーザー指摘「メインターゲットは35歳男性ね? なぜ35歳男性を入れない?」)。

35歳向けに変えたのは骨格の3点:

1. **入口を「老後は働けばいい」という35歳の逃げ道にした。**
   1文目で逃げ道を口にさせ、2文目「もらいながら働くと減る」で穴を開ける。
   60代の名指し(「60代。もらってる年金」)は捨てた
2. **60代向けの手順3カット(振込通知書 → 足す → 65万円以下?)を捨てた。**
   35歳の手元にその書類は無い。代わりに **判定(減っても半分 → 増える給料が多い →
   「働けばいい」は成り立つ)** と **行動(老後の備えを決めるとき、働く分を数えていい)**
   を置いた
3. **「65万円は毎年4月に見直される」を声に入れ、持ち帰るのを額ではなく形にした。**
   35歳が65歳になるころ、65万円は別の額になっている。言わずに終えると
   30年後に65万円だと信じたまま帰る(嘘になる)

前の版から残したもの: 年金は2つ(4人全員が詰まった穴)・仕組みの芯を例より先に・
最初から65万円で通す(51万円は「上がる前の額」として1回だけ)・
「引かれる前の給料」を例より先に・動詞は「減る」で統一・正直の幕(60万円の人)。

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
TITLE = "働くと減る年金"
BADGE = "※ 2026年8月時点。65万円は毎年4月に見直されます"
F.use_fp_theme(TITLE, speaker=108, badge=BADGE)      # 東北きりたん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

# 台本に出す値は verify.py と一致していること
assert V.LIMIT_OLD == 510_000 and V.LIMIT_NEW == 650_000
assert V.BASIC == 100_000 and V.SALARY == 450_000 and V.TOTAL == 550_000
assert V.STOP_NEW == 0
assert V.TOTAL_HIGH == 700_000 and V.OVER_HIGH == 50_000
assert V.suspended(V.BASIC, 600_000, V.LIMIT_NEW) == 25_000

SCENES = {
    # ---- カバー(キャラ 1/4)。逃げ道を口にした35歳。65万円は何の額か伏せる(K1)
    "toi": sf.person("01_base", height=0.46),
    "toi__cover": sf.cover("老後は働けばいい?", "年金が減りはじめる合計は", "65万円",
                           name="01_base", main_lab="月",
                           disclaimer="※ 2026年8月時点。額は毎年4月に見直されます。"),
    # 穴を開ける。**図だけが持つ情報**: 減るのは受け取っている年金であること
    "ana": sf.hero("減る", "年金をもらいながら働くと", name=None,
                   role="loss", count=False, size="reference"),

    # ---- 幕2: 年金は2つあって、減るのは会社で働いた分だけ
    "futatsu": sf.formula("基礎年金 + 厚生年金", name=None,
                          answer="あなたの年金", title="年金は2つある"),
    "kousei": sf.hero("基礎年金", "こっちは減らない", name=None,
                      role="gain", count=False, size="reference"),

    # ---- 幕3: 仕組みの芯。足す → 法律の額と比べる → 超えた分の半分
    # **図だけが持つ情報**: 足す「給料」が税や保険料を引く前の額であること
    "tasu": sf.formula("厚生年金 + 給料", name=None,
                       answer="税を引く前", title="まず足す2つ"),
    "kijun": sf.hero("65万円", "法律が決めた額", name=None, role="loss"),
    "ika": sf.hero("全額もらえる", "判定は毎月やり直す", name=None,
                   role="gain", count=False, size="reference"),
    "hanbun": sf.hero("半分", "超えた分の。あとで戻らない", name=None,
                      role="loss", count=False, size="reference"),

    # ---- 幕4: 変化。**51万円はここで1回だけ、上がる前の額として出す**
    "sa": sf.arrow("51万円", "65万円", "3月まで", "4月から",
                   title="法律が決めた額", role="gain"),

    # ---- 幕5: 例(キャラ 2/4)。65万円だけで解く
    "rei": sf.person_bubble("01_base", "厚生年金10万円"),
    "rei_q": sf.formula("10万円 + 45万円", name=None,
                        answer="55万円", title="この人で試す"),
    "zero": sf.hero("0円", "この人が減る額", name=None,
                    role="gain", count=False),

    # ---- 幕6: 正直に言う(キャラ 3/4)。全員が0円になるわけではない
    # 立ち絵は幕5と**同じ01_base**。声が「おなじ人」と言うため
    "rei2": sf.person_bubble("01_base", "給料60万円"),
    "koeru": sf.formula("70万円 − 65万円", name=None,
                        answer="5万円", title="超えている分"),
    "mada": sf.hero("月2万5000円", "5万円の半分", name=None, role="loss"),

    # ---- 幕7: 判定。減っても半分 → 増える給料のほうが多い → 成り立つ
    "tokushi": sf.compare("増える給料", "減る年金", "働いた分",
                          "超えた分の半分", title="どっちが多い?", role="neutral"),
    "seiritsu": sf.hero("成り立つ", "「老後は働けばいい」", name=None,
                        role="gain", count=False, size="reference"),

    # ---- 幕8: 形で持ち帰る(キャラ 4/4) → 行動
    # **図だけが持つ情報**: あなたの65歳では額が変わっていること
    "minaoshi": sf.arrow("65万円", "?万円", "2026年", "あなたの65歳",
                         title="毎年4月に見直し", role="neutral"),
    "katachi": sf.formula("超えた分 ÷ 2", name=None,
                          answer="減る額", title="覚えるのはこの形"),
    "cta": sf.cta("", "02_point", show_comment=True, bubble="働く分も数える"),
}

# 免責は、合計の話が画面に出るまで先頭の一文だけにする
for _k in ("toi", "ana", "futatsu", "kousei"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# ナレーション: 20ユニット。
# 幕の並びは「逃げ道 → 穴 → 年金は2つ → 仕組み → 額が上がった → 例 → 正直 → 判定 → 形 → 行動」。
# 工程E(段落ごと書き直す)で、20文すべて書き下ろしている。1行パッチはしていない。
UNITS = [
    # --- 幕1 逃げ道と穴。1文目で35歳の逃げ道を口にさせ、2文目で穴を開ける
    Unit("toi", "「老後は働けばいい」と思ってる?", anim=1.0, cover=True,
         se="pop", speed=1.03, intonation=1.3, pad=0.10, chara="none"),
    Unit("ana", "でも年金をもらいながら働くと、年金が減る。", anim=1.0, se="don",
         speed=1.13, intonation=1.15, pad=0.15, chara="none"),

    # --- 幕2 年金は2つ。減るほうを名指しし、自己判定の手がかりを渡す
    Unit("futatsu", "年金は2つ。基礎年金と厚生年金。", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("kousei", "減るのは、会社で働いた厚生年金だけ。", anim=1.0, speed=1.13,
         pad=0.10, chara="none"),

    # --- 幕3 仕組みの芯。足す2つの中身を、例より先に決めておく
    Unit("tasu", "まず1か月の厚生年金と、引かれる前の給料を足す。", anim=1.0,
         speed=1.13, intonation=1.1, pad=0.10, chara="none"),
    Unit("kijun", "その合計は、法律の【65万円】以下?", anim=1.0, se="don",
         speed=1.13, intonation=1.2, pad=0.10, chara="none"),
    Unit("ika", "65万円以下なら、厚生年金は減らない。", anim=1.0, speed=1.03,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("hanbun", "超えたら?厚生年金が減るのは、超えた分の【半分】。", anim=1.0,
         speed=1.03, intonation=1.2, pad=0.10, chara="none"),

    # --- 幕4 変化。**51万円が声に出るのはここだけ**。上がった向きだけを渡す
    Unit("sa", "この65万円、今年4月に【51万円】から上がった。", anim=1.2, se="don",
         speed=1.03, intonation=1.25, pad=0.10, chara="none"),

    # --- 幕5 例。合計を出し、65万円と比べ、減る額まで降ろす
    Unit("rei", "たとえば厚生年金が月【10万円】の人。", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("rei_q", "給料が月【45万円】なら、合計【55万円】。", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("zero", "65万円より少ない。だから減る額は【0円】。", anim=1.2, se="don",
         speed=1.03, intonation=1.3, pad=0.30, chara="none"),

    # --- 幕6 正直に言う。全員が0円になるわけではない。幕5と同じ3手をあてる
    Unit("rei2", "では、おなじ人の給料が【60万円】なら?", anim=1.0, speed=1.13,
         intonation=1.25, pad=0.10, chara="none"),
    Unit("koeru", "合計【70万円】。65万円を【5万円】超えた。", anim=1.0, speed=1.13,
         pad=0.10, chara="none"),
    Unit("mada", "その半分、厚生年金が【2万5000円】減る。", anim=1.0,
         speed=1.13, intonation=1.2, pad=0.20, chara="none"),

    # --- 幕7 判定。条件と根拠を先に置いてから「だから」で結論につなぐ
    Unit("tokushi", "減っても半分。働いて増える給料と、どっちが多い?", anim=1.0,
         speed=1.03, intonation=1.2, pad=0.10, chara="none"),
    Unit("seiritsu", "増える給料。だから「老後は働けばいい」は成り立つ。", anim=1.0,
         se="don", speed=1.03, intonation=1.2, pad=0.20, chara="none"),

    # --- 幕8 形で持ち帰る → 行動。35歳が65歳になるころ、額は別物になっている
    Unit("minaoshi", "ただし65万円は毎年4月に見直される。あなたの65歳では別の額。",
         anim=1.0, speed=1.13, intonation=1.1, pad=0.10, chara="none"),
    Unit("katachi", "覚えるのは額じゃない。超えた分の半分、という形。", anim=1.0,
         speed=1.03, intonation=1.15, pad=0.10, chara="none"),
    Unit("cta", "老後の備えを決めるとき、65歳から働く分を数えていい。", anim=1.0,
         speed=1.03, intonation=1.2, pad=0.10, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S034.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
