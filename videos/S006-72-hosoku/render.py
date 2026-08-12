#!/usr/bin/env python3
"""S006: 72の法則(2倍になる年数の暗算)。shortlibでレンダリングする。

数値はverify.pyと同一の計算式から再計算し、assertで照合してから描画する。
バッジは全編「利回りは例・元本保証なし」。
"""
import math
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_out_back, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, EMPH,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "利回りは例・元本保証なし"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---- 数値(verify.pyと同一計算) ----
RATES = [1, 2, 3, 4, 5, 6, 7, 8]
RULE = {r: 72 / r for r in RATES}
EXACT5 = math.log(2) / math.log(1.05)                 # 14.21年
assert round(RULE[5], 1) == 14.4 and round(EXACT5, 1) == 14.2
assert RULE[1] == 72 and RULE[3] == 24 and round(RULE[7], 1) == 10.3 and RULE[2] == 36
assert all(abs(RULE[r] - math.log(2) / math.log(1 + r / 100)) / (math.log(2) / math.log(1 + r / 100)) < 0.04
           for r in RATES), "verify.pyと不一致"


# ---- シーン ----

def _hero6(fig, main: str, sub: str | None = None, sub_alpha=1.0, size=104, sub_fs=32):
    draw_glow_text(fig, 0.5, 0.62, main, size)
    if sub:
        fig.text(0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=sub_fs, alpha=clamp01(sub_alpha))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    v = round(14 * ease_out(clamp01(t * 1.15)))
    draw_glow_text(fig, 0.5, 0.62, f"{v}年", 132 * max(scale, 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    fig.text(0.5, 0.795, "2倍になるまで", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "14年", 150)
    fig.text(0.5, 0.435, "暗算で出せる", ha="center", va="center", color=INK,
             fontsize=44, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.88, "年5%運用の例・元本保証なし", ha="center", va="center",
             color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    _hero6(fig, "14年", "年5%運用のお金が2倍になる年数", sub_alpha=clamp01(t), size=132)


def scene_anzan(fig, t):
    fig.text(0.5, 0.90, "電卓は、いらない", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.60, "暗算で出せる", ha="center", va="center", color=EMPH,
             fontsize=62 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(62), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_num72(fig, t):
    _hero6(fig, "72", "魔法の数字", sub_alpha=clamp01(t * 2 - 0.4), size=150)


def scene_formula(fig, t):
    fig.text(0.5, 0.68, "72 ÷ 金利(%)", ha="center", va="center", color=INK, fontsize=48,
             path_effects=stroke_fx(INK, outline=outline_for(48), fatten=2))
    a = clamp01(t * 2 - 0.4)
    fig.text(0.5, 0.54, "= 2倍になる年数", ha="center", va="center", color=EMPH,
             fontsize=44, alpha=a, path_effects=stroke_fx(EMPH, outline=outline_for(44), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_example(fig, t):
    fig.text(0.5, 0.68, "72 ÷ 5", ha="center", va="center", color=INK, fontsize=48,
             path_effects=stroke_fx(INK, outline=outline_for(48), fatten=2))
    a = clamp01(t * 2 - 0.5)
    draw_glow_text(fig, 0.5, 0.52, "= 約14年", 80 * max(ease_out_back(a), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_quiz(fig, t):
    fig.text(0.5, 0.90, "クイズ", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.68, "年1%の預金なら?", ha="center", va="center", color=INK, fontsize=46,
             path_effects=stroke_fx(INK, outline=outline_for(46), fatten=2))
    a = clamp01(t * 2 - 0.4)
    draw_glow_text(fig, 0.5, 0.52, "?", 110 * max(ease_out_back(a), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_ans72(fig, t):
    _hero6(fig, "72年", "1%だと、ほぼ人生一周", sub_alpha=clamp01(t * 2 - 0.5), size=120)


def scene_r3(fig, t):
    _hero6(fig, "24年", "年3%の場合(72÷3)", sub_alpha=clamp01(t * 2 - 0.4))


def scene_r7(fig, t):
    _hero6(fig, "約10年", "年7%の場合(72÷7)", sub_alpha=clamp01(t * 2 - 0.4))


def scene_gosa(fig, t):
    fig.text(0.5, 0.90, "どれくらい正確?(年5%)", ha="center", color=INK_2, fontsize=34)
    rows = [("72の法則", "14.4年", EMPH), ("厳密な計算", "14.2年", INK)]
    for i, (name, v, c) in enumerate(rows):
        a = clamp01(t * 2.5 - i * 0.6)
        y = 0.65 - i * 0.11
        fig.text(0.32, y, name, ha="center", va="center", color=MUTED, fontsize=32, alpha=a)
        fig.text(0.68, y, v, ha="center", va="center", color=c, fontsize=44, alpha=a,
                 path_effects=stroke_fx(c, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.44, "誤差 わずか1.4%", ha="center", va="center", color=INK_2,
             fontsize=28, alpha=clamp01(t * 2 - 1.0))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_inflation(fig, t):
    fig.text(0.5, 0.90, "同じ法則をインフレに", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.68, "物価 年2%なら(72÷2)", ha="center", va="center", color=INK, fontsize=38,
             path_effects=stroke_fx(INK, outline=outline_for(38), fatten=2))
    a = clamp01(t * 2 - 0.4)
    fig.text(0.5, 0.53, "36年で 価値半分", ha="center", va="center", color=EMPH,
             fontsize=52 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(52), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hayami(fig, t):
    fig.text(0.5, 0.88, "2倍になるまでの年数", ha="center", color=INK, fontsize=38,
             path_effects=stroke_fx(INK, outline=outline_for(38), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.095, 0.36), 0.73, 0.42, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.115, 0.795, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    fig.text(0.30, 0.74, "年利", ha="center", color=MUTED, fontsize=26)
    fig.text(0.64, 0.74, "72÷金利", ha="center", color=MUTED, fontsize=26)
    for i, r in enumerate(RATES):
        yy = 0.695 - i * 0.038
        v = RULE[r]
        disp = f"{v:.0f}年" if v == int(v) else f"約{v:.1f}年"
        fig.text(0.30, yy, f"{r}%", ha="center", color=MUTED, fontsize=24)
        fig.text(0.64, yy, disp, ha="center", color=INK, fontsize=26)
    fig.text(0.46, 0.385, "利回りは例。厳密値との誤差は4%未満(概要欄)", ha="center",
             color=MUTED, fontsize=19)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.76, "この法則、知ってた?", ha="center", color=INK, fontsize=50,
             path_effects=stroke_fx(INK, outline=outline_for(50), fatten=3))
    chips = ["知ってた", "初めて知った", "使ってる", "今日覚えた"]
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
    "anzan": scene_anzan,
    "num72": scene_num72,
    "formula": scene_formula,
    "example": scene_example,
    "quiz": scene_quiz,
    "ans72": scene_ans72,
    "r3": scene_r3,
    "r7": scene_r7,
    "gosa": scene_gosa,
    "inflation": scene_inflation,
    "hayami": scene_hayami,
    "chips": scene_chips,
}

# Given-New: 各文は動画内で導入済みの語+新情報1つ
UNITS = [
    Unit("hero_count", "【14年】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "年5%運用のお金が、【2倍】になる年数。", anim=0.8, speed=1.2),
    Unit("anzan", "実はこれ、【暗算】で出せるのだ。", anim=1.2, speed=1.15, intonation=1.2),
    Unit("num72", "使うのは、【72】という数字。", anim=1.0, speed=1.15),
    Unit("formula", "72÷金利で、2倍になる年数が出る。", anim=1.4,
         narration="72わる金利で、2倍になる年数が出る。", speed=1.15),
    Unit("example", "72÷5で、約【14年】なのだ。", anim=1.2,
         narration="72わる5で、約14年なのだ。", speed=1.15, intonation=1.15),
    Unit("quiz", "では年1%の預金なら…【何年】?", anim=1.4,
         speed=1.15, intonation=1.25),
    Unit("ans72", "答えは【72年】。人生ほぼ一周なのだ。", anim=1.2, se="don",
         speed=1.1, intonation=1.25, pause_scale=1.3),
    Unit("r3", "年3%なら、【24年】。", anim=1.0, speed=1.15),
    Unit("r7", "年7%なら、【約10年】なのだ。", anim=1.0, speed=1.15),
    Unit("gosa", "この法則、誤差は【わずか】なのだ。", anim=1.4, speed=1.15),
    Unit("inflation", "逆に物価2%なら、36年で【価値半分】。", anim=1.4, se="don",
         speed=1.1, intonation=1.2, pitch=-0.04, pause_scale=1.2),
    Unit("hayami", "【早見表】で、年利別に見るのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "コメントで、教えてほしいのだ。", anim=1.4, pad=0.15,  # 即切りループ(⑦/⑭)
         speed=1.15, intonation=1.15),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S006.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
