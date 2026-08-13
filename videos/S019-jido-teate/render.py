#!/usr/bin/env python3
"""S019: 児童手当は総額234万円(T4タイムライン型)。数値はverify.pyとassert照合。"""
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
BADGE = "第1子・3月生まれの例・2026年8月時点"

assert 15_000 * 36 == 540_000, "verify.pyと不一致"
assert 10_000 * 180 == 1_800_000, "verify.pyと不一致"
assert 540_000 + 1_800_000 == 2_340_000, "verify.pyと不一致"
assert 540_000 + 10_000 * 191 == 2_450_000, "verify.pyと不一致"
assert 30_000 * 216 == 6_480_000, "verify.pyと不一致"


def scene_timeline(fig, t):
    """固有シーン: 0歳→3歳→18歳年度末のタイムラインバー。"""
    from matplotlib.patches import Rectangle
    fig.text(0.5, 0.90, "もらえる流れ(子ども1人)", ha="center", color=INK_2, fontsize=32)
    a1 = sc.clamp01(t * 1.8)
    a2 = sc.clamp01(t * 1.8 - 0.5)
    x0, y0, h = 0.12, 0.52, 0.09
    w1 = 0.76 * (36 / 216)
    w2 = 0.76 * (180 / 216)
    fig.patches.append(Rectangle((x0, y0), w1 * a1, h, transform=fig.transFigure,
                                 facecolor=GOLD, edgecolor="none"))
    if a2 > 0:
        fig.patches.append(Rectangle((x0 + w1, y0), w2 * a2, h, transform=fig.transFigure,
                                     facecolor=MUTED_BAR, edgecolor="none"))
    fig.text(x0 + w1 / 2, y0 + h + 0.03, "月1.5万", ha="center", color=INK, fontsize=26, alpha=a1,
             path_effects=stroke_fx(INK, outline=outline_for(26), fatten=1.5))
    fig.text(x0 + w1 / 2, y0 - 0.04, "0〜3歳\n54万円", ha="center", va="top", color=INK_2,
             fontsize=22, alpha=a1)
    fig.text(x0 + w1 + w2 / 2, y0 + h + 0.03, "月1万", ha="center", color=INK, fontsize=26, alpha=a2)
    fig.text(x0 + w1 + w2 / 2, y0 - 0.04, "3歳〜18歳の年度末\n180万円", ha="center", va="top",
             color=INK_2, fontsize=22, alpha=a2)
    if a2 >= 1:
        fig.text(0.5, 0.325, "合計 234万円", ha="center", color=EMPH, fontsize=40,
                 path_effects=stroke_fx(EMPH, outline=outline_for(40), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(234, "{:,}万円", BADGE, BRAND, size=118),
    "hero_count__cover": sc.cover("児童手当ぜんぶで", "234万円", "子ども1人あたりの総額",
                                  "所得制限なし・こども家庭庁", BRAND),
    "hero_full": sc.hero("234万円", "児童手当の総額(子ども1人・18歳まで)", BADGE, BRAND,
                         size=112, sub_fs=28),
    "timeline": scene_timeline,
    "shotoku": sc.card("しかも今は", "所得制限なし", "(2024年10月から撤廃された)", BADGE, BRAND,
                       main_size=56),
    "tanjobi": sc.card("実は", "誕生月で総額が変わる", "(支給は「18歳のあと最初の3月末」まで)", BADGE, BRAND,
                       main_size=46),
    "tanjobi2": sc.card("その差", "4月生まれ245万円", "(3月生まれ234万円。差11万円)", BADGE, BRAND,
                        main_size=50),
    "daisan": sc.reveal("648万円", "第3子以降は月3万円だから", "30,000円 × 216ヶ月", BADGE, BRAND, size=112),
    "shinsei": sc.card("いちばん大事", "申請しないともらえない", "(出生・転入から15日以内が目安)", BADGE, BRAND,
                       main_size=44),
    "gacha": sc.card("ここだけの話", "誕生月ガチャ、ここにも", "(4月生まれ、ちょっとお得なのだ)", BADGE, BRAND,
                     main_size=46),
    "chips": sc.chips("あなたの家は?", ["もらってる", "これから", "申請を確認する", "独身なのだ"], BADGE, BRAND),
    "loop_back": sc.hero("234万円", "児童手当の総額(子ども1人・18歳まで)", BADGE, BRAND,
                         size=112, sub_fs=28),
}

UNITS = [
    Unit("hero_count", "【234万円】。", anim=1.2, cover=True, se="pop", face="normal",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "子ども1人でもらえる、児童手当の総額。", anim=0.8, speed=1.2),
    Unit("timeline", "3歳まで月1万5千円、そのあと月1万円。",
         narration="3歳まで月1万5千円、そのあとは毎月1万円。", anim=1.8, speed=1.15),
    Unit("shotoku", "今は、所得制限も【なし】なのだ。", anim=1.2, se="don", speed=1.15),
    Unit("tanjobi", "そして実は、誕生月で総額が変わるのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.2),
    Unit("tanjobi2", "4月生まれ245万、3月生まれ234万なのだ。", anim=1.2, speed=1.1,
         intonation=1.15),
    Unit("daisan", "さらに3人目は月3万。総額【648万円】。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("shinsei", "ただし、【申請】しないともらえないのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("gacha", "誕生月ガチャ、こんな所にもあるのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("chips", "あなたの家は、どのタイプ?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして1人分の総額が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S019.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
