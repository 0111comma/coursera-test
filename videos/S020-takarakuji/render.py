#!/usr/bin/env python3
"""S020: 宝くじ1万円分、平均いくら戻る?(T1クイズ型)。数値はverify.pyとassert照合。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "令和6年度の実績・平均の話"

assert int(10_000 * 0.465) == 4_650, "verify.pyと不一致"
assert 10_000 - 4_650 == 5_350, "verify.pyと不一致"
assert round(0.75 / 0.465, 1) == 1.6, "verify.pyと不一致"


def scene_kangen(fig, t):
    """固有シーン: 1万円が4,650円になる棒の縮み比較。"""
    from matplotlib.patches import Rectangle
    fig.text(0.5, 0.90, "1万円分買うと、平均で", ha="center", color=INK_2, fontsize=34)
    a1 = sc.clamp01(t * 1.8)
    a2 = sc.clamp01(t * 1.8 - 0.6)
    hmax = 0.30
    fig.patches.append(Rectangle((0.16, 0.40), 0.28, hmax * a1, transform=fig.transFigure,
                                 facecolor=MUTED_BAR, edgecolor="none"))
    fig.text(0.30, 0.40 + hmax + 0.03, "買った額\n10,000円", ha="center", color=INK_2,
             fontsize=26, alpha=a1)
    if a2 > 0:
        fig.patches.append(Rectangle((0.56, 0.40), 0.28, hmax * 0.465 * a2,
                                     transform=fig.transFigure, facecolor=GOLD, edgecolor="none"))
        fig.text(0.70, 0.40 + hmax * 0.465 + 0.03, "戻る額(平均)\n4,650円", ha="center",
                 color=INK, fontsize=26, alpha=a2,
                 path_effects=stroke_fx(INK, outline=outline_for(26), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(4_650, "{:,}円", BADGE, BRAND, size=118,
                                lead="その1万円、いくら戻る?"),
    "hero_count__cover": sc.cover("その1万円、いくら戻ると思う?", "戻りは4,650円", "では競馬は何%戻る?",
                                  "還元率46.5%・総務省", BRAND, main_size=96),
    "hero_full": sc.hero("4,650円", "宝くじ1万円分の平均の戻り", BADGE, BRAND, size=112, sub_fs=30),
    "kangen": scene_kangen,
    "pct": sc.card("1万円のうち戻る割合は", "46.5%", "(令和6年度の当せん金割合)", BADGE, BRAND,
                   main_size=64, head_fs=32,
                     ask="あなたは、買う派?買わない派?"),
    "quiz": sc.quiz("クイズ", "では競馬は", "何%戻る?", "(買った額のうち、戻ってくる割合)", BADGE, BRAND),
    "kotae": sc.reveal("約75%", "宝くじの約1.6倍戻る", "(券種により約70〜80%)", BADGE, BRAND, size=118),
    "horitsu": sc.card("実は法律で", "当せん金は5割以下", "(当せん金付証票法で上限が決まってる)", BADGE, BRAND,
                       main_size=48),
    "yume": sc.card("ここだけの話", "夢の値段は5,350円", "(10,000円 − 戻る4,650円)", BADGE, BRAND,
                    main_size=50),
    "sutansu": sc.card("だから", "買うなとは言わない", "(夢の値段を知って選ぶのだ)", BADGE, BRAND,
                       main_size=50),
    "chips": sc.chips("宝くじ、あなたは?", ["夢を買う派", "ジャンボだけ", "買わない派", "当てたことある"], BADGE, BRAND),
    "loop_back": sc.hero("4,650円", "宝くじ1万円分の平均の戻り", BADGE, BRAND, size=112, sub_fs=30),
}

UNITS = [
    Unit("hero_count", "【4650円】。", anim=1.2, cover=True, se="pop", face="normal",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "宝くじを1万円買ったときの、平均の戻り。", anim=0.8, speed=1.2),
    Unit("kangen", "半分以上は、戻らないのだ。", anim=1.6, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("pct", "戻ってくる割合にすると、46.5%なのだ。", anim=1.2, speed=1.15),
    Unit("quiz", "では競馬は、何%戻ると思う?", anim=1.4, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("kotae", "答えは約【75%】。宝くじの1.6倍なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("horitsu", "宝くじの戻りは、法律で5割以下なのだ。", anim=1.2, se="don", speed=1.15),
    Unit("yume", "つまり夢の値段は、【5350円】なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("sutansu", "買うなとは言わない。夢は自由なのだ。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("chips", "宝くじ、あなたはどっち?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして平均の戻りが、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S020.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
