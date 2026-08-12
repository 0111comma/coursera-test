#!/usr/bin/env python3
"""S004: 年収400万円の手取り(約8割)と天引きの内訳。shortlibでレンダリングする。

数値はverify.pyと同一の計算式から再計算し、assertで照合してから描画する。
バッジは全編「2026年度・東京の概算」(モデル条件はカバー注記+概要欄)。
"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_out_back, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年度・東京の概算"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---- 数値(verify.pyと同一計算) ----
INCOME = 4_000_000
SHAHO_PARTS = {
    "厚生年金": INCOME * 0.183 / 2,          # 366,000
    "健康保険": INCOME * 0.0985 / 2,         # 197,000
    "雇用ほか": INCOME * 0.0050 + INCOME * 0.0023 / 2,   # 24,600
}
SHAHO = sum(SHAHO_PARTS.values())            # 587,600
SHOTOKU = INCOME - (INCOME * 0.20 + 440_000)  # 給与所得 2,760,000
kazei_s = int((SHOTOKU - 880_000 - SHAHO) // 1000 * 1000)
SHOTOKUZEI = kazei_s * 0.05 * 1.021           # 65,957
kazei_j = int((SHOTOKU - 430_000 - SHAHO) // 1000 * 1000)
JUMINZEI = kazei_j * 0.10 - 2_500 + 5_000     # 176,700
TOTAL_OFF = SHAHO + SHOTOKUZEI + JUMINZEI     # 830,257
TEDORI = INCOME - TOTAL_OFF                   # 3,169,743

assert round(SHAHO_PARTS["厚生年金"] / 1000) == 366
assert round(SHAHO_PARTS["健康保険"] / 1000) == 197
assert round(SHAHO_PARTS["雇用ほか"] / 100) == 246
assert round(JUMINZEI / 1000) == 177 and round(SHOTOKUZEI / 1000) == 66
assert round(TOTAL_OFF / 10_000) == 83 and round(TEDORI / 10_000) == 317, "verify.pyと不一致"

# 内訳チャートの行(大きい順)。socialフラグ=社会保険料(ahaで金/グレーに色分け)
ROWS = [
    ("厚生年金", 36.6, True),
    ("健康保険", 19.7, True),
    ("住民税", 17.7, False),
    ("所得税", 6.6, False),
    ("雇用ほか", 2.5, True),
]
MAXV = 36.6


# ---- シーン ----

def scene_hero_count(fig, t):
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    v = round(83 * ease_out(clamp01(t * 1.15)))
    draw_glow_text(fig, 0.5, 0.62, f"{v}万円", 118 * max(scale, 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    fig.text(0.5, 0.795, "消える天引き", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "83万円", 132)
    fig.text(0.5, 0.435, "手取りは 約8割", ha="center", va="center", color=INK,
             fontsize=44, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.88, "年収400万円・2026年度・東京・独身の概算", ha="center", va="center",
             color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    draw_glow_text(fig, 0.5, 0.62, "83万円", 118)
    fig.text(0.5, 0.51, "年収400万円から引かれるお金", ha="center", va="center",
             color=INK_2, fontsize=34, alpha=clamp01(t))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_tedori(fig, t):
    draw_glow_text(fig, 0.5, 0.62, "317万円", 110)
    fig.text(0.5, 0.51, "手取り = 400万円の約8割", ha="center", va="center",
             color=INK_2, fontsize=34, alpha=clamp01(t * 2 - 0.4))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_bunkai(fig, t):
    fig.text(0.5, 0.66, "83万円の中身", ha="center", va="center", color=INK, fontsize=54,
             path_effects=stroke_fx(INK, outline=outline_for(54), fatten=3))
    fig.text(0.5, 0.53, "5つの天引き", ha="center", va="center", color=INK_2,
             fontsize=34, alpha=clamp01(t * 2 - 0.4))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_quiz(fig, t):
    fig.text(0.5, 0.90, "一番重いのは?", ha="center", color=INK_2, fontsize=34)
    chips = ["所得税", "住民税", "健康保険", "厚生年金"]
    for i, c in enumerate(chips):
        a = clamp01(t * 3.2 - i * 0.5)
        if a <= 0:
            continue
        x = 0.29 + (i % 2) * 0.42
        y = 0.68 - (i // 2) * 0.11
        fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=34, alpha=a,
                 bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                           edgecolor=EMPH, linewidth=2.5, alpha=a))
    draw_glow_text(fig, 0.5, 0.44, "?", 90 * max(ease_out_back(clamp01(t * 2 - 0.8)), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def _breakdown(fig, t, n_show, headline, recolor=False):
    """内訳チャート: 名前(左)+比例バー+金額(右端固定=見切れなし)。1本ずつ開示"""
    fig.text(0.5, 0.90, headline, ha="center", color=INK_2, fontsize=34)
    for i, (name, v, social) in enumerate(ROWS[:n_show]):
        a = clamp01(t * 2.5) if i == n_show - 1 else 1.0
        y = 0.72 - i * 0.075
        if recolor:
            color = GOLD if social else MUTED_BAR
        else:
            color = GOLD if i == n_show - 1 else MUTED_BAR
        fig.text(0.34, y, name, ha="right", va="center", color=INK_2, fontsize=29, alpha=a)
        fig.add_artist(FancyBboxPatch(
            (0.37, y - 0.017), max(0.30 * (v / MAXV) * ease_out(a), 0.012), 0.034,
            boxstyle="round,pad=0.004", transform=fig.transFigure,
            facecolor=color, edgecolor="none", alpha=a))
        fig.text(0.86, y, f"{v}万", ha="right", va="center", color=INK, fontsize=30, alpha=a)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_ans(fig, t):
    _breakdown(fig, t, 1, "正解: 厚生年金")


def scene_kenpo(fig, t):
    _breakdown(fig, t, 2, "83万円の中身")


def scene_jumin(fig, t):
    _breakdown(fig, t, 3, "83万円の中身")


def scene_shotoku(fig, t):
    _breakdown(fig, clamp01(t * 1.4), 5, "83万円の中身")


def scene_aha(fig, t):
    _breakdown(fig, 1.0, 5, "金色 = 社会保険料(約59万円)", recolor=True)


def scene_hosho(fig, t):
    fig.text(0.5, 0.90, "社会保険料のゆくえ", ha="center", color=INK_2, fontsize=34)
    rows = [("厚生年金", "老後などの年金に"), ("健康保険", "医療費が3割負担に")]
    for i, (a_, b) in enumerate(rows):
        al = clamp01(t * 2.5 - i * 0.6)
        y = 0.66 - i * 0.12
        fig.text(0.30, y, a_, ha="center", va="center", color=EMPH, fontsize=36, alpha=al,
                 path_effects=stroke_fx(EMPH, outline=outline_for(36), fatten=1.5))
        fig.text(0.455, y, "→", ha="center", va="center", color=MUTED, fontsize=36, alpha=al)
        fig.text(0.52, y, b, ha="left", va="center", color=INK, fontsize=33, alpha=al,
                 path_effects=stroke_fx(INK, outline=outline_for(33), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_meisai(fig, t):
    fig.text(0.5, 0.90, "給与明細の見方", ha="center", color=INK_2, fontsize=34)
    fig.patches.append(FancyBboxPatch(
        (0.16, 0.42), 0.62, 0.38, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5,
    ))
    fig.text(0.5, 0.765, "給与明細", ha="center", va="center", color=MUTED, fontsize=26)
    rows = [("支給", "400万円", INK_2, 0.685), ("控除", "-83万円", EMPH, 0.60),
            ("差引(手取り)", "317万円", INK, 0.515)]
    for name, v, c, y in rows:
        fig.text(0.22, y, name, ha="left", va="center", color=c, fontsize=30)
        fig.text(0.72, y, v, ha="right", va="center", color=c, fontsize=32)
    a = clamp01(t * 2 - 0.5)
    fig.add_artist(FancyBboxPatch(
        (0.19, 0.575), 0.56, 0.052, boxstyle="round,pad=0.006",
        transform=fig.transFigure, fill=False, edgecolor=EMPH, linewidth=3, alpha=a))
    fig.text(0.5, 0.445, "← この欄に内訳が全部ある", ha="center", va="center",
             color=EMPH, fontsize=24, alpha=clamp01(t * 2 - 0.9))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hayami(fig, t):
    fig.text(0.5, 0.88, "年収400万円の天引き", ha="center", color=INK, fontsize=38,
             path_effects=stroke_fx(INK, outline=outline_for(38), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.095, 0.38), 0.73, 0.40, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.115, 0.795, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    rows = [("厚生年金", "36万6千円"), ("健康保険", "19万7千円"), ("住民税", "17万7千円"),
            ("所得税", "6万6千円"), ("雇用保険+支援金", "約2万5千円"),
            ("合計", "約83万円"), ("手取り", "約317万円")]
    for i, (name, v) in enumerate(rows):
        y = 0.735 - i * 0.048
        c = EMPH if name in ("合計", "手取り") else (MUTED if i < 5 else INK)
        fig.text(0.30, y, name, ha="center", color=MUTED if i < 5 else EMPH, fontsize=25)
        fig.text(0.64, y, v, ha="center", color=INK if i < 5 else EMPH, fontsize=27)
    fig.text(0.46, 0.40, "2026年度・東京・独身・40歳未満の概算", ha="center",
             color=MUTED, fontsize=19)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.76, "明細、見てる?", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=outline_for(52), fatten=3))
    chips = ["毎月見てる", "たまに", "見てない", "紙がない"]
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
    "tedori": scene_tedori,
    "bunkai": scene_bunkai,
    "quiz": scene_quiz,
    "ans": scene_ans,
    "kenpo": scene_kenpo,
    "jumin": scene_jumin,
    "shotoku": scene_shotoku,
    "aha": scene_aha,
    "hosho": scene_hosho,
    "meisai": scene_meisai,
    "hayami": scene_hayami,
    "chips": scene_chips,
}

# Given-New: 各文は動画内で導入済みの語+新情報1つ
UNITS = [
    Unit("hero_count", "【83万円】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "年収400万円から、引かれるお金。", anim=0.8, speed=1.2),
    Unit("tedori", "手取りは【317万円】、約8割なのだ。", anim=1.2, speed=1.15),
    Unit("bunkai", "引かれた83万円の、【中身】を見るのだ。", anim=1.2, speed=1.2),
    Unit("quiz", "一番重いのは…【どれ】だと思うのだ?", anim=1.6,
         speed=1.15, intonation=1.25),
    Unit("ans", "正解は【厚生年金】。36万6千円なのだ。", anim=1.4, se="don",
         speed=1.1, intonation=1.2, pitch=-0.04, pause_scale=1.3),
    Unit("kenpo", "健康保険は、【19万7千円】なのだ。", anim=1.2, speed=1.15),
    Unit("jumin", "住民税は、【17万7千円】。", anim=1.0, speed=1.15),
    Unit("shotoku", "所得税は、意外と【6万6千円】。", anim=1.4, speed=1.15, intonation=1.2),
    Unit("aha", "重いのは税金より、【社会保険料】。", anim=1.2, se="don",
         speed=1.1, intonation=1.2, pitch=-0.04, pause_scale=1.2),
    Unit("hosho", "そのぶん、年金や医療の【保障】つき。", anim=1.4, speed=1.15),
    Unit("meisai", "明細の【控除欄】に、全部あるのだ。", anim=1.4, pad=0.3,
         speed=1.1, intonation=1.15),
    Unit("hayami", "【早見表】で、内訳を見るのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "コメントで、教えてほしいのだ。", anim=1.4, pad=0.15,  # 即切りループ(⑦/⑭)
         speed=1.15, intonation=1.15),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S004.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
