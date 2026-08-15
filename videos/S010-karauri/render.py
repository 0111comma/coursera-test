#!/usr/bin/env python3
"""S010: 空売りとは何か(仕組み解説型)。企画書は plan.md、数値は verify.py と照合。

ループ㊹(v2・全面改稿): v1はユーザー却下。原因は数字フックの誤用とペルソナ不在。
- 想定視聴者は P-A(NISAで積立中・個別株はやらない・空売りを説明できない)。docs/persona.md
- **この人は空売りを知らないので、金額のフックは効かない。** v1の「100万円の空売りで損200万円」は
  名詞を知らない人には他人事であり、何の動画かも伝わらなかった
- v2は「株が下がると、もうかる人がいる」という**名詞なしで分かる矛盾**で開き、名詞は2文目で与える
- 数字は仕組みを理解したあと(6ユニット目)に初めて出す
- 締めは「ニュースの空売りが分かる」。やり方は勧めない(戦略§6)
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "100万円分の例・値動きはイメージ"

MOTO = 1_000_000
assert MOTO - int(MOTO * 3.0) == -2_000_000, "verify.pyと不一致"
assert MOTO - int(MOTO * 0.8) == 200_000, "verify.pyと不一致"
assert int(MOTO * 0.0) - MOTO == -1_000_000, "verify.pyと不一致"


# 株価チャートの土台(ループ㊼)。ユーザー指摘:
#   「株価のこのタイミングで買って、どのタイミングで売って、どのタイミングで買い戻すとか
#     チャートでわかりやすくして欲しい」「借りて返している様子が全くない」
# → 横=時間、縦=株価。売買は線上の点。株を借りている期間はチャートの下に帯で出す。
# 値動きはブラウン橋(price_path)で、本物の株価と同じようにギザギザさせる。
DOWN = sc.price_path(100, 80, seed=11)     # 下がった場合: 100万 → 80万
UP = sc.price_path(100, 300, seed=5)       # 上がった場合: 100万 → 300万
KARI = (0.0, 1.0, "株を借りている")

SELL = (0.0, "借りて売る", "sell")
BUY = (1.0, "買い戻して返す", "buy")


def chart_down(title, marks, band=None, reveal=1.0):
    return sc.price_chart(DOWN, marks, band, title, BADGE, BRAND,
                          ymin=78, ymax=102, reveal=reveal, borrow=KARI)


def chart_up(title, marks, band=None, reveal=1.0):
    return sc.price_chart(UP, marks, band, title, BADGE, BRAND,
                          ymin=90, ymax=310, reveal=reveal, borrow=KARI)


def scene_hitaisho(fig, t):
    """固有シーン: 損の広がり方の非対称。買いは止まる、空売りは止まらない。

    棒は共通の底(損0)から上へ伸ばし、上に行くほど損が大きい。
    ラベルは棒の上にだけ置き、注記は1行だけ(3行を同じ高さに並べると潰れる)。
    """
    fig.text(0.5, 0.905, "損はどこまで広がるか", ha="center", color=INK_2, fontsize=34)
    a1 = sc.clamp01(t * 2.0)
    a2 = sc.clamp01(t * 2.0 - 0.7)
    base = 0.545

    # 左: 買い。株価が0になっても投資額の100万円で止まる
    h1 = 0.09 * a1
    fig.patches.append(Rectangle((0.14, base), 0.28, h1, transform=fig.transFigure,
                                 facecolor=MUTED_BAR, edgecolor="none"))
    fig.text(0.28, 0.675, "買い", ha="center", va="center", color=INK_2, fontsize=30, alpha=a1)
    fig.text(0.28, base + 0.045, "100万で止まる", ha="center", va="center", color=INK,
             fontsize=23, alpha=a1)

    # 右: 空売り。上に伸び続け、矢印で画面の外へ抜ける
    if a2 > 0:
        h2 = 0.175 * a2
        fig.patches.append(Rectangle((0.58, base), 0.28, h2, transform=fig.transFigure,
                                     facecolor=EMPH, edgecolor="none"))
        fig.add_artist(FancyArrow(0.72, base + h2, 0, 0.035 * a2, width=0.014,
                                  head_width=0.055, head_length=0.025,
                                  transform=fig.transFigure, facecolor=EMPH,
                                  edgecolor="none", length_includes_head=True))
        fig.text(0.72, 0.785, "空売り", ha="center", va="center", color=EMPH, fontsize=30,
                 alpha=a2, path_effects=stroke_fx(EMPH, outline=outline_for(30), fatten=2))
        fig.text(0.72, base + 0.08, "上限なし", ha="center", va="center", color=INK,
                 fontsize=25, alpha=a2,
                 path_effects=stroke_fx(INK, outline=outline_for(25), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_gyaku(fig, t):
    """固有シーン: 買いと空売りで、得をする「向き」が逆(figure-forms.md「二者が非対称」)。

    意味を担うのは矢印の向きだけ。語句は対象の左右に置き、文は置かない。
    """
    fig.text(0.5, 0.905, "得をする向きが、逆", ha="center", color=INK_2, fontsize=34)
    rows = [("買い", +1, MUTED_BAR, sc.clamp01(t * 2.4)),
            ("空売り", -1, EMPH, sc.clamp01(t * 2.4 - 0.7))]
    for i, (name, sign, color, a) in enumerate(rows):
        if a <= 0:
            continue
        y = 0.730 - i * 0.140
        fig.text(0.19, y, name, ha="center", va="center", color=INK, fontsize=30, alpha=a)
        fig.add_artist(FancyArrow(0.40, y - sign * 0.040, 0.18, sign * 0.080, width=0.010,
                                  head_width=0.038, head_length=0.030,
                                  transform=fig.transFigure, facecolor=color,
                                  edgecolor="none", length_includes_head=True, alpha=a))
        fig.text(0.83, y, "得", ha="center", va="center", color=color, fontsize=42, alpha=a,
                 path_effects=stroke_fx(color, outline=outline_for(42), fatten=2.5))
    fig.text(0.5, 0.505, "あなたの投信は、下がると損?", ha="center", va="center",
             color=EMPH, fontsize=28, alpha=sc.clamp01(t * 2.4 - 1.4))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "nazo": sc.hero("株が下がると", "もうかる人がいる", BADGE, BRAND, size=84, sub_fs=44),
    "nazo__cover": sc.cover("株が下がると、もうかるのはなぜ?", "空売り", "やることは、3つだけ",
                            "仕組みを図で解説", BRAND, main_size=124),
    "teigi": sc.card("空売り", "持っていない株を、売る", "(借りている間は貸株料がかかる)", BADGE, BRAND,
                     main_size=50, head_fs=40),
    "step1": chart_down("①株を借りる", [(0.0, "株を借りる", "sell")], reveal=0.14),
    "step2": chart_down("②借りた株を売る", [SELL], reveal=0.30),
    "step3": chart_down("③買い戻して返す", [SELL, BUY]),
    "rei": chart_down("売値と買値", [SELL, BUY]),
    "mouke": chart_down("差額が、もうけ", [SELL, BUY], (100, 80, "もうけ 20万")),
    "imi": scene_gyaku,
    "toi": sc.card("上がったときは", "買い戻す値段も上がる", "(返すには、買うしかない)", BADGE, BRAND,
                   main_size=48, head_fs=34),
    "takaku": chart_up("上がった場合", [SELL, BUY]),
    "baisu": chart_up("差額は、そのまま損", [SELL, BUY], (100, 300, "損 200万")),
    "hitaisho": scene_hitaisho,
    "mugen": sc.card("株価に上限はないので", "損にも上限がない", "(実際は追証や強制決済で止められる)", BADGE, BRAND,
                     main_size=54, head_fs=32),
    "kai": sc.card("比べてみると", "買いは、そこで止まる", "(株価が0でも、出した100万が上限)", BADGE, BRAND,
                   main_size=50, head_fs=34),
    "shime": sc.hero("株が下がると", "もうかる人がいる。それが空売り", BADGE, BRAND,
                     size=84, sub_fs=34),
}

# ネタ選定ゲート(F1): 予想「持ってない株を売る?意味がわからない」
#   → 結論「借りて売って買い戻すだけ。ただし損に上限がない」
# フックは「名詞なしで分かる矛盾」。数字は仕組みを理解したあとに出す(ループ㊹・persona.md)。
UNITS = [
    Unit("nazo", "株が下がると、もうかる人がいるのだ。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25, pitch=0.0),
    Unit("teigi", "その方法が【空売り】。やることは3つだけ。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("step1", "まず、証券会社から株を借りる。", anim=1.2, speed=1.15),
    Unit("step2", "その借りた株を、今の100万円で売るのだ。", anim=1.2, speed=1.15),
    Unit("step3", "株が80万円に下がったら、買い戻して返すのだ。", anim=1.2, speed=1.15),
    Unit("rei", "100万円で売って、80万円で買い戻す。", anim=1.2, speed=1.15),
    Unit("mouke", "差額の20万円が、まるごともうけなのだ。", anim=1.4, se="don", face="happy",
         speed=1.1, intonation=1.2),
    Unit("imi", "これが、下がると得をする仕組み。", anim=1.2, speed=1.15),
    Unit("toi", "では、上がってしまったら?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("takaku", "その株を返すには、300万円で買い戻すのだ。", anim=1.2, face="troubled",
         speed=1.15),
    Unit("baisu", "でも売ったのは100万円。損は【200万円】なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("kai", "ただし普通に買うなら、最悪でも100万まで。", anim=1.2, speed=1.15),
    Unit("hitaisho", "でも株価に上限はない。だから損にも上限がない。", anim=1.8, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("shime", "これで、ニュースの空売りが分かる。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S010.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
