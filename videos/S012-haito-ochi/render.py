#!/usr/bin/env python3
"""S012: 配当をもらった日に、株価が下がる。企画書は plan.md、数値は verify.py と照合。

図の型(figure-forms.md):
- 権利落ちは株価チャート。横=日付、縦=株価。権利落ち日の段差が主役なので、
  値動きの振れ幅は小さく取り、30円の段差が形として見えるスケールにする
- 「もらった額」と「下がった額」は棒2本。同じ長さになることが結論そのもの
- 税引き後の合計も棒2本+差の帯

図に出した金額は必ず字幕でも言う(S010でのユーザー指摘)。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (  # noqa: E402
    Unit, render_video, require_voicevox, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "株価3000円・配当30円の例"

PRICE, DIV, TAX = 3000, 30, 0.20315
EX = PRICE - DIV
NET = DIV * (1 - TAX)
assert EX == 2970 and round(NET, 1) == 23.9 and round(EX + NET, 1) == 2993.9, "verify.pyと不一致"

# 権利落ちの段差だけが意味を持つので、値動きは小さく(vol=0.10)、目盛りは狭く取る
BEFORE = sc.price_path(3000, 3000, n=70, vol=0.10, seed=7)
AFTER = [p - DIV for p in sc.price_path(3000, 3002, n=70, vol=0.10, seed=23)]
CHART = BEFORE + AFTER
# 売買の点は、値動きの途中ではなく「前日の終わり」と「翌日の始まり」に正確に置く。
# ずらすと、チャートに出る価格ラベルが台本の金額と食い違う
U_BEFORE = (len(BEFORE) - 1) / (len(CHART) - 1)
U_AFTER = len(BEFORE) / (len(CHART) - 1)


def scene_dokokara(fig, t):
    """固有シーン: 配当はどこから来るのかの経路図(「物やお金が動く → 経路図」)。

    会社の箱から株主へお金が移るだけで、全体が増えていないことを位置で見せる。
    """
    from matplotlib.patches import FancyArrow, Rectangle
    fig.text(0.5, 0.905, "配当は、どこから出ているか", ha="center", color=INK_2, fontsize=34)
    a1 = sc.clamp01(t * 2.4)
    a2 = sc.clamp01(t * 2.4 - 0.8)
    # 会社の箱。配当を出したぶんだけ、箱の中身が減る
    fig.patches.append(Rectangle((0.13, 0.560), 0.30, 0.215, transform=fig.transFigure,
                                 facecolor=MUTED_BAR, edgecolor="none", alpha=0.95))
    if a2 > 0:
        fig.patches.append(Rectangle((0.13, 0.560 + 0.215 - 0.055 * a2), 0.30, 0.055 * a2,
                                     transform=fig.transFigure, facecolor=SURFACE_HOLE,
                                     edgecolor="none"))
    fig.text(0.28, 0.520, "会社のお金", ha="center", va="center", color=INK_2, fontsize=28)
    fig.text(0.78, 0.520, "株主", ha="center", va="center", color=INK_2, fontsize=28)
    if a2 > 0:
        fig.add_artist(FancyArrow(0.46, 0.665, 0.20 * a2, 0, width=0.020, head_width=0.055,
                                  head_length=0.030, transform=fig.transFigure,
                                  facecolor=EMPH, edgecolor="none",
                                  length_includes_head=True, alpha=a2))
        fig.text(0.56, 0.725, "配当", ha="center", va="center", color=EMPH, fontsize=30,
                 alpha=a2, path_effects=stroke_fx(EMPH, outline=outline_for(30), fatten=2))
        fig.patches.append(Rectangle((0.70, 0.560), 0.16, 0.055 * a2, transform=fig.transFigure,
                                     facecolor=EMPH, edgecolor="none", alpha=0.95))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SURFACE_HOLE = "#1a1a19"   # 会社の箱から減った分を塗りつぶす色(背景と同色)

OCHI_MARKS = [(U_BEFORE, "もらう権利", "sell"), (U_AFTER, "翌日", "buy")]

SCENES = {
    "nazo": sc.hero("配当をもらった日に", "起きること", BADGE, BRAND, size=74, sub_fs=44),
    "nazo__cover": sc.cover("配当をもらうと、なぜ株価が下がる?", "配当落ち",
                            "もらった分だけ、下がる", "はじめての人向け", BRAND, main_size=116),
    "teigi": sc.card("配当とは", "株主に配るお金", "(年に1回か2回、配る会社が多い)",
                     BADGE, BRAND, main_size=56, head_fs=36),
    "kabu": sc.card("たとえば", "3000円の株", "(1つだけ持っているとする)",
                    BADGE, BRAND, main_size=62, head_fs=36),
    "chart": sc.price_chart(CHART, [(U_BEFORE, "もらう権利がつく日", "sell")], None,
                            "配当をもらう前日と、その翌日", BADGE, BRAND,
                            ymin=2955, ymax=3015, unit="円", reveal=0.52),
    "ochi": sc.price_chart(CHART, OCHI_MARKS, (3000, 2970, "30円 下がる"),
                           "配当をもらう前日と、その翌日", BADGE, BRAND,
                           ymin=2955, ymax=3015, unit="円"),
    "namae": sc.price_chart(CHART, OCHI_MARKS, (3000, 2970, "30円 下がる"),
                            "この日の呼び名は「権利落ち日」", BADGE, BRAND,
                            ymin=2955, ymax=3015, unit="円"),
    "onaji": sc.bars2("2つを並べてみると",
                      ("もらった配当", 30, "30円"),
                      ("下がった株価", 30, "30円"),
                      BADGE, BRAND),
    "dokokara": scene_dokokara,
    "toi": sc.quiz("足し算してみる", "2970円 + 30円", "= 3000円?", "", BADGE, BRAND),
    "zei": sc.card("ところが配当には", "税金がかかる", "(受け取るときに引かれる)",
                   BADGE, BRAND, main_size=54, head_fs=34,
                   ask="あなたの株は、どの口座?"),
    "wari": sc.bars2("配当から引かれる税金",
                     ("配当", 30, "30円"),
                     ("手取り", 23.9, "24円"),
                     BADGE, BRAND, gap="2割ひかれる"),
    "goukei": sc.bars2("受け取った直後の合計",
                       ("配当をもらう前", 3000, "3000円"),
                       ("もらった直後", 2993.9, "2993円"),
                       BADGE, BRAND, gap="少し減る", ymax=3100),
    "nisa": sc.card("NISAの口座なら", "税金はかからない", "(そのぶん、目減りしない)",
                    BADGE, BRAND, main_size=52, head_fs=34),
    "imi": sc.card("だから配当は", "増えたお金ではない", "(会社のお金が、あなたに移っただけ)",
                   BADGE, BRAND, main_size=50, head_fs=34),
    "shime": sc.hero("配当をもらった日に", "株価が下がる理由が、分かったのだ",
                     BADGE, BRAND, size=72, sub_fs=32),
}

# ネタ選定ゲート(F1): 予想「配当は、もらった分だけ得では?」
#   → 結論「配当は増えたお金ではなく移し替え。税金のぶん、直後は理論上わずかに減る」
# ループ51(端折り禁止): 1文につき新しい数字は1つまで。専門用語は使う前に言い換える。
UNITS = [
    Unit("nazo", "配当をもらった日に、株価が下がるのだ。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("teigi", "配当とは、会社が株主に配るお金。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("kabu", "たとえば、3000円の株があるとする。", anim=1.4, speed=1.15),
    Unit("chart", "その株の配当は、30円だとするのだ。", anim=1.4, speed=1.15),
    Unit("ochi", "すると次の日、株価は2970円になる。", anim=1.4, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("namae", "この下がる日を、【権利落ち日】という。", anim=1.2, speed=1.15),
    Unit("onaji", "つまり下がった分は、配当と同じ額。", anim=1.4, speed=1.15),
    Unit("dokokara", "その配当は、会社のお金が移っただけ。", anim=1.4, speed=1.15),
    Unit("toi", "では合計すると、もとどおりなのだ?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("zei", "ところが配当には、税金がかかるのだ。", anim=1.2, face="troubled",
         speed=1.15),
    Unit("wari", "その税金は、だいたい2割なのだ。", anim=1.4, speed=1.15),
    Unit("goukei", "だから手取りは、24円になるのだ。", anim=1.4, speed=1.15),
    Unit("nisa", "つまり合計は、2993円まで減る。", anim=1.4,
         puchun=True, speed=1.1, intonation=1.2, pitch=-0.05),
    Unit("imi", "でもNISAの口座なら、税金はかからない。", anim=1.2, face="happy",
         speed=1.15),
    Unit("shime", "配当は、増えたお金ではないのだ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S012.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
