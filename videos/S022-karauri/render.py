#!/usr/bin/env python3
"""S022: 空売りとは何か(仕組み解説型)。数値はverify.pyとassert照合。

ループ㊸: 主戦場を投資の仕組み解説に変更(戦略§4)。本作はその第1弾。
- ネタ選定ゲート(F1): 予想「持ってない株を売る?意味がわからない」
  → 結論「借りて売って買い戻すだけ。ただし損に上限がない」
- 用語の定義で終わらせず、3ステップの図を積み上げて仕組みを見せる
- リスクの解説に限る。やり方の推奨・煽りはしない(戦略§6)
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
    "hero": sc.hero("損 200万円", "100万円分を空売りして、株価が3倍になった場合", BADGE, BRAND,
                    size=104, sub_fs=24),
    "hero__cover": sc.cover("持ってない株を、売れると思う?", "損 200万円", "出したのは100万円なのに",
                            "空売りの仕組みとリスク", BRAND, main_size=104),
    "teigi": sc.card("そもそも空売りとは", "持っていない株を売る", "(信用取引という仕組みを使う)", BADGE, BRAND,
                     main_size=52, head_fs=32),
    "step1": shikumi(1),
    "step2": shikumi(2),
    "step3": shikumi(3),
    "step4": shikumi(4),
    "imi": sc.card("だから空売りとは", "下がると得をする取引", "(買いとは、もうかる向きが逆)", BADGE, BRAND,
                   main_size=50, head_fs=32,
                   ask="あなたは、下がる方に賭けられる?"),
    "toi": sc.card("では、逆に上がったら?", "買い戻す値段が上がる", "(返すために、買わないといけない)", BADGE, BRAND,
                   main_size=48, head_fs=32),
    "baisu": sc.reveal("損 200万円", "株価が3倍になった場合", "売った100万 − 買い戻し300万", BADGE, BRAND,
                       size=104),
    "hitaisho": scene_hitaisho,
    "mugen": sc.card("株価に上限はないので", "損にも上限がない", "(実際は追証や強制決済で止められる)", BADGE, BRAND,
                     main_size=54, head_fs=32),
    "kai": sc.card("ただし普通に買う場合は", "最悪でも100万円まで", "(株価が0になっても、出した分が上限)", BADGE, BRAND,
                   main_size=48, head_fs=32),
    "shime": sc.hero("損 200万円", "この非対称が、空売りのいちばん怖いところ", BADGE, BRAND,
                     size=104, sub_fs=24),
}

# ネタ選定ゲート(F1): 予想「持ってない株を売る?意味がわからない」
#   → 結論「借りて売って買い戻すだけ。ただし損に上限がない」
UNITS = [
    Unit("hero", "100万円の空売りで、【損が200万円】。", anim=1.0, cover=True,
         se="pop", face="surprised", speed=1.05, intonation=1.2, pitch=0.0),
    Unit("teigi", "まず空売りとは、持っていない株を売ること。", anim=1.2, speed=1.15),
    Unit("step1", "その株は、証券会社から借りるのだ。", anim=1.2, speed=1.15),
    Unit("step2", "そして借りた株を、今の値段で売る。", anim=1.2, speed=1.15),
    Unit("step3", "その株が値下がりしたら、買い戻して返す。", anim=1.2, speed=1.15),
    Unit("step4", "その差額が、もうけになるのだ。", anim=1.2, se="don", face="happy",
         speed=1.15, intonation=1.15),
    Unit("imi", "だから下がると得をする、珍しい取引なのだ。", anim=1.2, speed=1.15),
    Unit("toi", "では、上がったらどうなるのか。", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("baisu", "その株が3倍になれば、損は【200万円】。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("hitaisho", "これは株価に、上限がないから起きるのだ。", anim=1.8,
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("mugen", "つまり空売りの損には、上限がないのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.2),
    Unit("kai", "ただし買いなら、最悪でも出した100万円まで。", anim=1.2, speed=1.15),
    Unit("shime", "この差が、空売りのいちばん怖いところ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S022.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
