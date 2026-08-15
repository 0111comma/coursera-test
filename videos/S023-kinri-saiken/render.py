#!/usr/bin/env python3
"""S023: 金利が上がると、なぜ持っている債券は値下がりするのか。数値はverify.pyとassert照合。

ループ㊸(投資シリーズ第2弾)。
- ネタ選定ゲート(F1): 予想「金利が上がれば債券も得になる」
  → 結論「持っている債券は逆に値下がりする」
- 割引現在価値の式は出さず、「毎年の利息を比べられる」という1点で腑に落とす
"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "額面100万円・年利1%・残り10年の例"

GAKUMEN, COUPON, NENSU = 1_000_000, 0.01, 10


def _kakaku(r):
    rishi = GAKUMEN * COUPON
    return sum(rishi / (1 + r) ** t for t in range(1, NENSU + 1)) + GAKUMEN / (1 + r) ** NENSU


assert round(_kakaku(0.03) / 10_000) == 83, "verify.pyと不一致"
assert round((GAKUMEN - _kakaku(0.03)) / 10_000) == 17, "verify.pyと不一致"
assert GAKUMEN * COUPON == 10_000 and GAKUMEN * 0.03 == 30_000, "verify.pyと不一致"


def hikaku(step: int):
    """固有シーン: 古い債券と新しい債券の「毎年の利息」を並べる(本作の目玉図)。

    step=1 で自分の債券だけ、step=2 で新しい債券を隣に出す。
    割引計算を出さずに「同じ100万円で、もらえる利息が違う」ことだけを見せる。
    """
    def painter(fig, t):
        fig.text(0.5, 0.905, "どちらも同じ100万円", ha="center", color=INK_2, fontsize=34)
        rows = [("あなたの債券", "毎年 1万円", MUTED_BAR),
                ("新しく出た債券", "毎年 3万円", EMPH)]
        for i, (name, val, color) in enumerate(rows):
            if i + 1 > step:
                break
            a = sc.clamp01(t * 2.4) if i + 1 == step else 1.0
            y = 0.735 - i * 0.135
            fig.patches.append(FancyBboxPatch((0.10, y - 0.052), 0.80, 0.104,
                                              boxstyle="round,pad=0.008",
                                              transform=fig.transFigure, facecolor=color,
                                              edgecolor="none", alpha=a))
            fig.text(0.20, y, name, ha="left", va="center", color=INK, fontsize=26, alpha=a)
            fig.text(0.80, y, val, ha="right", va="center", color=INK, fontsize=34, alpha=a,
                     path_effects=stroke_fx(INK, outline=outline_for(34), fatten=1.5))
        if step >= 2:
            a = sc.clamp01(t * 2.4 - 0.8)
            fig.text(0.5, 0.505, "同じ値段なら、毎年2万円お得な方を選ぶ", ha="center",
                     va="center", color=EMPH, fontsize=28, alpha=a,
                     path_effects=stroke_fx(EMPH, outline=outline_for(28), fatten=2))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


def scene_nedan(fig, t):
    """固有シーン: 値下がりの実額。100万円の棒が83万円まで縮み、差の17万円を示す。"""
    fig.text(0.5, 0.905, "だから、この値段でしか売れない", ha="center", color=INK_2, fontsize=32)
    a1 = sc.clamp01(t * 2.2)
    a2 = sc.clamp01(t * 2.2 - 0.7)
    base, hmax = 0.545, 0.185

    fig.patches.append(Rectangle((0.14, base), 0.28, hmax * a1, transform=fig.transFigure,
                                 facecolor=MUTED_BAR, edgecolor="none"))
    fig.text(0.28, base + hmax + 0.03, "額面\n100万円", ha="center", color=INK_2,
             fontsize=25, alpha=a1, linespacing=1.3)
    if a2 > 0:
        h2 = hmax * 0.829 * a2
        fig.patches.append(Rectangle((0.58, base), 0.28, h2, transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none"))
        fig.text(0.72, base + hmax * 0.829 + 0.03, "今の値段\n約83万円", ha="center",
                 color=INK, fontsize=25, alpha=a2, linespacing=1.3,
                 path_effects=stroke_fx(INK, outline=outline_for(25), fatten=1.5))
    fig.text(0.5, 0.50, "差 約17万円 の値下がり", ha="center", va="center",
             color=EMPH, fontsize=34, alpha=sc.clamp01(t * 2.2 - 1.3),
             path_effects=stroke_fx(EMPH, outline=outline_for(34), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero": sc.hero("約83万円", "金利が上がったあとの、100万円の債券", BADGE, BRAND,
                    size=112, sub_fs=27),
    "hero__cover": sc.cover("金利が上がったら、債券はどうなる?", "100万→83万", "持っている債券が値下がりする",
                            "額面100万円・年利1%・残り10年", BRAND, main_size=96),
    "genin": sc.card("値下がりの原因は1つ", "金利が1% → 3%", "(市場の金利が上がっただけ)", BADGE, BRAND,
                     main_size=56, head_fs=32),
    "yosou": sc.card("多くの人はこう思う", "金利が上がれば得", "(利息が増えるのだから、と)", BADGE, BRAND,
                     main_color=MUTED_BAR, main_size=54, head_fs=32),
    "gyaku": sc.card("でも実際は逆", "持っている債券は下がる", "(金利と債券の値段は、逆に動く)", BADGE, BRAND,
                     main_size=46, head_fs=32,
                     ask="あなたの投信にも、債券は入ってる?"),
    "riyu": sc.card("理由はこれだけ", "新しい債券と比べられる", "(買う人は、両方を見て選べる)", BADGE, BRAND,
                    main_size=46, head_fs=32),
    "hikaku1": hikaku(1),
    "hikaku2": hikaku(2),
    "erabu": sc.card("同じ100万円を出すなら", "毎年3万円の方を買う", "(古い方は、そのままでは売れない)", BADGE, BRAND,
                     main_size=48, head_fs=32),
    "nebiki": sc.card("だから古い債券は", "値下げしないと売れない", "(利息の差を、値段で埋める)", BADGE, BRAND,
                      main_size=46, head_fs=32),
    "nedan": scene_nedan,
    "manki": sc.card("ただし満期まで持てば", "100万円は戻る", "(値下がりするのは、途中で売る場合)", BADGE, BRAND,
                     main_size=56, head_fs=32),
    "shime": sc.hero("金利↑ → 債券↓", "金利と債券の値段は、いつも逆に動く", BADGE, BRAND,
                     size=84, sub_fs=27),
}

# ネタ選定ゲート(F1): 予想「金利が上がれば債券も得」→ 結論「持っている債券は値下がりする」
UNITS = [
    Unit("hero", "金利が上がって、100万円の債券が【83万円】。", anim=1.0, cover=True,
         se="pop", face="surprised", speed=1.05, intonation=1.2, pitch=0.0),
    Unit("genin", "その金利は、1%から3%になっただけ。", anim=1.2, speed=1.15),
    Unit("yosou", "多くの人は、金利が上がれば得だと思う。", anim=1.2, speed=1.15),
    Unit("gyaku", "でも持っている債券は、逆に値下がりする。", anim=1.4, face="troubled",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("riyu", "その債券が、新しい債券と比べられるのだ。", anim=1.2, speed=1.15),
    Unit("hikaku1", "あなたの債券は、毎年1万円の利息。", anim=1.2, speed=1.15),
    Unit("hikaku2", "でも新しい債券は、毎年3万円の利息。", anim=1.2, face="surprised",
         speed=1.1, intonation=1.15),
    Unit("erabu", "その3万円の方を、誰でも買いたくなる。", anim=1.2, speed=1.15),
    Unit("nebiki", "だから古い債券は、値下げしないと売れない。", anim=1.2, speed=1.15),
    Unit("nedan", "その値引きが、【17万円】なのだ。", anim=1.8, se="don",
         speed=1.1, intonation=1.2, pitch=-0.03),
    Unit("manki", "ただし満期まで持てば、100万円は戻るのだ。", anim=1.2, face="happy",
         speed=1.15, intonation=1.15),
    Unit("shime", "つまり金利と債券の値段は、逆に動くのだ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S023.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
