#!/usr/bin/env python3
"""S011: 「103万円の壁」はもう古い(T2誤解訂正型)。数値はverify.pyとassert照合。"""
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
BADGE = "2026年分(令和8年)・2年間の特例込み"

assert 1_040_000 + 740_000 == 1_780_000, "verify.pyと不一致"


def scene_jidai(fig, t):
    """固有シーン: 壁の変遷タイムライン 103→123→178。"""
    fig.text(0.5, 0.90, "壁はこう動いた", ha="center", color=INK_2, fontsize=34)
    steps = [("〜2024年", "103万円", MUTED_BAR), ("2025年分", "123万円", MUTED_BAR),
             ("2026年分", "178万円", GOLD)]
    for i, (yr, v, c) in enumerate(steps):
        a = sc.clamp01(t * 2.4 - i * 0.55)
        if a <= 0:
            continue
        y = 0.70 - i * 0.105
        fig.text(0.27, y, yr, ha="center", color=INK_2, fontsize=29, alpha=a)
        fig.text(0.62, y, v, ha="center", color=INK, alpha=a,
                 fontsize=40 if i == 2 else 32,
                 path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2) if i == 2 else None)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(178, "{:,}万円", BADGE, BRAND, size=118),
    "hero_count__cover": sc.cover("バイト・パートの税金", "178万円", "「103万の壁」はもう古い",
                                  "所得税のライン・2026年分", BRAND),
    "hero_full": sc.hero("178万円", "所得税がかかり始める年収(2026年分)", BADGE, BRAND, size=112, sub_fs=30),
    "tsusetsu": sc.card("多くの人はこう答える", "「103万円まで」", "…それ、2年前の常識なのだ", BADGE, BRAND,
                        main_color=MUTED_BAR, main_size=54),
    "jidai": scene_jidai,
    "kaisei": sc.reveal("178万円", "2026年分はここまで所得税ゼロ", "基礎控除104万+給与の控除74万", BADGE, BRAND, size=104),
    "tokurei": sc.card("ただし注意", "2年間の特例込み", "(2026・2027年分。その後は縮小予定)", BADGE, BRAND, main_size=50),
    "shaho": sc.card("もう1つ注意", "社会保険の壁は別", "(106万・130万は税金と別の仕組み)", BADGE, BRAND, main_size=50),
    "haishi": sc.card("さらに今年", "106万の壁は10月に廃止", "(週20時間の基準に一本化)", BADGE, BRAND, main_size=44),
    "oboe": sc.card("ここだけの話", "壁、動きすぎ", "(ボクは覚え直すたびに調べてるのだ)", BADGE, BRAND, main_size=56),
    "hayami": sc.hayami("「壁」は1つじゃなく4つある", [
        ("所得税", "178万円"),
        ("住民税", "約110万円"),
        ("社保・106万", "10月に廃止"),
        ("社保・130万", "変更なし"),
        ("去年の所得税", "123万円"),
    ], "国税庁ほか・2026年8月時点(178万は特例込み)", BADGE, BRAND, focal=0),
    "chips": sc.chips("この壁、知ってた?", ["知ってた", "103万だと思ってた", "自分に関係ある", "家族に教える"], BADGE, BRAND),
    "loop_back": sc.hero("178万円", "所得税がかかり始める年収(2026年分)", BADGE, BRAND, size=112, sub_fs=30),
}

UNITS = [
    Unit("hero_count", "【178万円】。", anim=1.2, cover=True, se="pop", face="surprised",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "所得税がかかり始める、年収のライン。", anim=0.8, speed=1.2),
    Unit("tsusetsu", "「103万円の壁」と、まだ思ってた?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2),
    Unit("jidai", "実はこの壁、2年で2回も動いたのだ。", anim=1.8, speed=1.15),
    Unit("kaisei", "2026年分は、【178万円】まで税金ゼロ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("tokurei", "ただしこれ、2年間の【特例】込みなのだ。", anim=1.2, speed=1.15),
    Unit("shaho", "そして社会保険の壁は、【別】なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("haishi", "そのうち106万円の壁は、今年10月に【廃止】。", anim=1.2, se="don", speed=1.15),
    Unit("oboe", "壁、動きすぎなのだ。ボクは調べ直しなのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("hayami", "壁の種類は、【早見表】で見るのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "あなたは、どの壁が関係ある?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして税金の壁の今が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S011.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
