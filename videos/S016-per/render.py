#!/usr/bin/env python3
"""S016: PER15倍は「利益15年分の値段」。数値は verify.py と照合。

図の型(figure-forms.md):
- 「利益が何年分か」は積み上がっている量。→ 同じ大きさのブロックを積む(stack)。
  個数そのものが意味を持つので、数えられる大きさで並べる
- 15倍と30倍の比較は、ブロックの数の違いで見せる(棒に置き換えない)
- 「利益が増えるとPERは下がる」も stack の個数で見せる

図に出した数字は必ず字幕でも言う(S010でのユーザー指摘)。
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
BADGE = "株価1500円・1株利益100円の例"

PRICE, EPS = 1_500.0, 100.0
assert PRICE / EPS == 15.0 and 3_000.0 / EPS == 30.0, "verify.pyと不一致"


def scene_warizan(fig, t):
    """固有シーン: PERの割り算を、位置で見せる。

    左=株価の棒、右=1年分の利益の棒。左が右の何個分か、が PER。
    数字を並べるのではなく、「何個分か」を高さの比で見せる。
    """
    from matplotlib.patches import Rectangle
    fig.text(0.5, 0.905, "PERの正体は、わり算", ha="center", color=INK_2, fontsize=34)
    a = sc.clamp01(t * 2.2)
    base = 0.545
    # 左: 株価(高い棒)
    fig.patches.append(Rectangle((0.16, base), 0.22, 0.225 * a, transform=fig.transFigure,
                                 facecolor=GOLD, edgecolor="none", alpha=0.95))
    fig.text(0.27, base + 0.225 * a + 0.030, "株価1500円", ha="center", va="center",
             color=INK, fontsize=30, alpha=a,
             path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.8))
    # 右: 1年分の利益(15分の1の高さ)
    fig.patches.append(Rectangle((0.62, base), 0.22, 0.015 * a, transform=fig.transFigure,
                                 facecolor=EMPH, edgecolor="none", alpha=0.95))
    fig.text(0.73, base + 0.055, "利益100円", ha="center", va="center",
             color=EMPH, fontsize=28, alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(28), fatten=1.8))
    fig.text(0.50, base + 0.100, "÷", ha="center", va="center", color=INK_2, fontsize=48)
    fig.text(0.5, base - 0.032, "この高さの差が、何年分かを表す", ha="center", va="center",
             color=INK_2, fontsize=25)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "nazo": sc.hero("PER15倍", "何が15倍なのだ?", BADGE, BRAND, size=104, sub_fs=44),
    "nazo__cover": sc.cover("PER15倍って、何が15倍?", "PER", "答えは、利益15年分",
                            "1本で分かる解説", BRAND, main_size=150),
    "warizan": scene_warizan,
    "kotae": sc.stack("株価1500円の内訳", 15, "1個ぶんの利益は100円", "合計1500円",
                      BADGE, BRAND, cols=5),
    "imi": sc.card("言いかえると", "15年分の値段", "(15年で元が取れる計算)",
                   BADGE, BRAND, main_size=50, head_fs=34),
    "toi": sc.quiz("では、こちらは", "同じ利益100円で", "株価3000円", "", BADGE, BRAND),
    "sanju": sc.stack("株価3000円の内訳", 30, "1個ぶんの利益は100円", "合計3000円",
                      BADGE, BRAND, cols=6),
    "takai": sc.card("30年分も払う理由", "期待が大きいから",
                     "(利益が一定なら、の話)", BADGE, BRAND,
                     main_size=52, head_fs=34,
                     ask="あなたの持ち株は何年分?"),
    "fueru": sc.stack("利益が2倍になると", 8, "1個ぶんの利益は200円",
                      "株価は1500円のまま", BADGE, BRAND, cols=4, focus=7),
    "gyaku": sc.card("PERが低くても", "安いとは限らない",
                     "(利益が減れば、あとから上がる)", BADGE, BRAND,
                     main_size=52, head_fs=34),
    "shime": sc.hero("PERは", "何年分か、を表す", BADGE, BRAND, size=96, sub_fs=40),
}

# ネタ選定ゲート(F1): 予想「PERは"割安さの点数"みたいなもの?」
#   → 結論「利益の何年分の値段か。低いほど安いとは限らない」
UNITS = [
    Unit("nazo", "【PER15倍】。何が15倍なのだ?", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("warizan", "その正体は、株価1500円わる利益100円。", anim=1.4, face="happy",
         speed=1.15, intonation=1.2),
    Unit("kotae", "100円を15年ぶん集めると、1500円。", anim=1.6, speed=1.15),
    Unit("imi", "つまりPER15倍は、利益15年分の値段。", anim=1.4,
         se="don", speed=1.1, intonation=1.2),
    Unit("toi", "では同じ利益100円で、株価3000円なら?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("sanju", "答えは【30年分】。PERは30倍なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("takai", "30年分も払うのは、利益が増えると思うから。", anim=1.4, speed=1.15),
    Unit("fueru", "その利益が2倍の200円になれば、8年分。", anim=1.4, face="happy",
         speed=1.15),
    Unit("gyaku", "だからPERは、低いほど安いとは限らない。", anim=1.2, face="troubled",
         speed=1.15),
    Unit("shime", "PERは、利益の何年分かを表す数字。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S016.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
