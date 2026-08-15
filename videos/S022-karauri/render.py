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

from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrow

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "100万円分の例・手数料や金利は考慮せず"

MOTO = 1_000_000
assert MOTO - int(MOTO * 3.0) == -2_000_000, "verify.pyと不一致"
assert MOTO - int(MOTO * 0.8) == 200_000, "verify.pyと不一致"
assert int(MOTO * 0.0) - MOTO == -1_000_000, "verify.pyと不一致"


STEPS = [
    ("① 証券会社から株を借りる", "自分の株ではない"),
    ("② 借りた株を100万円で売る", "手元に100万円"),
    ("③ 80万円で買い戻して返す", "株は証券会社へ"),
]


def shikumi(step: int):
    """固有シーン: 空売りの3ステップを積み上げて見せる(本作の目玉図)。

    step=1〜3 で行が増え、step=4 で差額(もうけ)まで出す。
    毎ユニットで図が1行ずつ育つので、視聴者は同じ絵を見ながら理解を足していける。
    """
    def painter(fig, t):
        fig.text(0.5, 0.905, "空売りの3ステップ", ha="center", color=INK_2, fontsize=34)
        for i, (line, note) in enumerate(STEPS):
            if i + 1 > step:
                break
            # 最新の行だけアニメーションさせ、既出の行は出しきった状態にする
            a = sc.clamp01(t * 2.4) if i + 1 == step else 1.0
            y = 0.775 - i * 0.105
            fig.patches.append(FancyBboxPatch((0.09, y - 0.040), 0.82, 0.080,
                                              boxstyle="round,pad=0.008",
                                              transform=fig.transFigure,
                                              facecolor=GOLD if i + 1 == step else MUTED_BAR,
                                              edgecolor="none", alpha=a))
            fig.text(0.5, y + 0.006, line, ha="center", va="center", color=INK,
                     fontsize=29, alpha=a,
                     path_effects=stroke_fx(INK, outline=outline_for(29), fatten=1.5))
            fig.text(0.5, y - 0.028, note, ha="center", va="center", color=INK_2,
                     fontsize=20, alpha=a)
        if step >= 4:
            a = sc.clamp01(t * 2.4)
            fig.text(0.5, 0.495, "売った100万 − 買い戻し80万 = もうけ20万円",
                     ha="center", va="center", color=EMPH, fontsize=32, alpha=a,
                     path_effects=stroke_fx(EMPH, outline=outline_for(32), fatten=2))
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
    fig.text(0.5, 0.50, "株価に上限がないから、損にも上限がない", ha="center",
             color=INK_2, fontsize=23, alpha=a2)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "nazo": sc.hero("株が下がると", "もうかる人がいる", BADGE, BRAND, size=84, sub_fs=44),
    "nazo__cover": sc.cover("株が下がると、もうかるのはなぜ?", "空売り", "やることは、3つだけ",
                            "仕組みを図で解説", BRAND, main_size=124),
    "teigi": sc.card("その方法が【空売り】", "やることは3つだけ", "(持っていない株を、売る取引)", BADGE, BRAND,
                     main_size=52, head_fs=32),
    "step1": shikumi(1),
    "step2": shikumi(2),
    "step3": shikumi(3),
    "step4": shikumi(4),
    "rei": sc.reveal("もうけ 20万円", "100万円で売って、80万円で買い戻した場合", "その差額が、そのまま手元に残る",
                     BADGE, BRAND, size=96),
    "imi": sc.card("これが冒頭の答え", "下がると得をする取引", "(買いとは、もうかる向きが逆)", BADGE, BRAND,
                   main_size=50, head_fs=32,
                   ask="あなたの投信は、下がると損だけど?"),
    "toi": sc.card("では、逆に上がったら?", "買い戻す値段が上がる", "(返すために、買わないといけない)", BADGE, BRAND,
                   main_size=48, head_fs=32),
    "takaku": sc.card("株は返さないといけない", "だから高くても買い戻す", "(100万で売った株が、300万になっても)",
                      BADGE, BRAND, main_size=46, head_fs=32),
    "baisu": sc.reveal("損 200万円", "株価が3倍になった場合", "売った100万 − 買い戻し300万", BADGE, BRAND,
                       size=104),
    "hitaisho": scene_hitaisho,
    "mugen": sc.card("株価に上限はないので", "損にも上限がない", "(実際は追証や強制決済で止められる)", BADGE, BRAND,
                     main_size=54, head_fs=32),
    "kai": sc.card("ただし普通に買う場合は", "最悪でも100万円まで", "(株価が0になっても、出した分が上限)", BADGE, BRAND,
                   main_size=48, head_fs=32),
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
