# S001「月1万円の積立、20年後の答えがこれ」のレンダリング
# 実行: リポジトリルートで python3 videos/S001-tsumitate-fukuri/render.py
# 前提: VOICEVOXエンジンが127.0.0.1:50021で起動していること(なければOpen JTalkに落ちる)
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "production"))

import numpy as np
from shortlib import (
    Unit, render_video, new_canvas, style_axes,
    draw_badge, draw_footer_brand,
    SURFACE, INK, INK_2, MUTED, GRID, BASELINE, SERIES_1, SERIES_2,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"

# ---- 数値(verify.py と同じ式。台本の数字と一致することが必須) ----
MONTHLY = 10_000

def fv_man(annual_rate: float, years: int) -> float:
    """月1万円積立・月次複利の将来価値(万円)。annual_rate=0は元本のみ。"""
    n = years * 12
    if annual_rate == 0:
        return MONTHLY * n / 10_000
    r = annual_rate / 12
    return MONTHLY * ((1 + r) ** n - 1) / r / 10_000

FV20_5 = fv_man(0.05, 20)   # ≈411
FV20_3 = fv_man(0.03, 20)   # ≈328
FV10_5 = fv_man(0.05, 10)   # ≈155
PRINCIPAL20 = fv_man(0.0, 20)  # 240
GAIN20 = FV20_5 - PRINCIPAL20  # ≈171

assert round(FV20_5) == 411 and round(FV20_3) == 328 and round(GAIN20) == 171, "verify.pyと不一致"

# ---- シーン描画 ----

def scene_hero(fig):
    fig.text(0.5, 0.62, "411万円", ha="center", va="center", color=INK, fontsize=120)
    fig.text(0.5, 0.52, "月1万円 × 20年の答え", ha="center", va="center", color=INK_2, fontsize=40)
    draw_footer_brand(fig, BRAND)


def scene_stacked(fig):
    ax = fig.add_axes([0.16, 0.42, 0.68, 0.42])
    style_axes(ax)
    ax.grid(False)
    # 元本(青)+運用益(橙)の積み上げ。セグメント間は背景色の細い隙間
    ax.bar([0], [PRINCIPAL20], width=0.5, color=SERIES_1, edgecolor=SURFACE, linewidth=3)
    ax.bar([0], [GAIN20], bottom=[PRINCIPAL20], width=0.5, color=SERIES_2, edgecolor=SURFACE, linewidth=3)
    ax.set_xlim(-0.55, 0.75)
    ax.set_ylim(0, 460)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    # 直接ラベル(テキストはインク色、系列色はマーカーで示す)
    ax.text(0.30, PRINCIPAL20 / 2, "元本\n240万円", color=INK, fontsize=30, va="center")
    ax.text(0.30, PRINCIPAL20 + GAIN20 / 2, "運用益\n+171万円", color=INK, fontsize=30, va="center")
    ax.plot([0.27], [PRINCIPAL20 / 2], marker="s", markersize=14, color=SERIES_1, clip_on=False)
    ax.plot([0.27], [PRINCIPAL20 + GAIN20 / 2], marker="s", markersize=14, color=SERIES_2, clip_on=False)
    ax.text(0, PRINCIPAL20 + GAIN20 + 18, "計 411万円", color=INK, fontsize=40, ha="center")
    fig.text(0.5, 0.90, "内訳", ha="center", color=INK_2, fontsize=32)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def scene_curve(fig):
    ax = fig.add_axes([0.14, 0.44, 0.74, 0.40])
    style_axes(ax)
    months = np.arange(0, 241)
    r = 0.05 / 12
    vals = np.where(months == 0, 0.0, MONTHLY * ((1 + r) ** months - 1) / np.maximum(r, 1e-12)) / 10_000
    principal = MONTHLY * months / 10_000
    years = months / 12
    ax.plot(years, vals, color=SERIES_1, linewidth=4, solid_capstyle="round")
    ax.plot(years, principal, color=MUTED, linewidth=2.5, linestyle=(0, (4, 3)))
    # 10年目と20年目の直接ラベル
    for y, v, dy in [(10, FV10_5, 40), (20, FV20_5, 30)]:
        ax.plot([y], [v], marker="o", markersize=12, color=SERIES_1,
                markeredgecolor=SURFACE, markeredgewidth=2)
        ax.annotate(f"{y}年目 {round(v)}万円", (y, v), xytext=(y - 6.5, v + dy),
                    color=INK, fontsize=26)
    ax.text(20.3, principal[-1], "元本", color=MUTED, fontsize=24, va="center")
    ax.set_xlim(0, 23.5)
    ax.set_ylim(0, 480)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xticklabels(["0年", "5年", "10年", "15年", "20年"])
    ax.set_yticks([100, 200, 300, 400])
    ax.set_yticklabels(["100万", "200万", "300万", "400万"])
    # 前半・後半の増え幅を明示(複利の加速の種明かし)
    fig.text(0.5, 0.90, "増えるスピードは後半ほど速い", ha="center", color=INK_2, fontsize=32)
    fig.text(0.5, 0.385, f"前半10年 +{round(FV10_5)}万円 → 後半10年 +{round(FV20_5 - FV10_5)}万円",
             ha="center", color=INK, fontsize=28)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def scene_compare(fig):
    ax = fig.add_axes([0.14, 0.42, 0.74, 0.42])
    style_axes(ax)
    ax.grid(False)
    labels = ["年利5%", "年利3%", "0%"]
    vals = [FV20_5, FV20_3, PRINCIPAL20]
    xs = np.arange(3)
    ax.bar(xs, vals, width=0.56, color=SERIES_1)
    for x, v in zip(xs, vals):
        ax.text(x, v + 12, f"{round(v)}万円", ha="center", color=INK, fontsize=32)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.tick_params(axis="x", labelsize=28, colors=INK_2)
    ax.set_ylim(0, 480)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    fig.text(0.5, 0.90, "月1万円 × 20年", ha="center", color=INK_2, fontsize=32)
    draw_badge(fig, "利回りは仮定値")
    draw_footer_brand(fig, BRAND)


def scene_cta(fig):
    fig.text(0.5, 0.88, "月1万円積立の早見表", ha="center", color=INK_2, fontsize=32)
    rates = [0.03, 0.05, 0.07]
    yearss = [10, 20, 30]
    x0, y0, dx, dy = 0.30, 0.76, 0.20, 0.075
    fig.text(x0 - 0.14, y0, "", fontsize=24)
    for j, ys in enumerate(yearss):
        fig.text(x0 + dx * j, y0, f"{ys}年", ha="center", color=MUTED, fontsize=26)
    for i, rt in enumerate(rates):
        fig.text(x0 - 0.14, y0 - dy * (i + 1), f"{rt:.0%}", ha="center", color=MUTED, fontsize=26)
        for j, ys in enumerate(yearss):
            v = round(fv_man(rt, ys))
            fig.text(x0 + dx * j, y0 - dy * (i + 1), f"{v}万", ha="center", color=INK, fontsize=28)
    fig.text(0.5, 0.44, "つづきは解説動画で", ha="center", color=INK, fontsize=44)
    fig.text(0.5, 0.37, f"{BRAND}", ha="center", color=INK_2, fontsize=30)
    draw_badge(fig, "利回りは仮定値")


SCENES = {
    "hero": scene_hero,
    "stacked": scene_stacked,
    "curve": scene_curve,
    "compare": scene_compare,
    "cta": scene_cta,
}

UNITS = [
    Unit("hero", "411万円。月1万円を20年積み立てた結果です。", pad=0.45),
    Unit("stacked", "でも、自分で払ったお金は240万円だけ。"),
    Unit("stacked", "残りの171万円は、運用で増えた分です。", pad=0.45),
    Unit("curve", "カラクリは複利です。利息に、さらに利息がつくんです。"),
    Unit("curve", "だから最初の10年より、あとの10年のほうが、増えるスピードが速い。", pad=0.45),
    Unit("compare", "ちなみにこれは、年利5%と仮定した計算。"),
    Unit("compare", "もっと控えめに3%で計算しても、328万円です。ゼロなら、当然240万円のまま。", pad=0.45),
    Unit("cta", "何%で、何年やると、いくらになるのか。全パターンの早見表は、解説動画で見られます。", pad=0.6),
]

if __name__ == "__main__":
    result = render_video(UNITS, SCENES, OUTDIR, "S001.mp4", speaker=2)
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
