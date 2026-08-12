#!/usr/bin/env python3
"""S003: 新NISAの生涯枠1800万円がうまるまでの年数。shortlibでレンダリングする。

利回り仮定を使わない動画(枠は簿価=元本ベースの割り算のみ)。
バッジは全編「2026年8月時点の制度」。読み上げ上書き: NISA→ニーサ/÷→わる/令和→れいわ。
"""
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
BADGE = "2026年8月時点の制度"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---- 数値(verify.pyと同一計算) ----
LIMIT_MAN = 1800
CASES = {0.5: 60_000, 1: 120_000, 3: 360_000, 5: 600_000, 10: 1_200_000}  # 月額万円→年間円
YEARS = {m: LIMIT_MAN * 10_000 / y for m, y in CASES.items()}
assert [int(YEARS[m]) for m in [0.5, 1, 3, 5, 10]] == [300, 150, 50, 30, 15]
assert LIMIT_MAN * 10_000 / 3_600_000 == 5.0
assert 2026 - 300 == 1726  # 「江戸から令和」の検算


# ---- シーン ----

def _hero3(fig, main: str, sub: str | None = None, sub_alpha=1.0, size=100, sub_fs=32):
    draw_glow_text(fig, 0.5, 0.62, main, size)
    if sub:
        fig.text(0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=sub_fs, alpha=clamp01(sub_alpha))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    v = round(50 * ease_out(clamp01(t * 1.15)))
    draw_glow_text(fig, 0.5, 0.62, f"{v}年", 132 * max(scale, 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    fig.text(0.5, 0.795, "枠がうまるまで", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "50年", 150)
    fig.text(0.5, 0.435, "満額なら 5年", ha="center", va="center", color=INK,
             fontsize=44, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.88, "NISAの生涯枠1800万円で計算", ha="center", va="center",
             color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    _hero3(fig, "50年", "月3万円でNISAの枠がうまる年数", sub_alpha=clamp01(t), size=132, sub_fs=34)


def scene_waku(fig, t):
    _hero3(fig, "1800万円", "非課税の枠・1人あたり(生涯)", sub_alpha=clamp01(t * 2 - 0.4))


def scene_calc1(fig, t):
    fig.text(0.5, 0.68, "月3万円 × 12ヶ月", ha="center", va="center", color=INK, fontsize=44,
             path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    a = clamp01(t * 2 - 0.4)
    draw_glow_text(fig, 0.5, 0.53, "= 年36万円", 66 * max(ease_out_back(a), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_calc2(fig, t):
    fig.text(0.5, 0.68, "1800万円 ÷ 36万円", ha="center", va="center", color=INK, fontsize=44,
             path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    a = clamp01(t * 2 - 0.5)
    draw_glow_text(fig, 0.5, 0.52, "= 50年", 84 * max(ease_out_back(a), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_quiz(fig, t):
    fig.text(0.5, 0.90, "クイズ", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.68, "月5千円なら?", ha="center", va="center", color=INK, fontsize=48,
             path_effects=stroke_fx(INK, outline=outline_for(48), fatten=2))
    a = clamp01(t * 2 - 0.4)
    draw_glow_text(fig, 0.5, 0.52, "?", 110 * max(ease_out_back(a), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_edo(fig, t):
    _hero3(fig, "300年", "1726年(江戸) → 2026年(令和)", sub_alpha=clamp01(t * 2 - 0.6), size=104)


def scene_m10(fig, t):
    _hero3(fig, "15年", "月10万円 = つみたて投資枠の上限", sub_alpha=clamp01(t * 2 - 0.4), size=104)


def scene_mangaku(fig, t):
    _hero3(fig, "5年", "満額 = 年間360万円(2つの枠の合計)", sub_alpha=clamp01(t * 2 - 0.4), size=104)


def scene_amaru(fig, t):
    fig.text(0.5, 0.90, "1800万円の枠は", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.60, "余るほど、大きい", ha="center", va="center", color=EMPH,
             fontsize=64 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(64), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_mukigen(fig, t):
    _hero3(fig, "無期限", "非課税の期限(恒久化)", sub_alpha=clamp01(t * 2 - 0.4))


def scene_gimu(fig, t):
    fig.text(0.5, 0.90, "枠を使い切る義務", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2 - 0.3)
    fig.text(0.5, 0.60, "×", ha="center", va="center", color=MUTED,
             fontsize=170 * max(ease_out_back(a), 0.05), alpha=a)
    fig.text(0.5, 0.44, "ないのだ", ha="center", va="center", color=INK, fontsize=44,
             alpha=clamp01(t * 2 - 0.8),
             path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hayami(fig, t):
    fig.text(0.5, 0.88, "枠がうまるまでの年数", ha="center", color=INK, fontsize=38,
             path_effects=stroke_fx(INK, outline=outline_for(38), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.095, 0.40), 0.73, 0.38, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.115, 0.795, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    fig.text(0.32, 0.735, "毎月", ha="center", color=MUTED, fontsize=28)
    fig.text(0.64, 0.735, "うまるまで", ha="center", color=MUTED, fontsize=28)
    rows = [("5千円", "300年"), ("1万円", "150年"), ("3万円", "50年"),
            ("5万円", "30年"), ("10万円", "15年")]
    for i, (m, y) in enumerate(rows):
        yy = 0.675 - i * 0.055
        fig.text(0.32, yy, m, ha="center", color=MUTED, fontsize=27)
        fig.text(0.64, yy, y, ha="center", color=INK, fontsize=30)
    fig.text(0.46, 0.425, "満額(年間360万円)なら5年。枠は元本ベースで計算",
             ha="center", color=MUTED, fontsize=20)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.76, "あなたの年数は?", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=outline_for(52), fatten=3))
    chips = ["15年以内", "30年", "50年", "それ以上"]
    for i, c in enumerate(chips):
        a = clamp01(t * 3.2 - i * 0.7)
        if a <= 0:
            continue
        x = 0.29 + (i % 2) * 0.42
        y = 0.66 - (i // 2) * 0.10
        fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=34, alpha=a,
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
    "waku": scene_waku,
    "calc1": scene_calc1,
    "calc2": scene_calc2,
    "quiz": scene_quiz,
    "edo": scene_edo,
    "m10": scene_m10,
    "mangaku": scene_mangaku,
    "amaru": scene_amaru,
    "mukigen": scene_mukigen,
    "gimu": scene_gimu,
    "hayami": scene_hayami,
    "chips": scene_chips,
}

# Given-New: 各文は動画内で導入済みの語+新情報1つ(S001/S002の視聴に依存しない)
UNITS = [
    Unit("hero_count", "【50年】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "月3万円で、NISAの枠がうまる年数。", anim=0.8,
         narration="月3万円で、ニーサの枠がうまる年数。", speed=1.2),
    Unit("waku", "非課税の枠は、1人【1800万円】。", anim=1.2, speed=1.15),
    Unit("calc1", "月3万円だと、年に【36万円】。", anim=1.2, speed=1.2),
    Unit("calc2", "1800万÷36万で、【50年】なのだ。", anim=1.6,
         narration="1800万わる36万で、50年なのだ。", speed=1.15, intonation=1.15),
    Unit("quiz", "では月5千円なら…何年だと思うのだ?", anim=1.4,
         speed=1.15, intonation=1.25),
    Unit("edo", "答えは【300年】。江戸から令和なのだ。", anim=1.4, se="don",
         narration="答えは300年。江戸かられいわなのだ。",
         speed=1.1, intonation=1.25, pause_scale=1.3),
    Unit("m10", "月10万円に増やしても、【15年】かかる。", anim=1.2, speed=1.2),
    Unit("mangaku", "満額、年間360万円でも、【5年】なのだ。", anim=1.2, speed=1.15),
    Unit("amaru", "つまり枠は、【余るほど】大きいのだ。", anim=1.2, se="don",
         speed=1.1, intonation=1.2, pitch=-0.04, pause_scale=1.2),
    Unit("mukigen", "しかも非課税は、【無期限】なのだ。", anim=1.0, speed=1.15),
    Unit("gimu", "枠を使い切る、義務はないのだ。", anim=1.0, pad=0.3,
         speed=1.1, intonation=1.15),
    Unit("hayami", "【早見表】で、自分の年数を見るのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "コメントで、教えてほしいのだ。", anim=1.4, pad=0.15,  # 即切りループ(⑦/⑭)
         speed=1.15, intonation=1.15),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S003.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
