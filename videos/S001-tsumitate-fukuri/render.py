# S001「月1万円を20年積み立てると、いくらになる?」(v2) のレンダリング
# 制作ルール: docs/research/short-video-format.md R1〜R14
# 実行: リポジトリルートで python3 videos/S001-tsumitate-fukuri/render.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "production"))

import numpy as np
from shortlib import (
    Unit, render_video, ease_out, stroke_fx, style_axes,
    draw_badge, draw_footer_brand, draw_rich_text,
    SURFACE, INK, INK_2, MUTED, GRID, BASELINE, SERIES_1, SERIES_2, EMPH,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

# ---- 数値(verify.py と同じ式。台本の数字と一致することが必須) ----
MONTHLY = 10_000

def fv_man(annual_rate: float, years: int, monthly: int = MONTHLY) -> float:
    n = years * 12
    if annual_rate == 0:
        return monthly * n / 10_000
    r = annual_rate / 12
    return monthly * ((1 + r) ** n - 1) / r / 10_000

FV20_5 = fv_man(0.05, 20)        # ≈411
FV20_3 = fv_man(0.03, 20)        # ≈328
FV10_5 = fv_man(0.05, 10)        # ≈155
PRINCIPAL20 = fv_man(0.0, 20)    # 240
GAIN20 = FV20_5 - PRINCIPAL20    # ≈171
FV20_5_3MAN = fv_man(0.05, 20, 30_000)  # ≈1233

assert round(FV20_5) == 411 and round(FV20_3) == 328 and round(GAIN20) == 171
assert round(FV10_5) == 155 and round(FV20_5 - FV10_5) == 256
assert round(FV20_5_3MAN) == 1233, "verify.pyと不一致"


# ---- シーン描画(painter(fig, t)。tは0→1のアニメ進行度) ----

def _hero_number(fig, value_man: int, sub: str | None, sub_alpha: float = 1.0):
    fig.text(0.5, 0.62, f"{value_man}万円", ha="center", va="center",
             color=EMPH, fontsize=118, path_effects=stroke_fx(EMPH, outline=12, fatten=4))
    if sub:
        fig.text(0.5, 0.52, sub, ha="center", va="center",
                 color=INK_2, fontsize=40, alpha=clamp01(sub_alpha))
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    # R2: 冒頭1秒のカウントアップ
    _hero_number(fig, round(FV20_5 * ease_out(t)), None)


def scene_hero_full(fig, t):
    _hero_number(fig, round(FV20_5), "月1万円 × 20年", sub_alpha=clamp01(t))


def scene_hero_loop(fig, t):
    # R11: 冒頭と同じ構造の「別パターンの数字」で概念ループ
    _hero_number(fig, round(FV20_5_3MAN * ease_out(t)), "月3万円 × 20年なら",
                 sub_alpha=1.0)
    draw_badge(fig, "年利5%と仮定")


def _stacked_axes(fig):
    ax = fig.add_axes([0.16, 0.42, 0.68, 0.42])
    style_axes(ax)
    ax.grid(False)
    ax.set_xlim(-0.55, 0.75)
    ax.set_ylim(0, 460)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    return ax


def scene_stacked_principal(fig, t):
    ax = _stacked_axes(fig)
    h = PRINCIPAL20 * ease_out(t)
    ax.bar([0], [h], width=0.5, color=SERIES_1, edgecolor=SURFACE, linewidth=3)
    ax.text(0.30, max(h / 2, 30), "元本\n240万円", color=INK, fontsize=30, va="center", alpha=clamp01(t))
    ax.plot([0.27], [max(h / 2, 30)], marker="s", markersize=14, color=SERIES_1,
            clip_on=False, alpha=clamp01(t))
    fig.text(0.5, 0.90, "内訳", ha="center", color=INK_2, fontsize=32)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def scene_stacked_full(fig, t):
    ax = _stacked_axes(fig)
    g = GAIN20 * ease_out(t)
    ax.bar([0], [PRINCIPAL20], width=0.5, color=SERIES_1, edgecolor=SURFACE, linewidth=3)
    ax.bar([0], [g], bottom=[PRINCIPAL20], width=0.5, color=SERIES_2, edgecolor=SURFACE, linewidth=3)
    ax.text(0.30, PRINCIPAL20 / 2, "元本\n240万円", color=INK, fontsize=30, va="center")
    ax.plot([0.27], [PRINCIPAL20 / 2], marker="s", markersize=14, color=SERIES_1, clip_on=False)
    ax.text(0.30, PRINCIPAL20 + max(g / 2, 20), "運用益\n+171万円", color=INK, fontsize=30,
            va="center", alpha=clamp01(t))
    ax.plot([0.27], [PRINCIPAL20 + max(g / 2, 20)], marker="s", markersize=14, color=SERIES_2,
            clip_on=False, alpha=clamp01(t))
    if t > 0.85:
        a = (t - 0.85) / 0.15
        ax.text(0, PRINCIPAL20 + GAIN20 + 18, "計 411万円", color=INK, fontsize=40,
                ha="center", alpha=clamp01(a))
    fig.text(0.5, 0.90, "内訳", ha="center", color=INK_2, fontsize=32)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def _curve_axes(fig):
    ax = fig.add_axes([0.14, 0.44, 0.74, 0.40])
    style_axes(ax)
    ax.set_xlim(0, 23.5)
    ax.set_ylim(0, 480)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xticklabels(["0年", "5年", "10年", "15年", "20年"])
    ax.set_yticks([100, 200, 300, 400])
    ax.set_yticklabels(["100万", "200万", "300万", "400万"])
    return ax


_MONTHS = np.arange(0, 241)
_R = 0.05 / 12
_VALS = np.where(_MONTHS == 0, 0.0, MONTHLY * ((1 + _R) ** _MONTHS - 1) / _R) / 10_000
_PRIN = MONTHLY * _MONTHS / 10_000
_YEARS = _MONTHS / 12


def scene_curve_draw(fig, t):
    # R4: 線が左から描かれる
    ax = _curve_axes(fig)
    k = max(2, int(len(_MONTHS) * t))
    ax.plot(_YEARS[:k], _VALS[:k], color=SERIES_1, linewidth=4, solid_capstyle="round")
    ax.plot(_YEARS[:k], _PRIN[:k], color=MUTED, linewidth=2.5, linestyle=(0, (4, 3)))
    fig.text(0.5, 0.90, "20年間の増え方", ha="center", color=INK_2, fontsize=32)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def scene_curve_annot(fig, t):
    ax = _curve_axes(fig)
    ax.plot(_YEARS, _VALS, color=SERIES_1, linewidth=4, solid_capstyle="round")
    ax.plot(_YEARS, _PRIN, color=MUTED, linewidth=2.5, linestyle=(0, (4, 3)))
    ax.text(20.3, _PRIN[-1], "元本", color=MUTED, fontsize=24, va="center")
    for y, v, dy in [(10, FV10_5, 40), (20, FV20_5, 30)]:
        ax.plot([y], [v], marker="o", markersize=12, color=SERIES_1,
                markeredgecolor=SURFACE, markeredgewidth=2, alpha=clamp01(t))
        ax.annotate(f"{y}年目 {round(v)}万円", (y, v), xytext=(y - 6.5, v + dy),
                    color=INK, fontsize=26, alpha=clamp01(t))
    fig.text(0.5, 0.90, "後半ほど加速する", ha="center", color=INK_2, fontsize=32)
    fig.text(0.5, 0.385, f"前半10年 +{round(FV10_5)}万円 → 後半10年 +{round(FV20_5 - FV10_5)}万円",
             ha="center", color=INK, fontsize=28, alpha=clamp01(t))
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def _compare_axes(fig):
    ax = fig.add_axes([0.14, 0.42, 0.74, 0.42])
    style_axes(ax)
    ax.grid(False)
    ax.set_ylim(0, 480)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["年利5%", "年利3%", "0%"])
    ax.tick_params(axis="x", labelsize=28, colors=INK_2)
    ax.set_xlim(-0.6, 2.6)
    return ax


_CMP_VALS = [FV20_5, FV20_3, PRINCIPAL20]


def _compare_bar(ax, x, v, prog):
    if prog <= 0:
        return
    h = v * ease_out(min(prog, 1.0))
    ax.bar([x], [h], width=0.56, color=SERIES_1)
    if prog >= 1.0:
        ax.text(x, h + 12, f"{round(v)}万円", ha="center", color=INK, fontsize=32)


def scene_compare_1(fig, t):
    ax = _compare_axes(fig)
    _compare_bar(ax, 0, _CMP_VALS[0], t)
    fig.text(0.5, 0.90, "月1万円 × 20年", ha="center", color=INK_2, fontsize=32)
    draw_badge(fig, "利回りは仮定値")
    draw_footer_brand(fig, BRAND)


def scene_compare_23(fig, t):
    ax = _compare_axes(fig)
    _compare_bar(ax, 0, _CMP_VALS[0], 1.0)
    _compare_bar(ax, 1, _CMP_VALS[1], t * 2)          # 前半で3%
    _compare_bar(ax, 2, _CMP_VALS[2], (t - 0.5) * 2)  # 後半で0%
    fig.text(0.5, 0.90, "月1万円 × 20年", ha="center", color=INK_2, fontsize=32)
    draw_badge(fig, "利回りは仮定値")
    draw_footer_brand(fig, BRAND)


def _mini_table(fig, y0):
    rates = [0.03, 0.05, 0.07]
    yearss = [10, 20, 30]
    x0, dx, dy = 0.34, 0.19, 0.05
    for j, ys in enumerate(yearss):
        fig.text(x0 + dx * j, y0, f"{ys}年", ha="center", color=MUTED, fontsize=24)
    for i, rt in enumerate(rates):
        fig.text(x0 - 0.15, y0 - dy * (i + 1), f"{rt:.0%}", ha="center", color=MUTED, fontsize=24)
        for j, ys in enumerate(yearss):
            fig.text(x0 + dx * j, y0 - dy * (i + 1), f"{round(fv_man(rt, ys))}万",
                     ha="center", color=INK, fontsize=26)


def scene_question(fig, t):
    # R11: 質問でコメント誘発。登録訴求はしない
    draw_rich_text(fig, 0.5, 0.70, "あなたなら", 64)
    draw_rich_text(fig, 0.5, 0.625, "月【いくら】積み立てる?", 64)
    draw_footer_brand(fig, BRAND)
    draw_badge(fig, "利回りは仮定値")


def scene_question_table(fig, t):
    scene_question(fig, 1.0)
    fig.text(0.5, 0.53, "▼ コメントで教えて ▼", ha="center", color=INK_2, fontsize=34)
    _mini_table(fig, 0.47)


SCENES = {
    "hero_count": scene_hero_count,
    "hero_full": scene_hero_full,
    "hero_loop": scene_hero_loop,
    "stacked_principal": scene_stacked_principal,
    "stacked_full": scene_stacked_full,
    "curve_draw": scene_curve_draw,
    "curve_annot": scene_curve_annot,
    "compare_1": scene_compare_1,
    "compare_23": scene_compare_23,
    "question": scene_question,
    "question_table": scene_question_table,
}

UNITS = [
    Unit("hero_count", "【411万円】。", anim=0.8),
    Unit("hero_full", "月1万円を20年、積み立てた結果なのだ。", anim=0.3),
    Unit("stacked_principal", "でも、自分で払ったのは【240万円】だけ。", anim=0.6),
    Unit("stacked_full", "残りの【171万円】は、勝手に増えたお金なのだ。", anim=0.6),
    Unit("curve_draw", "正体は【複利】。利息にも利息がつく仕組みなのだ。", anim=1.2),
    Unit("curve_annot", "だから後半ほど、増え方が加速するのだ。", anim=0.4),
    Unit("compare_1", "ただし年利5%は、あくまで【仮定】の話。", anim=0.5),
    Unit("compare_23", "控えめな3%でも、【328万円】になるのだ。", anim=0.7),
    Unit("hero_loop", "ちなみに月3万円なら、【1233万円】なのだ。", anim=0.8),
    Unit("question", "あなたなら、月いくら積み立てる?"),
    Unit("question_table", "コメントで教えてほしいのだ。", pad=1.0),
]

if __name__ == "__main__":
    result = render_video(UNITS, SCENES, OUTDIR, "S001.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
