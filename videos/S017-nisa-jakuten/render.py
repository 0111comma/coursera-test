#!/usr/bin/env python3
"""S017: NISAの弱点、損しても相殺できない(T7原文型)。数値はverify.pyとassert照合。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "損失50万円の例・2026年8月時点"

assert int(500_000 * 0.20315) == 101_575, "verify.pyと不一致"


def scene_genbun(fig, t):
    """固有シーン: 金融庁の注意書きを原文ベースで提示(T7)。"""
    from matplotlib.patches import FancyBboxPatch
    a = sc.clamp01(t * 1.6)
    fig.text(0.5, 0.90, "金融庁の説明には、こうある", ha="center", color=INK_2, fontsize=32)
    # 立ち絵(y0.245-0.465)を避け、引用枠ごと y>0.48 に収める
    fig.patches.append(FancyBboxPatch((0.10, 0.495), 0.80, 0.285, boxstyle="round,pad=0.015",
                                      transform=fig.transFigure, facecolor=SURFACE,
                                      edgecolor=MUTED, linewidth=2, alpha=a))
    fig.text(0.5, 0.725, "NISA口座の損失は", ha="center", color=INK, fontsize=34, alpha=a)
    fig.text(0.5, 0.660, "他の口座の利益と", ha="center", color=INK, fontsize=34, alpha=a)
    fig.text(0.5, 0.593, "損益通算できません", ha="center", color=EMPH, fontsize=38, alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(38), fatten=2))
    fig.text(0.5, 0.543, "(繰越控除もできません)", ha="center", color=INK_2, fontsize=26, alpha=a)
    fig.text(0.88, 0.512, "— 金融庁 NISA特設サイトより(要旨)", ha="right", color=INK_2,
             fontsize=20, alpha=a)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(101_575, "{:,}円", BADGE, BRAND, size=100,
                                lead="その損、税金で取り戻せる?"),
    "hero_count__cover": sc.cover("その損、税金で取り戻せる?", "10万1575円", "損しても取り戻せない税金",
                                  "損益通算の話・金融庁", BRAND, main_size=96),
    "hero_full": sc.hero("10万1575円", "「NISAの弱点」で消せなくなる税金(例)", BADGE, BRAND,
                         size=96, sub_fs=28),
    "zentei": sc.card("NISAといえば", "利益に税金ゼロ", "(そこは本当。じゃあ損したら?)", BADGE, BRAND,
                      main_size=54),
    "genbun": scene_genbun,
    "iikae": sc.reveal("ないもの扱い", "NISAの損は、税金の計算に使えない", "他の利益と相殺も、翌年への持ち越しも不可", BADGE, BRAND,
                       size=92),
    "kazei": sc.card("NISAじゃない普通の口座なら", "損50万で税0円にできる", "(利益50万−損50万=0。税101,575円が消える)", BADGE, BRAND,
                     main_size=42, head_fs=30),
    "nisa": sc.card("NISAの損50万は", "利益と相殺できない", "(利益50万に税101,575円がそのまま)", BADGE, BRAND,
                    main_size=46),
    "kurikoshi": sc.card("さらに", "翌年への繰越もなし", "(普通の口座なら3年ぶん持ち越せる)", BADGE, BRAND,
                         main_size=50,
                     ask="あなたはこの弱点、知ってた?"),
    "hachi": sc.card("ここだけの話", "泣きっ面に蜂", "(損した上に、税金でも使えないのだ)", BADGE, BRAND,
                     main_size=56),
    "balance": sc.card("それでも", "利益非課税は大きい", "(弱点も知った上で使うのだ)", BADGE, BRAND,
                       main_size=50),
    "chips": sc.chips("この弱点、知ってた?", ["知ってた", "初めて知った", "NISA使ってる", "これから調べる"], BADGE, BRAND),
    "loop_back": sc.hero("10万1575円", "「NISAの弱点」で消せなくなる税金(例)", BADGE, BRAND,
                         size=96, sub_fs=28),
}

UNITS = [
    Unit("hero_count", "【10万1575円】。", anim=1.2, cover=True, se="pop", face="normal",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "NISAの弱点で、消せなくなる税金。",
         narration="ニーサの弱点で、消せなくなる税金。", anim=0.8, speed=1.2),
    Unit("zentei", "NISAは利益に税金ゼロ。…でも損したら?",
         narration="ニーサは利益に税金ゼロ。…でも損したら?", anim=1.2, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.2),
    Unit("genbun", "金融庁の説明には、こう書いてあるのだ。", anim=1.6, speed=1.15),
    Unit("iikae", "NISAの損は、【ないもの扱い】なのだ。",
         narration="ニーサの損は、ないもの扱いなのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("kazei", "普通の口座なら、損50万で税10万を消せる。", anim=1.2, speed=1.1),
    Unit("nisa", "NISAの損50万は、それができないのだ。",
         narration="ニーサの損50万は、それができないのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("kurikoshi", "翌年に持ち越す【繰越】も、できないのだ。", anim=1.2, se="don", speed=1.15),
    Unit("hachi", "損した上に使えない。泣きっ面に蜂なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("balance", "それでも、利益の非課税は大きいのだ。", anim=1.2, face="happy", speed=1.15),
    Unit("chips", "あなたはこの弱点、知ってた?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして弱点の値段が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S017.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
