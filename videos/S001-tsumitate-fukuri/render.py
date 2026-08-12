# S001「月1万円の積立は『意味ない』のか?」(v3) のレンダリング
# プロット: script.md(plot-playbook.md D1〜D22準拠) / 数値: verify.py と同式をassert照合
# 実行: リポジトリルートで python3 videos/S001-tsumitate-fukuri/render.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "production"))

import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch
from shortlib import (
    Unit, render_video, ease_out, ease_in_out, stroke_fx, style_axes,
    draw_badge, draw_footer_brand, draw_rich_text, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, GRID, BASELINE, SERIES_1, SERIES_2, EMPH, GOLD,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

# ---- 数値(verify.py と同じ式) ----
MONTHLY = 10_000

def fv_man(annual_rate: float, years: int, monthly: int = MONTHLY) -> float:
    n = years * 12
    if annual_rate == 0:
        return monthly * n / 10_000
    r = annual_rate / 12
    return monthly * ((1 + r) ** n - 1) / r / 10_000

FV20_5 = fv_man(0.05, 20)          # ≈411
FV20_3 = fv_man(0.03, 20)          # ≈328
FV10_5 = fv_man(0.05, 10)          # ≈155
PRINCIPAL20 = fv_man(0.0, 20)      # 240
GAIN20 = FV20_5 - PRINCIPAL20      # ≈171
FV3MAN = fv_man(0.05, 20, 30_000)  # ≈1233
HALF_LINEAR = FV20_5 / 2           # ≈205.5(直線予想のフリ)
DAILY = MONTHLY / 30               # ≈333円

assert round(FV20_5) == 411 and round(PRINCIPAL20) == 240 and round(GAIN20) == 171
assert round(FV10_5) == 155 and round(FV20_5 - FV10_5) == 256
assert round(FV20_3) == 328 and round(FV3MAN) == 1233 and round(DAILY) == 333, "verify.pyと不一致"


# ---- シーン(painter(fig, t)) ----

def _hero(fig, value_man: int, sub: str | None, sub_alpha=1.0):
    draw_glow_text(fig, 0.5, 0.62, f"{value_man}万円", 118)
    if sub:
        fig.text(0.5, 0.52, sub, ha="center", va="center",
                 color=INK_2, fontsize=40, alpha=clamp01(sub_alpha))
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    _hero(fig, round(FV20_5 * ease_out(t)), None)


def scene_hero_full(fig, t):
    _hero(fig, round(FV20_5), "月1万円 × 20年", sub_alpha=clamp01(t))


def scene_hero_loop(fig, t):
    _hero(fig, round(FV3MAN * ease_out(t)), "月3万円 × 20年なら")
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
    # 敵(思い込み)を画面に言語化しつつ、元本だけの現実を見せる
    ax = _stacked_axes(fig)
    h = PRINCIPAL20 * ease_in_out(t)
    ax.bar([0], [h], width=0.5, color=SERIES_1, edgecolor=SURFACE, linewidth=3)
    ax.text(0.30, max(h / 2, 30), "自分で払った\n240万円", color=INK, fontsize=30,
            va="center", alpha=clamp01(t))
    fig.text(0.5, 0.90, "『どうせ意味ない』?", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def scene_stacked_full(fig, t):
    ax = _stacked_axes(fig)
    g = GAIN20 * ease_in_out(t)
    ax.bar([0], [PRINCIPAL20], width=0.5, color=SERIES_1, edgecolor=SURFACE, linewidth=3)
    ax.bar([0], [g], bottom=[PRINCIPAL20], width=0.5, color=GOLD, edgecolor=SURFACE, linewidth=3)
    ax.text(0.30, PRINCIPAL20 / 2, "自分で払った\n240万円", color=INK, fontsize=30, va="center")
    ax.text(0.30, PRINCIPAL20 + max(g / 2, 20), "勝手に増えた\n+171万円", color=INK, fontsize=30,
            va="center", alpha=clamp01(t))
    if t > 0.85:
        ax.text(0, PRINCIPAL20 + GAIN20 + 18, "計 411万円", color=INK, fontsize=40,
                ha="center", alpha=clamp01((t - 0.85) / 0.15))
    fig.text(0.5, 0.90, "内訳", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def scene_snowball(fig, t):
    # 複利=雪だるま: 転がるほど大きくなる雪玉(等アスペクトの軸に描く)
    ax = fig.add_axes([0.08, 0.40, 0.84, 0.46])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    slope_p1, slope_p2 = (0.2, 6.8), (9.8, 1.6)
    ax.plot([slope_p1[0], slope_p2[0]], [slope_p1[1], slope_p2[1]], color=BASELINE, linewidth=3)  # 坂
    m = (slope_p2[1] - slope_p1[1]) / (slope_p2[0] - slope_p1[0])

    def line_y(x):
        return slope_p1[1] + m * (x - slope_p1[0])

    snow = [(1.6, 0.45), (4.9, 0.95), (8.0, 1.75)]
    n_show = 1 + int(clamp01(t) * 2.999)  # tにつれて1→3個
    for i, (x, r0) in enumerate(snow[:n_show]):
        grow = ease_out(clamp01(t * 3 - i))
        r = r0 * max(grow, 0.15)
        # 雪玉は坂の上に接するように置く
        ax.add_patch(Circle((x, line_y(x) + r * 0.9), r, facecolor="#e8e6df", edgecolor=INK_2, linewidth=2))
    ax.text(1.6, 8.2, "利息", ha="center", color=INK_2, fontsize=26)
    ax.text(4.9, 7.6, "利息の利息", ha="center", color=INK_2, fontsize=26, alpha=clamp01(t * 3 - 1))
    ax.text(8.0, 7.2, "さらに…", ha="center", color=INK_2, fontsize=26, alpha=clamp01(t * 3 - 2))
    fig.text(0.5, 0.90, "複利(ふくり)", ha="center", color=INK, fontsize=40,
             path_effects=stroke_fx(INK, outline=8, fatten=2))
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
_YEARS = _MONTHS / 12


def _prediction_line(ax, alpha=1.0):
    # フリ:「直線で増える」という素朴な予想(0 → 20年で411万)
    ax.plot([0, 20], [0, FV20_5], color=MUTED, linewidth=3, linestyle=(0, (5, 4)), alpha=alpha)


def scene_predict(fig, t):
    ax = _curve_axes(fig)
    _prediction_line(ax, alpha=clamp01(t))
    a = clamp01(t * 2 - 1)
    ax.plot([10], [HALF_LINEAR], marker="o", markersize=12, color=MUTED, alpha=a)
    ax.annotate("10年目 = ちょうど半分?", (10, HALF_LINEAR), xytext=(2.2, HALF_LINEAR + 60),
                color=INK, fontsize=27, alpha=a)
    fig.text(0.5, 0.90, "よくある予想", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def scene_reveal(fig, t):
    # オチ: 実際の曲線は予想線の下を這う(10年目155万)
    ax = _curve_axes(fig)
    _prediction_line(ax, alpha=0.7)
    k = max(2, int(121 * ease_in_out(clamp01(t))))  # 10年目まで描く
    ax.plot(_YEARS[:k], _VALS[:k], color=SERIES_1, linewidth=4, solid_capstyle="round")
    if t >= 0.99:
        ax.plot([10], [FV10_5], marker="o", markersize=12, color=SERIES_1,
                markeredgecolor=SURFACE, markeredgewidth=2)
        ax.annotate("実際は 155万円", (10, FV10_5), xytext=(10.6, FV10_5 - 60),
                    color=INK, fontsize=27)
    fig.text(0.5, 0.90, "現実", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定")
    draw_footer_brand(fig, BRAND)


def scene_accel(fig, t):
    # 後半の爆発: 曲線が10年目から20年目まで伸び切る
    ax = _curve_axes(fig)
    _prediction_line(ax, alpha=0.4)
    k = 121 + int((241 - 121) * ease_in_out(clamp01(t)))
    ax.plot(_YEARS[:k], _VALS[:k], color=SERIES_1, linewidth=4, solid_capstyle="round")
    ax.plot([10], [FV10_5], marker="o", markersize=12, color=SERIES_1,
            markeredgecolor=SURFACE, markeredgewidth=2)
    if t >= 0.99:
        ax.plot([20], [FV20_5], marker="o", markersize=12, color=SERIES_1,
                markeredgecolor=SURFACE, markeredgewidth=2)
        # 後半10年の増加幅を右端の縦両矢印で示す
        ax.annotate("", xy=(21.6, FV20_5), xytext=(21.6, FV10_5),
                    arrowprops=dict(arrowstyle="<->", color=EMPH, linewidth=3))
        ax.plot([10, 21.6], [FV10_5, FV10_5], color=GRID, linewidth=1.5, linestyle=(0, (3, 3)))
        fig.text(0.5, 0.385, f"後半10年だけで +{round(FV20_5 - FV10_5)}万円",
                 ha="center", color=EMPH, fontsize=30,
                 path_effects=stroke_fx(EMPH, outline=7, fatten=2))
    fig.text(0.5, 0.90, "後半で爆発する", ha="center", color=INK_2, fontsize=34)
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
    ax.set_xticklabels(["年利5%", "年利3%", "何もしない"])
    ax.tick_params(axis="x", labelsize=28, colors=INK_2)
    ax.set_xlim(-0.6, 2.6)
    return ax


def _bar(ax, x, v, prog, label=None):
    if prog <= 0:
        return
    h = v * ease_in_out(clamp01(prog))
    ax.bar([x], [h], width=0.56, color=SERIES_1)
    if prog >= 1.0:
        ax.text(x, h + 12, label or f"{round(v)}万円", ha="center", color=INK, fontsize=30)


def scene_compare2(fig, t):
    ax = _compare_axes(fig)
    _bar(ax, 0, FV20_5, 1.0)
    _bar(ax, 1, FV20_3, t)
    fig.text(0.5, 0.90, "月1万円 × 20年", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "利回りは仮定値")
    draw_footer_brand(fig, BRAND)


def scene_compare0(fig, t):
    ax = _compare_axes(fig)
    _bar(ax, 0, FV20_5, 1.0)
    _bar(ax, 1, FV20_3, 1.0)
    _bar(ax, 2, PRINCIPAL20, t, label="240万円(増え +0円)")
    fig.text(0.5, 0.90, "月1万円 × 20年", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "利回りは仮定値")
    draw_footer_brand(fig, BRAND)


def scene_lever(fig, t):
    # アハ: 選べるのは利回りじゃなく積立額
    fig.text(0.5, 0.90, "選べるのはどっち?", ha="center", color=INK_2, fontsize=34)
    fig.text(0.36, 0.68, "利回り", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=8, fatten=2))
    fig.text(0.68, 0.68, "×", ha="center", va="center", color=MUTED, fontsize=64)
    a = clamp01(t * 2 - 0.6)
    fig.text(0.36, 0.55, "積立額", ha="center", color=EMPH, fontsize=52,
             path_effects=stroke_fx(EMPH, outline=8, fatten=2), alpha=1.0)
    fig.text(0.68, 0.55, "◯", ha="center", va="center", color=EMPH, fontsize=64, alpha=a)
    draw_badge(fig, "利回りは仮定値")
    draw_footer_brand(fig, BRAND)


def scene_coin(fig, t):
    draw_glow_text(fig, 0.5, 0.64, "1日 333円", 96)
    fig.text(0.5, 0.53, "= 月1万円 ÷ 30日", ha="center", color=INK_2, fontsize=36, alpha=clamp01(t))
    draw_footer_brand(fig, BRAND)


def _table(fig, y0, dx=0.19, dy=0.06, fs=28):
    rates = [0.03, 0.05, 0.07]
    yearss = [10, 20, 30]
    x0 = 0.36
    for j, ys in enumerate(yearss):
        fig.text(x0 + dx * j, y0, f"{ys}年", ha="center", color=MUTED, fontsize=fs - 2)
    for i, rt in enumerate(rates):
        fig.text(x0 - 0.16, y0 - dy * (i + 1), f"{rt:.0%}", ha="center", color=MUTED, fontsize=fs - 2)
        for j, ys in enumerate(yearss):
            fig.text(x0 + dx * j, y0 - dy * (i + 1), f"{round(fv_man(rt, ys))}万",
                     ha="center", color=INK, fontsize=fs)


def scene_table_big(fig, t):
    fig.text(0.5, 0.88, "月1万円積立の早見表", ha="center", color=INK, fontsize=38,
             path_effects=stroke_fx(INK, outline=7, fatten=2))
    # スクショを促す点線フレーム
    fig.patches.append(FancyBboxPatch(
        (0.10, 0.42), 0.80, 0.36, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.86, 0.795, "スクショ用", ha="right", color=EMPH, fontsize=24,
             alpha=clamp01(t))
    _table(fig, 0.70, dy=0.07, fs=32)
    fig.text(0.5, 0.435, "計算方式: 毎月末積立・月次複利", ha="center", color=MUTED, fontsize=20)
    draw_badge(fig, "利回りは仮定値")
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.80, "あなたなら、月いくら?", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=9, fatten=3))
    chips = ["5千円", "1万円", "3万円", "それ以上"]
    for i, c in enumerate(chips):
        a = clamp01(t * 3.2 - i * 0.7)  # 順にポップ(V4)
        if a <= 0:
            continue
        x = 0.29 + (i % 2) * 0.42
        y = 0.66 - (i // 2) * 0.10
        fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=34, alpha=a,
                 bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                           edgecolor=EMPH, linewidth=2.5, alpha=a))
    fig.text(0.5, 0.44, "▼ コメントで教えて ▼", ha="center", color=INK_2, fontsize=34,
             alpha=clamp01(t * 3.2 - 3))
    draw_badge(fig, "利回りは仮定値")
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": scene_hero_count,
    "hero_full": scene_hero_full,
    "stacked_principal": scene_stacked_principal,
    "stacked_full": scene_stacked_full,
    "snowball": scene_snowball,
    "predict": scene_predict,
    "reveal": scene_reveal,
    "accel": scene_accel,
    "compare2": scene_compare2,
    "compare0": scene_compare0,
    "lever": scene_lever,
    "hero_loop": scene_hero_loop,
    "coin": scene_coin,
    "table_big": scene_table_big,
    "chips": scene_chips,
}

UNITS = [
    Unit("hero_count", "【411万円】。", anim=1.2, cover=True, se="pop", intonation=1.15),
    Unit("hero_full", "月1万円を20年、積み立てた結果。", anim=0.8),
    Unit("stacked_principal", "『意味ない』はずが、払ったのは【240万円】だけ。", anim=2.2),
    Unit("stacked_full", "残りの【171万円】は、勝手に増えたのだ。", anim=1.8),
    Unit("snowball", "正体は、利息が利息を生む【雪だるま】なのだ。", anim=2.4),
    Unit("predict", "なら10年目は、ちょうど半分と思うのだ?", anim=1.6),
    Unit("reveal", "違って、10年目はまだ【155万円】なのだ。", anim=1.8, se="don", intonation=1.1),
    Unit("accel", "でも後半の10年で、一気に【+256万円】。", anim=1.6),
    Unit("compare2", "控えめな3%でも、【328万円】なのだ。", anim=1.4),
    Unit("compare0", "何もしなければ、増えは【ゼロ】なのだ。", anim=1.4),
    Unit("lever", "あなたが選べるのは、【積立額】なのだ。", anim=1.2, pad=0.35),
    Unit("hero_loop", "月3万円にすると…【1233万円】なのだ。", anim=1.2, se="don", intonation=1.15),
    Unit("coin", "月1万円なら、1日たった【333円】。", anim=0.8),
    Unit("table_big", "【早見表】で、月いくらか決めるのだ。", anim=0.8, se="pop"),
    Unit("chips", "コメントで教えてほしいのだ。", anim=1.4, pad=1.0),
]

if __name__ == "__main__":
    result = render_video(UNITS, SCENES, OUTDIR, "S001.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
