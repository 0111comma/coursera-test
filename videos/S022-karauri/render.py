#!/usr/bin/env python3
"""S022: 空売りとは何か(仕組み解説型)。企画書は plan.md、数値は verify.py と照合。

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
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrow

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "100万円分の例・手数料や金利は考慮せず"

MOTO = 1_000_000
assert MOTO - int(MOTO * 3.0) == -2_000_000, "verify.pyと不一致"
assert MOTO - int(MOTO * 0.8) == 200_000, "verify.pyと不一致"
assert int(MOTO * 0.0) - MOTO == -1_000_000, "verify.pyと不一致"


# 経路図の定位置。横=時間(3拍)、上のレーン=株、下のレーン=お金の残高。
# 「手順の文を箱に並べる」のは図ではない(figure-forms.md の判定表NG欄)。
COLS = [0.245, 0.50, 0.755]     # 横位置 = 時間の3拍
Y_KABU = 0.755                  # 株レーン(トークンの中心)
Y_TIME = 0.672                  # 時間ラベル。バッジ(y0.805〜)より下に置く
Y_BASE = 0.492                  # お金レーンの底(残高0)
H_MAX = 0.105                   # 残高100万のときの棒の高さ
ASPECT = 1080 / 1920            # 図座標で「丸」に見せるための縦横比

# 株が今どこにあるか / 手元のお金(万円)
WHERE = ["あなた", "市場", "証券会社"]
KANE = [0, 100, 20]          # 下がった場合: 売って+100、80万で買い戻して+20
KANE_LOSS = [0, 100, -200]   # 上がった場合: 300万で買い戻すので手元は−200万


def _token(fig, x, y, label, color, alpha=1.0, rx=0.072):
    """株の所在を示すトークン。位置そのものが「今どこにあるか」を表す。"""
    from matplotlib.patches import Ellipse
    fig.patches.append(Ellipse((x, y), 2 * rx, 2 * rx * ASPECT, transform=fig.transFigure,
                               facecolor=color, edgecolor="none", alpha=alpha))
    fig.text(x, y, label, ha="center", va="center", color=SURFACE, fontsize=23, alpha=alpha,
             fontweight="black")


def keiro(step: int, loss: bool = False):
    """固有シーン: 空売りの経路図(figure-forms.md「物やお金が動く → 経路図」)。

    意味を担う視覚要素:
      - 横位置 = 時間(借りる → 売る → 買い戻して返す)
      - 上レーンのトークンの位置と矢印 = 株が誰の手にあるか、どちらへ動いたか
      - 下レーンの棒の高さ = そのときの手元のお金。折れ線で「増えて減る」軌跡を見せる
    文は置かない(冗長性)。語句は必ず対象の上か中に置く(空間的近接)。
    """
    kane = KANE_LOSS if loss else KANE
    hmax = H_MAX * 0.5 if loss else H_MAX   # 損失側は縦を圧縮(比率は保つ)
    labels_time = ["借りる", "売る", "買い戻して返す"]

    def painter(fig, t):
        a_now = sc.clamp01(t * 2.4)
        fig.text(0.5, 0.905, "上がると、同じ図がこうなる" if loss else "株とお金は、こう動く",
                 ha="center", color=INK_2, fontsize=34)
        fig.text(0.045, Y_KABU, "株", ha="center", va="center", color=INK_2, fontsize=25)
        fig.text(0.045, Y_BASE + 0.055, "お金", ha="center", va="center", color=INK_2, fontsize=25)

        shown = min(step, 3)
        # 株レーン: 矢印を先に描き、トークンをその上に重ねる
        for i in range(1, shown):
            alpha = a_now if i + 1 == step else 1.0
            fig.add_artist(FancyArrow(COLS[i - 1] + 0.078, Y_KABU,
                                      (COLS[i] - COLS[i - 1]) - 0.156, 0, width=0.005,
                                      head_width=0.024, head_length=0.020,
                                      transform=fig.transFigure, facecolor=INK_2,
                                      edgecolor="none", length_includes_head=True, alpha=alpha))
        for i in range(shown):
            alpha = a_now if i + 1 == step else 1.0
            _token(fig, COLS[i], Y_KABU, WHERE[i],
                   GOLD if i != 1 else MUTED_BAR, alpha)

        # 時間ラベル(その列が何の瞬間か)
        for i, lb in enumerate(labels_time):
            on = i + 1 <= step
            fig.text(COLS[i], Y_TIME, lb, ha="center", va="center",
                     color=EMPH if i + 1 == step else INK_2,
                     fontsize=23, alpha=(a_now if i + 1 == step else 1.0) if on else 0.28)

        # お金レーン: 底を1本の線で共有し、棒の高さで残高を示す
        fig.add_artist(plt.Line2D([0.13, 0.88], [Y_BASE, Y_BASE], transform=fig.transFigure,
                                  color=MUTED, linewidth=1.5, alpha=0.5))
        tops = []
        for i in range(shown):
            alpha = a_now if i + 1 == step else 1.0
            h = hmax * (kane[i] / 100) * (a_now if i + 1 == step else 1.0)
            if abs(h) > 0.001:
                y0 = Y_BASE if h > 0 else Y_BASE + h
                fig.patches.append(Rectangle((COLS[i] - 0.055, y0), 0.11, abs(h),
                                             transform=fig.transFigure,
                                             facecolor=EMPH if i == 2 else GOLD,
                                             edgecolor="none", alpha=alpha))
            tops.append((COLS[i], Y_BASE + h))
            lab = f"{kane[i]:+,}万".replace("+", "") if kane[i] else "0円"
            fig.text(COLS[i], Y_BASE + h + (0.030 if h >= 0 else -0.030), lab,
                     ha="center", va="center", color=EMPH if kane[i] < 0 else INK,
                     fontsize=25, alpha=alpha,
                     path_effects=stroke_fx(EMPH if kane[i] < 0 else INK,
                                            outline=outline_for(25), fatten=1.5))
        # 残高の軌跡(増えて、減る)を細い折れ線で結ぶ
        if len(tops) >= 2:
            fig.add_artist(plt.Line2D([p[0] for p in tops], [p[1] for p in tops],
                                      transform=fig.transFigure, color=INK_2,
                                      linewidth=2, alpha=0.55, zorder=5))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


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
    "teigi": sc.card("空売り", "持っていない株を、売る", "(証券会社から借りて売る取引)", BADGE, BRAND,
                     main_size=50, head_fs=40),
    "step1": keiro(1),
    "step2": keiro(2),
    "step3": keiro(3),
    "rei": sc.reveal("もうけ 20万円", "100万 − 80万", "(株を返しても、手元に残る)",
                     BADGE, BRAND, size=96),
    "imi": scene_gyaku,
    "toi": sc.card("上がったときは", "買い戻す値段も上がる", "(返すには、買うしかない)", BADGE, BRAND,
                   main_size=48, head_fs=34),
    "takaku": keiro(3, loss=True),
    "baisu": sc.reveal("損 200万円", "株価が3倍になった場合", "100万で売り、300万で買い戻す", BADGE, BRAND,
                       size=104),
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
    Unit("step2", "その借りた株を、今の値段で売るのだ。", anim=1.2, speed=1.15),
    Unit("step3", "その株が下がったら、買い戻して返すのだ。", anim=1.2, speed=1.15),
    Unit("rei", "その差額20万円が、まるごともうけになる。", anim=1.4, se="don", face="happy",
         speed=1.1, intonation=1.2),
    Unit("imi", "これが、下がると得をする仕組み。", anim=1.2, speed=1.15),
    Unit("toi", "では、上がってしまったら?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("takaku", "その株を返すために、高い値段で買うのだ。", anim=1.2, face="troubled",
         speed=1.15),
    Unit("baisu", "その値段が3倍なら、損は【200万円】なのだ。", anim=1.4, face="surprised",
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
    result = render_video(UNITS, SCENES, OUTDIR, "S022.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
