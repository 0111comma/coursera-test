#!/usr/bin/env python3
"""S034: 働くと年金が減る。その線が2026年4月に51万円→65万円へ動く。

主対象は60代前半で厚生年金をもらいながら働く人。副対象は P-M(35歳)で
「親の働き方の話」として見る。

設計のねじ(plan §9):
- **「働くと年金が減る」は否定しない。**否定するのは「だから働き方を抑えるしかない」
  という結論のほう。線そのものが動くので、抑える理由が消える人がいる
- **「全員が得します」にしない。**給与が高い人は改正後も止まる(19〜22)。
  ここを飛ばすと嘘になるので、カットもテンポも削らない
- 元トピック案の「申請しないと一生損する」は**事実誤認なので採用しない**。
  この見直しに申請は要らない(23)

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
_HYO = [["いまの線", "51万円"],
        ["2026年4月から", "65万円"]]

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

    # ---- 幕1: 是認(減るのは本当)
    "modoseru": sf.hero("戻せる", "抑えた時間", name=None,
                        role="gain", count=False, size="reference"),
    "honto": sf.hero("本当です", "働くと年金が減る", name=None,
                     role="loss", count=False, size="reference"),
    # 制度名はここで1回だけ名乗る(作文原則10。ぼかし語にしない)
    "namae": sf.hero("在職老齢年金", "働きながらもらう人の話", name=None,
                     role="neutral", count=False, size="reference"),
    "joken": sf.formula("年金の月額 + 給料", name=None,
                        answer="この合計で決まる", title="減るかどうか"),

    # ---- 幕2: 線と、止まる額の出し方(問い → 答えの2カットで割る)
    "sen_now": sf.hero("51万円", "いまの線(2025年度)", name=None, role="loss"),
    "toi_ikura": sf.formula("51万円を超えたら", name=None, answer="いくら止まる?",
                            title="止まる額"),
    "kotae": sf.hero("半分", "超えた分の", name=None,
                     role="loss", count=False, size="reference"),

    # ---- 幕3: 線が動く(表は出しっぱなし、枠だけ下へすべらせる)
    "hyo_now": sf.table(_HYO_HEAD, _HYO, highlight=0, title="線が動きます",
                        total_mode="dim"),
    "sa": sf.arrow("51万円", "65万円", "いまの線", "4月から",
                   title="あなたの線", role="gain"),
    "haba": sf.hero("14万円", "線が上がる幅", name=None, role="gain",
                    size="reference"),
    "nanika": sf.formula("51万円 → 65万円", name=None, answer="何が変わる?",
                         title="14万円ぶんの意味"),

    # ---- 幕4: 例(キャラ 2/4)
    # person_bubble に title を付けると、見出しが立ち絵の領域に入る(check_overlap)
    "rei": sf.person_bubble("01_base", "年金10万円"),
    "rei_q": sf.formula("年金10万円 + 給料45万円", name=None,
                        answer="合計は?", title="足してみます"),
    "rei_a": sf.hero("55万円", "この人の合計", name=None,
                     role="neutral", size="reference"),
    "koeru": sf.formula("55万円 − 51万円", name=None, answer="4万円",
                        title="いまの線との差"),
    "tomaru": sf.hero("月2万円", "4万円の半分", name=None, role="loss"),
    "yonngatsu": sf.hero("0円", "65万円まで動いた線の内側", name=None,
                         role="gain", count=False),
    "nen": sf.arrow("月2万円", "0円", "いまは", "4月から",
                    title="止まる額の差", role="gain"),

    # ---- 幕5: 正直に言う(ここを飛ばさない)
    "zenin": sf.hero("全員ではない", "あなたの合計しだい", name=None,
                     role="neutral", count=False, size="reference"),
    "hyo_koe": sf.table(_HYO_HEAD, _HYO, highlight=1, title="超えたら?"),
    "rei2": sf.person_bubble("03_troubled", "給料60万円"),
    "koeru2": sf.formula("年金10万円 + 給料60万円", name=None,
                         answer="合計70万円", title="4月からも止まる例"),
    "koeru3": sf.hero("月2万5000円", "70万円 − 65万円 の半分", name=None,
                      role="loss"),

    # ---- 幕6: 手続きと決定(キャラ 3/4・4/4)
    "tetsuzuki": sf.person_bubble("02_point", "手続きなし"),
    # answer に長い語を置くと「=」と重なる(check_overlap)。note 側に置く
    "tashizan": sf.formula("年金の月額 + 給料", "= 【65万円】と比べる", name=None,
                           title="自分の位置", emph_color=sf.GREEN_DARK),
    "cta": sf.cta("", "02_point", show_comment=True, bubble="足すだけ"),
}

# 「基準額は毎年4月に見直される」の免責は、線の話が画面に出るまで先頭の一文だけにする
for _k in ("toi", "modoseru", "honto", "namae", "joken"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

UNITS = [
    # 1文目は plan §4 の問いをそのまま口に出す(check_toi。損得の語「減る」を含む)
    Unit("toi", "年金が減るから、働く時間を抑えてる?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),
    Unit("modoseru", "抑えた時間、戻せるかも。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("honto", "実は、働くと年金は減ります。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("namae", "年金が減る仕組みを、在職老齢年金という。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("joken", "あなたの年金と給料の合計で決まる。", anim=1.0,
         speed=1.05, chara="none"),

    Unit("sen_now", "合計の線は、月【51万円】。", anim=1.0, se="don",
         speed=1.0, intonation=1.2, chara="none"),
    Unit("toi_ikura", "51万円を超えたら?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("kotae", "答えは、超えた分の半分。", anim=1.0, speed=1.05, chara="none"),
    Unit("hyo_now", "その51万円が、2026年4月に。", anim=1.0, speed=1.0,
         intonation=1.2, chara="none"),
    Unit("sa", "あなたの線は【65万円】へ。", anim=1.2, se="don",
         speed=1.0, intonation=1.25, chara="none"),
    Unit("haba", "差は14万円。", anim=1.0, speed=1.05, chara="none"),
        Unit("nanika", "14万円で、何が変わる?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.35, chara="none"),

    Unit("rei", "たとえば年金が月10万円の人。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("rei_q", "10万円と45万円の合計。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("rei_a", "すると、あなたは55万円。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("koeru", "55万円は線を4万円超え。", anim=1.0, speed=1.05, chara="none"),
    Unit("tomaru", "4万円の半分、月【2万円】。", anim=1.0, se="impact",
         se_at=0.1, speed=1.0, intonation=1.25, chara="none"),
    Unit("yonngatsu", "あなたの2万円は、止まりません。", anim=1.2, se="don",
         speed=1.0, intonation=1.3, chara="none"),
    Unit("nen", "年で24万円の差。", anim=1.2, speed=1.0,
         intonation=1.2, pad=0.35, chara="none"),

    Unit("zenin", "ただし、合計しだい。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hyo_koe", "合計が65万円を超えたら?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("rei2", "給料60万円なら、合計は?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("koeru2", "70万円です。", anim=1.0, speed=1.05, chara="none"),
    Unit("koeru3", "70万円なら、月2万5000円。", anim=1.0, speed=1.05,
         chara="none"),

    Unit("tetsuzuki", "この見直しに、手続きは要りません。", anim=1.0, speed=1.05,
         intonation=1.15, chara="none"),
    Unit("tashizan", "足すのは年金と給料。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("cta", "あなたが抑えた時間、戻せますか?", anim=1.0, speed=1.0,
         intonation=1.3, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S034.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
