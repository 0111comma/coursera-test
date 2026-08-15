#!/usr/bin/env python3
"""S014: 外国株の投信は「現地の値段 × 為替」で決まる。数値は verify.py と照合。

図の型(figure-forms.md):
- 主役は掛け算そのもの。→ 固有シーンで「ドルの箱 × 為替 = 円の箱」を
  横位置で並べ、円の箱の高さだけが変わることを見せる
- 円安・円高の比較は棒2本 + 差の帯(1.5万 → 1.7万 / 1.3万)
- 現地と円建てが別々に動くことは、同じ軸に2本の折れ線

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
BADGE = "100ドル分・為替ヘッジなしの例"

USD, R0, R_YASU, R_TAKA = 100.0, 150.0, 170.0, 130.0
assert USD * R0 == 15_000 and USD * R_YASU == 17_000 and USD * R_TAKA == 13_000


def kakezan(rate, yen_val, highlight=False):
    """固有シーン: 円の値段は「現地の値段 × 為替」の掛け算だと、位置で見せる。

    左=ドルの箱(いつも同じ高さ)、中=為替、右=円の箱(高さが変わる)。
    高さが意味を持つのは右の箱だけ。そこだけが動くことが、この動画の結論。
    """
    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "円での値段の決まり方", ha="center", color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.2)
        base_y = 0.545
        # 左: 現地の値段(高さは固定)
        fig.patches.append(Rectangle((0.09, base_y), 0.20, 0.115, transform=fig.transFigure,
                                     facecolor=MUTED_BAR, edgecolor="none", alpha=0.95))
        fig.text(0.19, base_y + 0.145, "100ドル", ha="center", va="center", color=INK,
                 fontsize=30, path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.8))
        fig.text(0.19, base_y - 0.030, "現地の値段", ha="center", va="center",
                 color=INK_2, fontsize=25)
        # 中: 為替
        fig.text(0.375, base_y + 0.058, "×", ha="center", va="center", color=INK_2, fontsize=44)
        fig.text(0.50, base_y + 0.100, f"{rate:.0f}円", ha="center", va="center",
                 color=EMPH if highlight else INK, fontsize=36, alpha=a,
                 path_effects=stroke_fx(EMPH if highlight else INK,
                                        outline=outline_for(36), fatten=2))
        fig.text(0.50, base_y - 0.030, "為替", ha="center", va="center",
                 color=INK_2, fontsize=25)
        fig.text(0.625, base_y + 0.058, "=", ha="center", va="center", color=INK_2, fontsize=44)
        # 右: 円での値段(高さが変わるのはここだけ)
        h = 0.115 * (yen_val / 15_000) * a
        fig.patches.append(Rectangle((0.72, base_y), 0.20, h, transform=fig.transFigure,
                                     facecolor=EMPH if highlight else GOLD,
                                     edgecolor="none", alpha=0.95))
        fig.text(0.82, base_y + h + 0.032, f"{yen_val:,.0f}円", ha="center", va="center",
                 color=INK, fontsize=30, alpha=a,
                 path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.8))
        fig.text(0.82, base_y - 0.030, "円での値段", ha="center", va="center",
                 color=INK_2, fontsize=25)
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("株は横ばい", "なのに投信は増えた", BADGE, BRAND, size=92, sub_fs=42),
    "nazo__cover": sc.cover("現地が動いてないのに、なぜ増える?", "為替",
                            "投信の値段は掛け算", "仕組みを図で解説", BRAND, main_size=140),
    "shikumi": kakezan(150, 15_000),
    "kaeru": kakezan(170, 17_000, highlight=True),
    "hikaku": sc.bars2("円での値段は、こう変わる",
                       ("1ドル150円のとき", 15_000, "1万5000円"),
                       ("1ドル170円のとき", 17_000, "1万7000円"),
                       BADGE, BRAND, gap="差 2000円", ymax=18_000),
    "gyaku": kakezan(130, 13_000, highlight=True),
    "ryoho": sc.lines2("2つを重ねてみる",
                       [("現地", [100, 100, 100], INK_2),
                        ("円での値段", [100, 113, 87], EMPH)],
                       BADGE, BRAND, ymin=82, ymax=118,
                       xlabels=["買った日", "円安", "円高"]),
    "toi": sc.quiz("こういう日は", "現地 −10%", "円安 +10%",
                   "", BADGE, BRAND),
    "sousai": sc.card("答えは", "円では変わらない", "(下がった分を、円安が打ち消す)",
                      BADGE, BRAND, main_size=52, head_fs=34,
                      ask="あなたはどっち?"),
    "hedge": sc.card("この動きの止め方", "為替ヘッジ", "(その代わり、費用がかかる)",
                     BADGE, BRAND, main_size=58, head_fs=34),
    "shime": sc.hero("投信の値段は", "かけ算で決まる", BADGE, BRAND, size=88, sub_fs=40),
}

# ネタ選定ゲート(F1): 予想「アメリカの株が動いてないなら、投信も動かないのでは?」
#   → 結論「円での値段は掛け算。為替だけでも動く」
UNITS = [
    Unit("nazo", "アメリカの株は横ばい。なのに投信は増えた。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("shikumi", "その投信の値段は、100ドル×150円なのだ。", anim=1.4, face="happy",
         speed=1.15, intonation=1.2),
    Unit("kaeru", "その為替が170円になると、どうなるのだ?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.2),
    Unit("hikaku", "その1万5000円が、【1万7000円】に。", anim=1.4, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("gyaku", "その差は2000円。130円なら1万3000円。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("ryoho", "その間、現地の値段は動いていない。", anim=1.6, speed=1.15),
    Unit("toi", "では現地が10%下がって、同じだけ円安なら?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("sousai", "答えは、円では変わらないのだ。", anim=1.4,
         puchun=True, speed=1.1, intonation=1.2),
    Unit("hedge", "この動きを止めるのが、【為替ヘッジ】。", anim=1.2, speed=1.15),
    Unit("shime", "外国株の投信は、株の値段かける為替なのだ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S014.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
