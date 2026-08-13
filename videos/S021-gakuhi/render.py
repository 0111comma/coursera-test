#!/usr/bin/env python3
"""S021: 子どもの学費、最安コースでいくら?(T3比較型)。数値はverify.pyとassert照合。"""
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
BADGE = "文科省の調査ベース・自宅通学の学費のみ"

assert 282_000 + 535_800 * 4 == 2_425_200, "verify.pyと不一致"
assert 5_960_000 + 2_425_200 == 8_385_200, "verify.pyと不一致"
assert 19_760_000 + 4_110_000 == 23_870_000, "verify.pyと不一致"
assert round(23_870_000 / 8_385_200, 1) == 2.8, "verify.pyと不一致"


def scene_course(fig, t):
    """固有シーン: 3コースの棒比較(最安838万/中間1,007万/全私立2,387万)。"""
    from matplotlib.patches import Rectangle
    fig.text(0.5, 0.90, "コースでこう変わる", ha="center", color=INK_2, fontsize=34)
    rows = [("全公立+国立大", 838, GOLD), ("全公立+私大文系", 1_007, MUTED_BAR),
            ("ぜんぶ私立", 2_387, MUTED_BAR)]
    for i, (name, man, c) in enumerate(rows):
        a = sc.clamp01(t * 2.2 - i * 0.5)
        if a <= 0:
            continue
        y = 0.72 - i * 0.13
        w = 0.55 * (man / 2_387) * a
        fig.patches.append(Rectangle((0.28, y - 0.033), w, 0.066, transform=fig.transFigure,
                                     facecolor=c, edgecolor="none"))
        fig.text(0.27, y, name, ha="right", va="center", color=INK_2, fontsize=23)
        fig.text(0.28 + w + 0.015, y, f"{man:,}万", ha="left", va="center",
                 color=INK, fontsize=27, alpha=a,
                 path_effects=stroke_fx(INK, outline=outline_for(27), fatten=1.5) if i == 0 else None)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(838, "{:,}万円", BADGE, BRAND, size=118),
    "hero_count__cover": sc.cover("子ども1人の学費", "838万円", "いちばん安いコースでも",
                                  "幼稚園〜大学・文科省", BRAND),
    "hero_full": sc.hero("約838万円", "学費の最安コース(幼稚園〜大学)", BADGE, BRAND,
                         size=104, sub_fs=30),
    "uchiwake": sc.card("内訳", "高校まで596万+大学242万", "(ぜんぶ公立+国立大・自宅通学)", BADGE, BRAND,
                        main_size=42),
    "quiz": sc.quiz("クイズ", "では、ぜんぶ私立なら", "いくらだと思う?", "(幼稚園から大学まで)", BADGE, BRAND),
    "kotae": sc.reveal("約2,400万円", "最安コースの約2.8倍", "(私立中心+私大文系の場合)", BADGE, BRAND,
                       size=96),
    "course": scene_course,
    "heikin": sc.card("ただし", "学習費は塾・習い事込み", "(平均の数字。家庭差が大きい)", BADGE, BRAND,
                      main_size=46),
    "teate": sc.card("朗報", "児童手当で約28%", "(総額234万円 ÷ 最安838万円)", BADGE, BRAND,
                     main_size=52),
    "kansha": sc.card("ここだけの話", "親に感謝しかない", "(この金額、払ってもらってたのだ)", BADGE, BRAND,
                      main_size=50),
    "chips": sc.chips("あなたの家は?", ["ずっと公立", "私立まじり", "オール私立", "これから考える"], BADGE, BRAND),
    "loop_back": sc.hero("約838万円", "学費の最安コース(幼稚園〜大学)", BADGE, BRAND,
                         size=104, sub_fs=30),
}

UNITS = [
    Unit("hero_count", "【838万円】。", anim=1.2, cover=True, se="pop", face="surprised",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "子ども1人の学費、いちばん安いコース。", anim=0.8, speed=1.2),
    Unit("uchiwake", "高校まで全部公立で596万、国立大で242万。", anim=1.2, speed=1.1),
    Unit("quiz", "では、ぜんぶ私立ならいくら?", anim=1.4, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("kotae", "答えは約【2400万円】。差は約3倍なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("course", "コースべつの差が、これなのだ。", anim=1.8, speed=1.2),
    Unit("heikin", "数字は塾代込みの平均。家庭差は大きいのだ。", anim=1.2, speed=1.15),
    Unit("teate", "でも児童手当で、28%はまかなえるのだ。", anim=1.2, se="don", speed=1.1,
         intonation=1.15),
    Unit("kansha", "…この金額、親に感謝しかないのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("chips", "あなたの家は、どのコース?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして最安コースが、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S021.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
