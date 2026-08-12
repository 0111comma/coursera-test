#!/usr/bin/env python3
"""S008: 平均と中央値(10人の村+J-FLEC実データ)。shortlibでレンダリングする。

数値はverify.pyと同一の計算(村の例)+調査値の転記。assertで照合してから描画する。
バッジは全編「出典: J-FLEC 2025年調査」。
"""
import statistics
import sys
from pathlib import Path

from matplotlib.patches import Circle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_out_back, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "出典: J-FLEC 2025年調査"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---- 数値(verify.pyと同一計算+転記) ----
village = [100] * 9 + [9_100]
assert sum(village) / len(village) == 1_000 and statistics.median(village) == 100
SINGLE_AVG, SINGLE_MED = 919, 130
FAMILY_AVG, FAMILY_MED = 1_940, 720
assert round(SINGLE_AVG / SINGLE_MED) == 7, "verify.pyと不一致"


# ---- シーン ----

def _hero8(fig, main: str, sub: str | None = None, sub_alpha=1.0, size=104, sub_fs=32):
    draw_glow_text(fig, 0.5, 0.62, main, size)
    if sub:
        fig.text(0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=sub_fs, alpha=clamp01(sub_alpha))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    v = round(919 * ease_out(clamp01(t * 1.15)))
    draw_glow_text(fig, 0.5, 0.62, f"{v}万円", 112 * max(scale, 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    fig.text(0.5, 0.795, "単身の平均貯蓄", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "919万円", 126)
    fig.text(0.5, 0.435, "真ん中の人は 130万", ha="center", va="center", color=INK,
             fontsize=44, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.88, "出典: J-FLEC 2025年調査", ha="center", va="center",
             color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    _hero8(fig, "919万円", "単身世帯の平均の金融資産", sub_alpha=clamp01(t), size=112)


def scene_karakuri(fig, t):
    fig.text(0.5, 0.90, "多すぎ?と思ったら", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.60, "カラクリがある", ha="center", va="center", color=EMPH,
             fontsize=58 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(58), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def _draw_village(fig, t, highlight_rich=False, highlight_middle=False):
    """10人のドット(2行×5)。richは右下の1人(金・大きめ)"""
    for i in range(10):
        col, row = i % 5, i // 5
        x = 0.18 + col * 0.16
        y = 0.62 - row * 0.14
        a = clamp01(t * 4 - i * 0.25)
        if a <= 0:
            continue
        rich = (i == 9)
        r = 0.048 if rich else 0.034
        color = GOLD if rich else MUTED_BAR
        if highlight_middle and i == 4:
            color = EMPH
        alpha = a if (not highlight_rich or rich) else a * 0.45
        fig.patches.append(Circle((x, y), r, transform=fig.transFigure,
                                  facecolor=color, edgecolor=INK_2, linewidth=1.5, alpha=alpha))


def scene_mura(fig, t):
    fig.text(0.5, 0.90, "10人の村", ha="center", color=INK_2, fontsize=34)
    _draw_village(fig, t)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_mura2(fig, t):
    fig.text(0.5, 0.90, "10人の村", ha="center", color=INK_2, fontsize=34)
    _draw_village(fig, 1.0)
    a = clamp01(t * 2 - 0.3)
    fig.text(0.34, 0.40, "9人は 100万円", ha="center", va="center", color=INK_2, fontsize=30, alpha=a)
    fig.text(0.72, 0.40, "1人だけ 9100万円", ha="center", va="center", color=EMPH, fontsize=30,
             alpha=clamp01(t * 2 - 0.7),
             path_effects=stroke_fx(EMPH, outline=outline_for(30), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_avg(fig, t):
    fig.text(0.5, 0.90, "この村の平均", ha="center", color=INK_2, fontsize=34)
    _draw_village(fig, 1.0)
    a = clamp01(t * 2 - 0.3)
    draw_glow_text(fig, 0.5, 0.38, "平均 1000万円", 64 * max(ease_out_back(a), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_med(fig, t):
    fig.text(0.5, 0.90, "でも真ん中の人は", ha="center", color=INK_2, fontsize=34)
    _draw_village(fig, 1.0, highlight_middle=True)
    a = clamp01(t * 2 - 0.3)
    fig.text(0.5, 0.38, "100万円", ha="center", va="center", color=EMPH,
             fontsize=60 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(60), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_meimei(fig, t):
    _hero8(fig, "中央値", "順番に並べた「真ん中」の値", sub_alpha=clamp01(t * 2 - 0.4))


def scene_tane(fig, t):
    fig.text(0.5, 0.90, "平均のカラクリ", ha="center", color=INK_2, fontsize=34)
    _draw_village(fig, 1.0, highlight_rich=True)
    fig.text(0.5, 0.40, "一部のお金持ちが引き上げる", ha="center", va="center", color=INK,
             fontsize=34, alpha=clamp01(t * 2 - 0.4),
             path_effects=stroke_fx(INK, outline=outline_for(34), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_jitsu(fig, t):
    _hero8(fig, "130万円", "単身世帯の中央値(実データ)", sub_alpha=clamp01(t * 2 - 0.4), size=110)


def scene_nanabai(fig, t):
    fig.text(0.5, 0.90, "平均と中央値の差", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2 - 0.2)
    fig.text(0.5, 0.66, "平均 919万円", ha="center", va="center", color=MUTED, fontsize=40, alpha=a)
    fig.text(0.5, 0.56, "中央値 130万円", ha="center", va="center", color=INK, fontsize=44,
             alpha=a, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    draw_glow_text(fig, 0.5, 0.43, "約7倍", 76 * max(ease_out_back(clamp01(t * 2 - 0.7)), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_miru(fig, t):
    fig.text(0.5, 0.90, "実態と比べるなら", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.60, "中央値を見る", ha="center", va="center", color=EMPH,
             fontsize=60 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(60), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hayami(fig, t):
    fig.text(0.5, 0.88, "平均と中央値(2025年調査)", ha="center", color=INK, fontsize=36,
             path_effects=stroke_fx(INK, outline=outline_for(36), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.095, 0.42), 0.73, 0.36, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.115, 0.795, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    fig.text(0.44, 0.73, "平均", ha="center", color=MUTED, fontsize=27)
    fig.text(0.72, 0.73, "中央値", ha="center", color=MUTED, fontsize=27)
    rows = [("単身", "919万", "130万"), ("二人以上", "1940万", "720万")]
    for i, (n, a_, m) in enumerate(rows):
        yy = 0.655 - i * 0.08
        fig.text(0.22, yy, n, ha="center", color=MUTED, fontsize=27)
        fig.text(0.44, yy, a_, ha="center", color=INK, fontsize=31)
        fig.text(0.72, yy, m, ha="center", color=GOLD, fontsize=31)
    fig.text(0.46, 0.455, "J-FLEC「家計の金融行動に関する世論調査」", ha="center",
             color=MUTED, fontsize=19)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.76, "どっちを見てた?", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=outline_for(52), fatten=3))
    chips = ["平均", "中央値", "両方", "初めて知った"]
    for i, c in enumerate(chips):
        a = clamp01(t * 3.2 - i * 0.7)
        if a <= 0:
            continue
        x = 0.29 + (i % 2) * 0.42
        y = 0.66 - (i // 2) * 0.10
        fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=32, alpha=a,
                 bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                           edgecolor=EMPH, linewidth=2.5, alpha=a))
    fig.text(0.5, 0.40, "▼ コメントで教えて ▼", ha="center", va="center",
             color=MUTED, fontsize=30, alpha=clamp01(t * 2 - 1.0))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": scene_hero_count,
    "hero_count__cover": scene_hero_count__cover,
    "hero_full": scene_hero_full,
    "karakuri": scene_karakuri,
    "mura": scene_mura,
    "mura2": scene_mura2,
    "avg": scene_avg,
    "med": scene_med,
    "meimei": scene_meimei,
    "tane": scene_tane,
    "jitsu": scene_jitsu,
    "nanabai": scene_nanabai,
    "miru": scene_miru,
    "hayami": scene_hayami,
    "chips": scene_chips,
}

# Given-New: 各文は動画内で導入済みの語+新情報1つ
UNITS = [
    Unit("hero_count", "【919万円】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "単身世帯の、平均の金融資産。", anim=0.8, speed=1.2),
    Unit("karakuri", "多すぎ?でも【カラクリ】があるのだ。", anim=1.2,
         speed=1.15, intonation=1.2),
    Unit("mura", "10人の村で、考えるのだ。", anim=1.2, speed=1.15),
    Unit("mura2", "9人は貯金100万円、1人だけ【9100万円】。", anim=1.6, speed=1.15),
    Unit("avg", "この村の平均は、【1000万円】。", anim=1.2, se="don",
         speed=1.1, intonation=1.2, pause_scale=1.2),
    Unit("med", "でも真ん中の人は、【100万円】なのだ。", anim=1.2,
         speed=1.1, intonation=1.2, pitch=-0.04),
    Unit("meimei", "この真ん中が、【中央値】。", anim=1.0, speed=1.15),
    Unit("tane", "平均は、一部のお金持ちが【引き上げる】。", anim=1.4, speed=1.15),
    Unit("jitsu", "実データでも、単身の中央値は【130万円】。", anim=1.2, se="don",
         speed=1.1, intonation=1.15, pause_scale=1.2),
    Unit("nanabai", "平均919万との差は、【7倍】なのだ。", anim=1.4, speed=1.15, intonation=1.2),
    Unit("miru", "比べるなら、【中央値】を見るのだ。", anim=1.2, pad=0.3,
         speed=1.15, intonation=1.2),
    Unit("hayami", "【早見表】で、平均と中央値を見るのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "コメントで、教えてほしいのだ。", anim=1.4, pad=0.15,  # 即切りループ(⑦/⑭)
         speed=1.15, intonation=1.15),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S008.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
