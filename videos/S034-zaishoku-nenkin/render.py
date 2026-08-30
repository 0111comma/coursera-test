#!/usr/bin/env python3
"""S034: 働くと年金が減る。その線が2026年4月に51万円→65万円へ動く。

主対象は60代前半で厚生年金をもらいながら働く人。副対象は P-M(35歳)で
「親の働き方の話」として見る。

設計のねじ(plan §9):
- **「働くと年金が減る」は否定しない。**否定するのは「だから働き方を抑えるしかない」
  という結論のほう。線そのものが動くので、抑える理由が消える人がいる
- **「全員が得します」にしない。**給料が高い人は改正後も減る(18〜21)。
  しかも**その人を二人称で名指しして**言う。いま月9万5000円 → 4月からも
  月2万5000円。ここを飛ばすと嘘になるので、カットもテンポも削らない
- 元トピック案の「申請しないと一生損する」は**事実誤認なので採用しない**。
  この見直しに申請は要らない(尺の都合で概要欄に置いた。plan §6)

拍の順序:
- **例(7〜11)を線の動き(12〜17)より前に置く。**先に65万円を配ると、
  視聴者が自分で「55<65だから減らない」と結論を出してしまい、
  リビール(減る額が0円)が確認作業になる。先に痛み(月2万円が減っている)を見せる
- **動詞は最後まで「減る」。**「止まる(支給停止)」は制度側の言い方で、
  丸ごとゼロに聞こえるのに直後に「半分」が来るため、
  規則そのものが読めなくなっていた(2026-08-30 素人審査 #6)
- **「線」は5でその場で言い換える**(境目の線)。線は台本に6回出る
- 14万円(65万 − 51万)は**声に出さない**。2カット連続の主役になり、
  「差」の語が年24万円の差とぶつかっていたため

数の扱い:
- 「基本月額」「総報酬月額相当額」は使わない(耳で判別できず、自分の数字を
  当てはめられない)。「年金の月額」「給料」と言う
- 10万円・45万円・60万円は**この動画の中だけの仮定**。plan §10 の前提表に明記
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

# 常設ヘッダーは本編の問いを先出ししない(kotoba-rules K1)。主題の名乗りだけ。
TITLE = "働くと減る年金"
BADGE = "※ 2026年8月時点の制度です。基準額は毎年4月に見直されます"
F.use_fp_theme(TITLE, speaker=108, badge=BADGE)      # 東北きりたん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

# 台本に出す値は verify.py と一致していること
assert V.LIMIT_OLD == 510_000 and V.LIMIT_NEW == 650_000
assert V.RAISE == 140_000
assert V.BASIC == 100_000 and V.SALARY == 450_000 and V.TOTAL == 550_000
assert V.STOP_OLD == 20_000 and V.STOP_NEW == 0
assert V.DIFF_YEAR == 240_000
assert V.suspended(V.BASIC, 600_000, V.LIMIT_NEW) == 25_000

_HYO_HEAD = ["", "合わせて"]
# 4月からの値は**伏せる**(カバーと同じ「6?万円」)。ここで65万円を出すと、
# 14の矢印(51万円 → 65万円)が確認作業になり、13「誰も自分の線を知らない」の
# 画面が答えを先に配ってしまう
_HYO = [["いまの線", "51万円"],
        ["2026年4月から", "6?万円"]]

_COVER_HOOK = "その線が\n2026年4月に"

SCENES = {
    # ---- カバー(キャラ 1/4)
    # 赤=いまの線(既知として出す)/ 緑=4月からの線(伏せる)の非対称。
    # 何の51万円かはカバーで言わない(転回を先に殺さない。kotoba-rules K1)
    "toi": sf.person("03_troubled", height=0.46),
    "toi__cover": sf.cover("働くと年金が減る", _COVER_HOOK, "51万円",
                           name="03_troubled",
                           main_lab="いまの線",
                           alt_val="6?万円", alt_lab="4月から",
                           disclaimer="※ 2026年8月時点の制度です。"),

    # ---- 幕1: 是認。**「正しい」を声でも言う**(N5 語のロック)。
    # 画面は声で言わない側(何を抑えた判断なのか)を書く
    "honto": sf.hero("正しい", "働き方を抑えた判断は", name=None,
                     role="gain", count=False, size="reference"),
    # 制度名はここで1回だけ名乗る(作文原則10。ぼかし語にしない)
    "namae": sf.hero("在職老齢年金", "働きながらもらう人の話", name=None,
                     role="neutral", count=False, size="reference"),
    "joken": sf.formula("年金の月額 + 給料", name=None,
                        answer="この合計で決まる", title="減る額"),

    # ---- 幕2: 境目の線と、減る額の規則(動詞は最後まで「減る」で通す)
    "sen_now": sf.hero("51万円", "いまの線(2025年度)", name=None, role="loss"),
    "kotae": sf.hero("半分", "超えた分の", name=None,
                     role="loss", count=False, size="reference"),

    # ---- 幕3: 例(キャラ 2/4)。**線が動く前に、いま減っている額を見せる**
    # person_bubble に title を付けると、見出しが立ち絵の領域に入る(check_overlap)
    "rei": sf.person_bubble("01_base", "年金10万円"),
    "rei_q": sf.formula("年金10万円 + 給料45万円", name=None,
                        answer="合計は?", title="足してみます"),
    "rei_a": sf.hero("55万円", "足した合計", name=None,
                     role="neutral", size="reference"),
    "koeru": sf.formula("55万円 − 51万円", name=None, answer="4万円",
                        title="いまの線との差"),
    "tomaru": sf.hero("月2万円", "4万円の半分", name=None, role="loss"),

    # ---- 幕4: 転回。**まず「なぜ自分の線を知らないのか」を言う**(kotoba-rules C5)
    "hyo_now": sf.table(_HYO_HEAD, _HYO, highlight=0, title="いまの線と4月の線",
                        total_mode="dim"),
    # 13は声が「知らない」なので、画面は**知られていない事実のほう**を出す
    "minaoshi": sf.hero("毎年4月", "基準額の見直し", name=None,
                        role="neutral", count=False, size="reference"),
    "sa": sf.arrow("51万円", "65万円", "いまの線", "4月から",
                   title="あなたの線", role="gain"),
    "uchigawa": sf.hero("内側", "55万円 < 65万円", name=None,
                        role="gain", count=False, size="reference"),
    "yonngatsu": sf.hero("0円", "2026年4月からの線の内側", name=None,
                         role="gain", count=False),
    # 年額は**掛け算の工程ごと**画面に置く(月2万円 × 12か月 → 年24万円)。
    # 台本の最大の数字が、出どころ不明のまま出ないようにする
    "nen": sf.hero("年24万円", "月2万円 × 12か月", name=None, role="gain"),

    # ---- 幕5: 正直に言う(ここを飛ばさない。キャラ 3/4)
    "rei2": sf.person_bubble("03_troubled", "給料60万円"),
    "koeru2": sf.formula("年金10万円 + 給料60万円", name=None,
                         answer="合計70万円", title="4月からも減る例"),
    "ima": sf.formula("70万円 − 65万円", name=None, answer="5万円",
                      title="4月の線との差"),
    "nokori": sf.arrow("5万円", "2万5000円", "超えた分", "減る額",
                       title="超えた分の半分", role="loss"),

    # ---- 幕6: 決定(キャラ 4/4)
    # 声は動作(足して65万円と比べる)。**画面は声で言わない条件**(給料の中身)を出す
    "tashizan": sf.formula("年金の月額 + 給料", "給料 = 月給 + 賞与÷12", name=None,
                           title="自分の位置", emph_color=sf.GREEN_DARK),
    "cta": sf.cta("", "02_point", show_comment=True, bubble="足すだけ"),
}

# 「基準額は毎年4月に見直される」の免責は、線の話が画面に出るまで先頭の一文だけにする
for _k in ("toi", "honto", "namae", "joken"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# ナレーション: 23ユニット。
# 幕の並びは「規則 → 例で痛みを見せる → 線が動く → 得 → 正直 → 決定」。
#
# 2026-08-30 審査団(構成・日本語・コピー・素人)の第3ラウンドで書き直した。
# **1行パッチではなく、指摘のあった幕を丸ごと書き直している**(工程E)。
#
# 1. **動詞を「減る」に統一した。**前の版は1〜5が「減る」で6から「止まる」に
#    変わり、素人審査が「同じことなのか別のことなのか分からない。止まるなら
#    全部ゼロに聞こえるのに、直後に半分と言われる」で読めなくなっていた。
#    この動画の心臓は6で、以降の2万円・0円・2万5000円が全部そこにぶら下がる
# 2. **「線」の正体を5で渡す**(境目の線)。線は6回出るのに、日常語ではなかった
# 3. **12〜13で「なぜ自分の線を知らないのか」を言う**(基準額は毎年4月に
#    見直される)。事実だけが並んで機構が無い、というコピー審査の指摘(C5)
# 4. **18〜21を三人称の計算にしない。**給料60万円の人にも、いま9万5000円 →
#    4月から2万5000円 という落差が残る(verify.py の早見表 600,000円 行)。
#    順序は必ず「いま」→「4月からも減る」。正直な着地を最後に置く。
#    前の版はここで「全員が【0円】ではない」と抽象的に否定したあと、
#    その人に何も残さずに終わっていた(台本で唯一の下り坂だった)
UNITS = [
    # 1文目は plan §4 の問いをそのまま口に出す(check_toi。損得の語「減る」を含む)
    Unit("toi", "年金が減るから、働く時間を抑えてる?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),

    # --- 幕1 是認。**「正しい」を二人称で、声に出す**(画面だけに置かない)
    Unit("honto", "年金は本当に減る。あなたの判断は正しい。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("namae", "あなたの年金を減らすこれを、在職老齢年金という。", anim=1.0, speed=1.05,
         chara="none"),
    # 1で立てた「働く時間」を、ここで名指しで否定する。以降の数字が自分ごとになる
    Unit("joken", "減る額は?働く時間ではなく年金と給料。", anim=1.0,
         speed=1.0, intonation=1.15, chara="none"),

    # --- 幕2 境目の線と規則。**「線」の意味をその場で渡す**
    Unit("sen_now", "境目の線は年金と給料で月【51万円】。", anim=1.0, se="don",
         speed=1.0, intonation=1.2, chara="none"),
    Unit("kotae", "線を超えた分の半分だけ年金が減る。", anim=1.0, speed=1.05,
         chara="none"),

    # --- 幕3 例。合計を出し、いま減っている額まで一気に降ろす
    Unit("rei", "たとえば年金が月【10万円】。", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("rei_q", "給料45万円を足すと?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("rei_a", "答えは【55万円】。あなたも同じ?", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("koeru", "55万円は線を4万円超える。", anim=1.0, speed=1.05, chara="none"),
    Unit("tomaru", "その半分、月【2万円】が減る。", anim=1.0, se="impact",
         se_at=0.1, speed=1.0, intonation=1.25, chara="none"),

    # --- 幕4 転回。痛み(月2万円)を見せたあとで、線が動く理由から入る
    Unit("hyo_now", "この線は毎年4月に動く。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("minaoshi", "4月に動くから、あなたの去年の額はもう違う。", anim=1.0, speed=1.0,
         intonation=1.15, chara="none"),
    Unit("sa", "その線が4月から【65万円】。", anim=1.2, se="don",
         speed=1.0, intonation=1.25, chara="none"),
    # 10の「超える」の否定形で受ける(対句)。「内側」は画面だけに置く
    Unit("uchigawa", "あなたの55万円はもう超えない。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("yonngatsu", "減っていた2万円が、【0円】に。", anim=1.2, se="don",
         speed=1.0, intonation=1.3, chara="none"),
    # 月→年の掛け替えを「直すと」で宣言してから出す(kotoba-rules K4)。
    # 「年に直すと」は VOICEVOX が **トシニ** と読む(2026-08-30 に照会)。
    # 「年間に」なら ネンカンニ で、掛け替えの宣言も残る
    Unit("nen", "年間に直すと年金が【24万円】ふえる。", anim=1.2, speed=1.0,
         intonation=1.2, pad=0.35, chara="none"),

    # --- 幕5 正直に言う。**ここを飛ばすと「全員が得します」の嘘になる**
    Unit("rei2", "ただし、給料が60万円の人は?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("koeru2", "年金と足すと【70万円】。", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("ima", "70万円は4月の線を【5万円】超える。", anim=1.0,
         speed=1.05, intonation=1.15, chara="none"),
    Unit("nokori", "5万円の半分、2万5000円が減る。", anim=1.2,
         speed=1.05, intonation=1.15, chara="none"),

    # --- 幕6 決定。足す数2つと、比べる相手1つを**声で**渡し、
    # 比べた答え(下なら戻せる)まで言い切る(plan §7)
    Unit("tashizan", "年金と給料を足して65万円より下?", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("cta", "下なら、抑えた時間を戻せる?", anim=1.0, speed=1.0,
         intonation=1.3, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S034.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
