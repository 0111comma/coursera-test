#!/usr/bin/env python3
"""S020: 宝くじ1万円分は、夢と寄付のセット販売(T1クイズ型)。数値はverify.pyとassert照合。

ループ㊷(ユーザー判定): ネタは合格・表現は不合格。書き直しの方針:
- 却下された理由は「結論が予想通り」。本作は残り5,350円の**行き先**を明かすことで
  「損」→「夢と寄付のセット販売」に反転させる(これが本当のペイオフ)
- 締めを4択チップにしない。立場を委ねて終わる(全12本が同じ締め方だった反省)
- 接続語の機械的な貼り付けをやめ、意味のある位置にだけ置く
"""
import sys
from pathlib import Path

from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "令和6年度の実績・平均の話"

KANGEN, SHUEKI, KEIHI = 0.465, 0.375, 0.160
assert int(10_000 * KANGEN) == 4_650, "verify.pyと不一致"
assert 10_000 - 4_650 == 5_350, "verify.pyと不一致"
assert int(10_000 * SHUEKI) == 3_750, "verify.pyと不一致"
assert round(KANGEN + SHUEKI + KEIHI, 3) == 1.0, "verify.pyと不一致"


def scene_kangen(fig, t):
    """固有シーン: 1万円が4,650円に縮む。買った瞬間に半分が消える絵。"""
    fig.text(0.5, 0.90, "1万円分買うと、平均で", ha="center", color=INK_2, fontsize=34)
    a1 = sc.clamp01(t * 1.8)
    a2 = sc.clamp01(t * 1.8 - 0.6)
    base, hmax = 0.52, 0.23
    fig.patches.append(Rectangle((0.16, base), 0.28, hmax * a1, transform=fig.transFigure,
                                 facecolor=MUTED_BAR, edgecolor="none"))
    fig.text(0.30, base + hmax + 0.03, "買った額\n10,000円", ha="center", color=INK_2,
             fontsize=26, alpha=a1)
    if a2 > 0:
        fig.patches.append(Rectangle((0.56, base), 0.28, hmax * 0.465 * a2,
                                     transform=fig.transFigure, facecolor=GOLD, edgecolor="none"))
        fig.text(0.70, base + hmax * 0.465 + 0.03, "戻る額(平均)\n4,650円", ha="center",
                 color=INK, fontsize=26, alpha=a2,
                 path_effects=stroke_fx(INK, outline=outline_for(26), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_uchiwake(fig, t):
    """固有シーン: 1万円の行き先を1本の帯で分解する(本作の目玉図)。

    「戻らない5,350円」の正体が、経費だけでなく自治体の収益金であることを見せる。
    単体スクショで意味が通るよう、金額・割合・時点・出典を図の中に入れる(B10)。
    """
    fig.text(0.5, 0.905, "1万円は、こう分かれる", ha="center", color=INK_2, fontsize=34)
    # 焦点は1つだけ(自治体の収益金)。当せん金・経費は後退色に置く
    segs = [("当せん金", KANGEN, 4_650, MUTED),
            ("自治体の収益金", SHUEKI, 3_750, EMPH),
            ("経費など", KEIHI, 1_600, MUTED_BAR)]
    x0, w_all, y, h = 0.10, 0.80, 0.66, 0.10
    x = x0
    for i, (name, ratio, yen, color) in enumerate(segs):
        a = sc.clamp01(t * 2.2 - i * 0.5)
        if a <= 0:
            continue
        w = w_all * ratio
        fig.patches.append(Rectangle((x, y), w * a, h, transform=fig.transFigure,
                                     facecolor=color, edgecolor="none"))
        # ラベルは帯の下に段違いで置く(狭い区画でも重ならないように)
        ly = y - 0.05 - (i % 2) * 0.058
        fig.text(x + w / 2, ly, f"{name}\n{yen:,}円", ha="center", va="top",
                 color=INK if i == 1 else INK_2, fontsize=22, alpha=a, linespacing=1.3)
        fig.text(x + w / 2, y + h / 2, f"{ratio:.1%}", ha="center", va="center",
                 color=INK, fontsize=24, alpha=a,
                 path_effects=stroke_fx(INK, outline=outline_for(24), fatten=1.5))
        x += w
    fig.text(0.5, 0.483, "宝くじ公式サイト「収益金の使い道」より", ha="center",
             color=INK_2, fontsize=22, alpha=sc.clamp01(t * 2.2 - 1.2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_anata(fig, t):
    """固有シーン: 締め。4択チップを使わず、判断を視聴者に渡して終える(E4/ループ㊷)。"""
    fig.text(0.5, 0.86, "1万円ぶんの", ha="center", color=INK_2, fontsize=34)
    draw_glow_text(fig, 0.5, 0.745, "夢と寄付の値段", 66)
    draw_glow_text(fig, 0.5, 0.615, "5,350円", 96)
    fig.text(0.5, 0.505, "高いと思う?  安いと思う?", ha="center", color=EMPH, fontsize=36,
             alpha=sc.clamp01(t * 2 - 0.6),
             path_effects=stroke_fx(EMPH, outline=outline_for(36), fatten=2))
    fig.text(0.66, 0.36, "コメントで\n教えてほしいのだ", ha="center", color=MUTED, fontsize=27,
             linespacing=1.4, alpha=sc.clamp01(t * 2 - 1.1))
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(4_650, "{:,}円", BADGE, BRAND, size=118,
                                lead="その1万円、いくら戻る?"),
    "hero_count__cover": sc.cover("その1万円、いくら戻ると思う?", "戻りは4,650円", "残りはどこへ行く?",
                                  "還元率46.5%・令和6年度", BRAND, main_size=96),
    "kangen": scene_kangen,
    "quiz": sc.quiz("クイズ", "じゃあ競馬は", "何%戻る?", "(買った額のうち、戻ってくる割合)", BADGE, BRAND),
    "kotae": sc.reveal("約75%", "宝くじより、競馬の方が戻る", "(券種により約70〜80%)", BADGE, BRAND, size=118),
    "horitsu": sc.card("低いのには理由がある", "法律で5割まで", "(当せん金付証票法。それ以上は出せない)", BADGE, BRAND,
                       main_size=56, head_fs=32),
    "doko": sc.card("では、残りの5,350円は", "どこへ行くのか", "(経費だけでは、ないのだ)", BADGE, BRAND,
                    main_size=54, head_fs=32,
                    ask="あなたの1万円も、そこへ?"),
    "uchiwake": scene_uchiwake,
    "tsukaimichi": sc.card("その3,750円の行き先", "道路・学校・子育て支援", "(発売元の都道府県と政令市の事業)", BADGE, BRAND,
                           main_size=44, head_fs=30),
    "reframe": sc.card("つまり宝くじとは", "夢と寄付のセット販売", "(買った時点で、約37%は寄付になる)", BADGE, BRAND,
                       main_size=48),
    "anata": scene_anata,
}

# 接続語は意味のある位置にだけ置く(ループ㊷)。締めは4択でなく判断の委譲。
UNITS = [
    Unit("hero_count", "1万円分の宝くじ。戻るのは平均【4650円】。", anim=1.2, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.2, pitch=0.0),
    Unit("kangen", "その半分以上が、買った瞬間に消えるのだ。", anim=1.6, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("quiz", "じゃあ競馬は、何%戻ると思う?", anim=1.4, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("kotae", "答えは【75%】。競馬の方が、戻るのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("horitsu", "その宝くじ、当せん金は法律で5割まで。", anim=1.2, speed=1.15),
    Unit("doko", "では残りの5350円は、どこへ行くのか。", anim=1.4, face="normal",
         speed=1.1, intonation=1.2, pause_scale=1.2),
    Unit("uchiwake", "その残りの約37%は、自治体の収入なのだ。", anim=1.8, speed=1.15),
    Unit("tsukaimichi", "そのお金で、道路や学校や子育て支援。", anim=1.2, se="don", speed=1.15),
    Unit("reframe", "つまり宝くじは、夢と寄付のセット販売。", anim=1.4, face="happy",
         speed=1.1, intonation=1.25),
    Unit("anata", "この5350円、高いと思うか安いと思うか。", anim=1.4, pad=0.2, face="smug",
         speed=1.1, intonation=1.2, pitch=-0.02),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S020.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
