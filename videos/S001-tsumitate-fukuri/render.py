# S001「月1万円の積立は意味ない?【20年分計算してみた】」(v4: コールド視聴者理解可能性版)
# プロット: script.md(plot-playbook.md D1〜D22 + 深掘り⑧P1〜P5準拠)
# 実行: リポジトリルートで python3 videos/S001-tsumitate-fukuri/render.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "production"))

import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_in_out, ease_out_back, stroke_fx, outline_for,
    style_axes, draw_badge, draw_footer_brand, draw_rich_text, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, GRID, BASELINE, SERIES_1, SERIES_2, EMPH, GOLD,
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
PIGGY = fv_man(0.0, 20)            # 240(貯金箱=利息ゼロ)
GAIN20 = FV20_5 - PIGGY            # ≈171
FV3MAN = fv_man(0.05, 20, 30_000)  # ≈1233
HALF_LINEAR = FV20_5 / 2           # ≈205.5(「半分」予想のフリ)
DAILY = MONTHLY / 30               # ≈333円

assert round(FV20_5) == 411 and round(PIGGY) == 240 and round(GAIN20) == 171
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
    # 深掘り④: 突発的な出現(スケールパンチ+オーバーシュート)+カウントアップ
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    value = round(FV20_5 * ease_out(clamp01(t * 1.15)))
    draw_glow_text(fig, 0.5, 0.62, f"{value}万円", 118 * max(scale, 0.05))
    draw_badge(fig, "年利5%と仮定の計算")  # 打消し表示は強調表示(411万)と同一画面に(ループ⑫)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    _hero(fig, round(FV20_5), "月1万円 × 20年", sub_alpha=clamp01(t))
    draw_badge(fig, "年利5%と仮定の計算")


def scene_hero_loop(fig, t):
    _hero(fig, round(FV3MAN * ease_out(t)), "月3万円 × 20年なら")
    draw_badge(fig, "利回りは仮定・元本保証なし")


def scene_gaman(fig, t):
    # H3/H5: 1233万の直後の本音(欲望の自虐)。数字を含む関連ユーモア(H1)
    fig.text(0.5, 0.90, "ここだけの本音", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.62, "月3千円で挫折しそう", ha="center", va="center", color=INK,
             fontsize=44 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.51, "(ボクの意志力の問題なのだ)", ha="center", va="center",
             color=MUTED, fontsize=26, alpha=clamp01(t * 2 - 0.8))
    draw_badge(fig, "年利5%と仮定の計算")
    draw_footer_brand(fig, BRAND)


def scene_loop_back(fig, t):
    # E6: ビジュアルループ(冒頭カバーと同構図の411万円)。2周目が答え合わせになる
    _hero(fig, round(FV20_5), "月1万円 × 20年", sub_alpha=clamp01(t * 2))
    draw_badge(fig, "年利5%と仮定の計算")


# ---- 貯金箱 vs 投資(深掘り⑧: 前提を絵で明示する) ----

def _duo_axes(fig):
    ax = fig.add_axes([0.14, 0.42, 0.72, 0.42])
    style_axes(ax)
    ax.grid(False)
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 470)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["貯金箱", "世界中の株"])  # 資産クラスで具体化。商品名は出さない(§6-1)
    ax.tick_params(axis="x", labelsize=30, colors=INK_2)
    return ax


def _duo_bar(ax, x, v, prog, color, label_done=None):
    if prog <= 0:
        return 0.0
    e = ease_in_out(clamp01(prog))
    h = v * e
    ax.bar([x], [h], width=0.5, color=color)
    if prog > 0.15:
        txt = label_done if (label_done and prog >= 1.0) else f"{round(v * e)}万円"
        ax.text(x, h + 12, txt, ha="center", color=INK, fontsize=30)
    return h


def scene_piggy(fig, t):
    # 誰でも分かる基準線(貯金箱=利息ゼロ)を先に置く
    ax = _duo_axes(fig)
    _duo_bar(ax, 0, PIGGY, t, SERIES_1)
    fig.text(0.5, 0.90, "もし貯金箱に入れてたら?", ha="center", color=INK_2, fontsize=34)
    draw_footer_brand(fig, BRAND)


def scene_invest(fig, t):
    # 前提の種明かし: 世界中の株に積み立てていたから増えた(+171万の差を明示)
    ax = _duo_axes(fig)
    _duo_bar(ax, 0, PIGGY, 1.0, MUTED_BAR)
    _duo_bar(ax, 1, FV20_5, t, GOLD)
    if t >= 0.85:
        a = clamp01((t - 0.85) / 0.15)
        ax.plot([0.32, 1.05], [PIGGY + 6, PIGGY + 6], color=GRID, linewidth=1.5,
                linestyle=(0, (3, 3)), alpha=a)
        ax.annotate("", xy=(1.38, FV20_5), xytext=(1.38, PIGGY),
                    arrowprops=dict(arrowstyle="<->", color=EMPH, linewidth=3, alpha=a))
        ax.text(1.47, (FV20_5 + PIGGY) / 2, f"+{round(GAIN20)}万円", color=EMPH,
                fontsize=27, va="center", ha="center", alpha=a, rotation=90)
    fig.text(0.5, 0.90, "世界中の株で運用した場合", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定の計算")
    draw_footer_brand(fig, BRAND)


def scene_assume(fig, t):
    # 仮定の明示を音声+画面の両方で(コンプライアンス兼、理解の前提)
    ax = _duo_axes(fig)
    _duo_bar(ax, 0, PIGGY, 1.0, MUTED_BAR)
    _duo_bar(ax, 1, FV20_5, 1.0, GOLD)
    a = clamp01(t * 2)
    fig.text(0.5, 0.345, "増え方の仮定: 年平均 5%", ha="center", va="center",
             color=INK, fontsize=34, alpha=a,
             bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                       edgecolor=EMPH, linewidth=2.5, alpha=a))
    fig.text(0.5, 0.90, "世界中の株で運用した場合", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定の計算")
    draw_footer_brand(fig, BRAND)


def scene_snowball(fig, t):
    ax = fig.add_axes([0.08, 0.40, 0.84, 0.46])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    slope_p1, slope_p2 = (0.2, 6.8), (9.8, 1.6)
    ax.plot([slope_p1[0], slope_p2[0]], [slope_p1[1], slope_p2[1]], color=BASELINE, linewidth=3)
    m = (slope_p2[1] - slope_p1[1]) / (slope_p2[0] - slope_p1[0])

    def line_y(x):
        return slope_p1[1] + m * (x - slope_p1[0])

    snow = [(1.6, 0.45), (4.9, 0.95), (8.0, 1.75)]
    n_show = 1 + int(clamp01(t) * 2.999)
    for i, (x, r0) in enumerate(snow[:n_show]):
        grow = ease_out(clamp01(t * 3 - i))
        r = r0 * max(grow, 0.15)
        ax.add_patch(Circle((x, line_y(x) + r * 0.9), r, facecolor="#e8e6df", edgecolor=INK_2, linewidth=2))
    ax.text(1.6, 8.2, "利息", ha="center", color=INK_2, fontsize=26)
    ax.text(4.9, 7.6, "利息の利息", ha="center", color=INK_2, fontsize=26, alpha=clamp01(t * 3 - 1))
    ax.text(8.0, 7.2, "さらに…", ha="center", color=INK_2, fontsize=26, alpha=clamp01(t * 3 - 2))
    fig.text(0.5, 0.90, "複利(ふくり)のしくみ", ha="center", color=INK, fontsize=40,
             path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2))
    draw_badge(fig, "年利5%と仮定の計算")
    draw_footer_brand(fig, BRAND)


def _curve_axes(fig):
    # 高さ0.37: 20年ラベル(グラフ上端)が拡大後バッジ(下端y=0.810)と重ならない高さ(ループ⑫)
    ax = fig.add_axes([0.14, 0.44, 0.74, 0.37])
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


def scene_predict(fig, t):
    # クイズのフリ: 「半分くらい?」という素朴な予想を可視化
    ax = _curve_axes(fig)
    a = clamp01(t)
    ax.plot([0, 20], [0, FV20_5], color=MUTED, linewidth=3, linestyle=(0, (5, 4)), alpha=a)
    ax.plot([20], [FV20_5], marker="o", markersize=12, color=MUTED, alpha=a)
    ax.text(20, FV20_5 + 25, "20年で411万円", ha="center", color=INK_2, fontsize=25, alpha=a)
    a2 = clamp01(t * 2 - 1)
    ax.plot([10], [HALF_LINEAR], marker="o", markersize=12, color=MUTED, alpha=a2)
    ax.annotate("半分なら 約205万円?", (10, HALF_LINEAR), xytext=(1.8, HALF_LINEAR + 65),
                color=INK, fontsize=27, alpha=a2)
    fig.text(0.5, 0.90, "クイズ: 10年目はいくら?", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定の計算")
    draw_footer_brand(fig, BRAND)


def scene_reveal(fig, t):
    # 正解: 実際の曲線は「半分」よりずっと下(まだ155万)
    ax = _curve_axes(fig)
    ax.plot([0, 20], [0, FV20_5], color=MUTED, linewidth=3, linestyle=(0, (5, 4)), alpha=0.55)
    ax.plot([10], [HALF_LINEAR], marker="o", markersize=10, color=MUTED, alpha=0.55)
    k = max(2, int(121 * ease_in_out(clamp01(t))))
    ax.plot(_YEARS[:k], _VALS[:k], color=SERIES_1, linewidth=4, solid_capstyle="round")
    if t < 0.99:
        ax.plot([_YEARS[k - 1]], [_VALS[k - 1]], marker="o", markersize=10, color=SERIES_1,
                markeredgecolor=SURFACE, markeredgewidth=2)
    if t >= 0.99:
        ax.plot([10], [FV10_5], marker="o", markersize=12, color=SERIES_1,
                markeredgecolor=SURFACE, markeredgewidth=2)
        ax.annotate("実際は 155万円", (10, FV10_5), xytext=(10.6, FV10_5 - 60),
                    color=INK, fontsize=27)
    fig.text(0.5, 0.90, "正解", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定の計算")
    draw_footer_brand(fig, BRAND)


def scene_accel(fig, t):
    # 深掘り⑧P4: 前半と後半を色分け領域+両方のラベルで比較(何の比較か一目で分かる)
    ax = _curve_axes(fig)
    a = clamp01(t)
    ax.axvspan(0, 10, color=MUTED_BAR, alpha=0.10)
    ax.axvspan(10, 20, color=GOLD, alpha=0.16 * a)
    k = 121 + int((241 - 121) * ease_in_out(clamp01(t)))
    ax.plot(_YEARS[:k], _VALS[:k], color=SERIES_1, linewidth=4, solid_capstyle="round")
    if t < 0.99:
        ax.plot([_YEARS[k - 1]], [_VALS[k - 1]], marker="o", markersize=10, color=SERIES_1,
                markeredgecolor=SURFACE, markeredgewidth=2)
    ax.plot([10], [FV10_5], marker="o", markersize=11, color=SERIES_1,
            markeredgecolor=SURFACE, markeredgewidth=2)
    ax.text(5, 437, "前半10年", ha="center", color=INK_2, fontsize=26)
    ax.text(5, 396, f"+{round(FV10_5)}万円", ha="center", color=INK_2, fontsize=28)
    if t >= 0.6:
        a2 = clamp01((t - 0.6) / 0.3)
        ax.plot([20], [FV20_5], marker="o", markersize=12, color=SERIES_1,
                markeredgecolor=SURFACE, markeredgewidth=2, alpha=a2)
        ax.text(15, 437, "後半10年", ha="center", color=INK_2, fontsize=26, alpha=a2)
        ax.text(15, 396, f"+{round(FV20_5 - FV10_5)}万円", ha="center", color=EMPH, fontsize=30,
                alpha=a2, path_effects=stroke_fx(EMPH, outline=outline_for(30), fatten=2))
    fig.text(0.5, 0.90, "伸びは後半に集中する", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "年利5%と仮定の計算")
    draw_footer_brand(fig, BRAND)


def _compare_axes(fig):
    ax = fig.add_axes([0.14, 0.42, 0.74, 0.42])
    style_axes(ax)
    ax.grid(False)
    ax.set_ylim(0, 480)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["年利5%", "年利3%", "貯金箱"])
    ax.tick_params(axis="x", labelsize=28, colors=INK_2)
    ax.set_xlim(-0.6, 2.6)
    return ax


def _bar(ax, x, v, prog, label=None, color=SERIES_1, counter=True):
    # 深掘り⑤: フォーカス1本だけアクセント色+数値カウンター連動
    if prog <= 0:
        return
    e = ease_in_out(clamp01(prog))
    h = v * e
    ax.bar([x], [h], width=0.56, color=color)
    if counter and prog > 0.15:
        txt = label if (label and prog >= 1.0) else f"{round(v * e)}万円"
        ax.text(x, h + 12, txt, ha="center", color=INK, fontsize=30)


def scene_compare2(fig, t):
    ax = _compare_axes(fig)
    _bar(ax, 0, FV20_5, 1.0, color=MUTED_BAR)
    _bar(ax, 1, FV20_3, t, color=GOLD)
    _bar(ax, 2, PIGGY, 1.0, color=MUTED_BAR)  # 貯金箱の基準線も文脈として表示(compare0廃止に伴い)
    fig.text(0.5, 0.90, "20年後の残高くらべ", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "利回りは仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_lever_no(fig, t):
    # 橋渡し(フリ): 比較→操作の転換。年利は選べない、を先に言う(オチ=lever)
    fig.text(0.5, 0.90, "自分で選べるのはどっち?", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2 - 0.3)
    fig.text(0.34, 0.68, "年利", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=outline_for(52), fatten=2))
    fig.text(0.70, 0.68, "×", ha="center", va="center", color=MUTED, fontsize=64, alpha=a)
    fig.text(0.70, 0.632, "選べない", ha="center", color=MUTED, fontsize=22, alpha=a)
    draw_badge(fig, "利回りは仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_lever(fig, t):
    fig.text(0.5, 0.90, "自分で選べるのはどっち?", ha="center", color=INK_2, fontsize=34)
    fig.text(0.34, 0.68, "年利", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=outline_for(52), fatten=2))
    fig.text(0.70, 0.68, "×", ha="center", va="center", color=MUTED, fontsize=64)
    fig.text(0.70, 0.632, "選べない", ha="center", color=MUTED, fontsize=26)
    a = clamp01(t * 2 - 0.6)
    fig.text(0.34, 0.53, "毎月の金額", ha="center", color=EMPH, fontsize=52,
             path_effects=stroke_fx(EMPH, outline=outline_for(52), fatten=2))
    fig.text(0.70, 0.53, "◯", ha="center", va="center", color=EMPH, fontsize=64, alpha=a)
    fig.text(0.70, 0.492, "選べる", ha="center", color=EMPH, fontsize=26, alpha=a)
    draw_badge(fig, "利回りは仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_coin(fig, t):
    draw_glow_text(fig, 0.5, 0.64, "1日 333円", 96)
    fig.text(0.5, 0.53, "= 月1万円 ÷ 30日", ha="center", color=INK_2, fontsize=36, alpha=clamp01(t))
    draw_footer_brand(fig, BRAND)


def _table(fig, y0, dx=0.18, dy=0.07, fs=32):
    rates = [0.03, 0.05, 0.07]
    yearss = [10, 20, 30]
    x0 = 0.35  # 深掘り⑩: 右ボタン列(x>0.85)にスクショ枠ごと収めるため左寄せ
    for j, ys in enumerate(yearss):
        fig.text(x0 + dx * j, y0, f"{ys}年", ha="center", color=MUTED, fontsize=fs - 2)
    for i, rt in enumerate(rates):
        fig.text(x0 - 0.16, y0 - dy * (i + 1), f"年利{rt:.0%}", ha="center", color=MUTED, fontsize=fs - 6)
        for j, ys in enumerate(yearss):
            fig.text(x0 + dx * j, y0 - dy * (i + 1), f"{round(fv_man(rt, ys))}万",
                     ha="center", color=INK, fontsize=fs)


def scene_table_big(fig, t):
    fig.text(0.5, 0.88, "月1万円積立の早見表", ha="center", color=INK, fontsize=38,
             path_effects=stroke_fx(INK, outline=outline_for(38), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.095, 0.42), 0.73, 0.36, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.115, 0.795, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    _table(fig, 0.70)
    fig.text(0.46, 0.435, "計算方式: 毎月末積立・月次複利", ha="center", color=MUTED, fontsize=24)
    draw_badge(fig, "利回りは仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    # y=0.76: バッジ(下端0.810)と質問の「ら?」が重ならない位置(ループ⑫で衝突を実測修正)
    fig.text(0.5, 0.76, "あなたなら、月いくら?", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=outline_for(52), fatten=3))
    chips = ["5千円", "1万円", "3万円", "それ以上"]
    for i, c in enumerate(chips):
        a = clamp01(t * 3.2 - i * 0.7)
        if a <= 0:
            continue
        x = 0.29 + (i % 2) * 0.42
        y = 0.66 - (i // 2) * 0.10
        fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=34, alpha=a,
                 bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                           edgecolor=EMPH, linewidth=2.5, alpha=a))
    fig.text(0.5, 0.44, "▼ コメントで教えて ▼", ha="center", color=INK_2, fontsize=34,
             alpha=clamp01(t * 3.2 - 3))
    draw_badge(fig, "利回りは仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    # 深掘り⑨: サムネ専用構図(字幕なし)。3〜5字のメイン+対比の一言で約束を伝える
    fig.text(0.5, 0.795, "月1万円 × 20年", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "411万円", 132)
    fig.text(0.5, 0.435, "貯金箱なら 240万円", ha="center", va="center", color=INK,
             fontsize=44, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    # サムネにも打消し表示(強調表示と同一画面の原則。ループ⑫)。⑨の3要素階層を崩さないようMUTED
    fig.text(0.5, 0.88, "年利5%と仮定の計算", ha="center", va="center", color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": scene_hero_count,
    "hero_count__cover": scene_hero_count__cover,
    "hero_full": scene_hero_full,
    "piggy": scene_piggy,
    "invest": scene_invest,
    "assume": scene_assume,
    "snowball": scene_snowball,
    "predict": scene_predict,
    "reveal": scene_reveal,
    "accel": scene_accel,
    "compare2": scene_compare2,
    "lever_no": scene_lever_no,
    "lever": scene_lever,
    "hero_loop": scene_hero_loop,
    "gaman": scene_gaman,
    "coin": scene_coin,
    "table_big": scene_table_big,
    "chips": scene_chips,
    "loop_back": scene_loop_back,
}

# 深掘り⑧: 各文は「動画内で導入済みの情報+新情報1つ」だけで構成する(Given-New)
UNITS = [
    Unit("hero_count", "【411万円】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "月1万円を20年、積み立てた結果。", anim=0.8, speed=1.2),
    # 誰でも分かる基準線(貯金箱=利息ゼロ)を先に置く
    Unit("piggy", "貯金箱に入れてたら、【240万円】のはず。", anim=1.8, speed=1.15),
    # 前提の種明かし: 世界中の株(全世界株式インデックス)に積み立てていたから増えた。
    # 「投資で運用」では曖昧(ユーザーレビュー第2弾)。商品名は出さない(戦略§6-1)
    Unit("invest", "でも【世界中の株】なら、+171万円。", anim=2.2,
         narration="でも世界中の株なら、プラス171万円。",
         speed=1.15, intonation=1.2),
    Unit("assume", "年5%で増えると【仮定】した計算なのだ。", anim=1.0, speed=1.15),
    Unit("snowball", "正体は、利息が利息を生む【雪だるま】。", anim=2.4,
         speed=1.15, intonation=1.15),
    # クイズ(フリ→オチ)
    Unit("predict", "では10年目は、半分くらいと思うのだ?", anim=1.6,
         speed=1.15, intonation=1.25),
    Unit("reveal", "実際は、まだ【155万円】しかないのだ。", anim=1.8,
         puchun=True, se="impact", se_at=0.34,  # フリーズ演出: プチュン(暗転)→ドーン
         speed=1.1, intonation=1.2, pitch=-0.06, pause_scale=1.4),
    Unit("accel", "後半の10年で、【+256万円】。", anim=1.6,
         narration="後半の10年で、プラス256万円。",
         speed=1.25, intonation=1.3, pitch=0.0),
    # 橋渡し(ユーザーレビュー第2弾)を1文に圧縮(E3: 尾の圧縮): 不確実性の明示+操作変数への転換
    Unit("lever", "利回りは選べない。選べるのは【金額】なのだ。", anim=1.2, pad=0.35,
         speed=1.15, intonation=1.2),
    Unit("hero_loop", "月3万円にすると…【1233万円】なのだ。", anim=1.2, se="don",
         narration="月3万円にすると…、1233万円なのだ。",
         speed=1.1, intonation=1.3, pitch=0.0, pause_scale=1.7),
    # H3+H5: 衝撃数字(1233万)直後の過剰リアクション+欲望の自虐(知識の自虐は禁止)
    Unit("gaman", "ボクは月3千円で、挫折しそうなのだ。", anim=1.2,
         speed=1.1, intonation=1.3, pitch=0.02),
    # H4のフォロー(正情報への復帰)+B6の人間スケール換算を兼ねる
    Unit("coin", "でも月1万円なら、1日【333円】。", anim=0.8, speed=1.2, intonation=1.15),
    Unit("table_big", "【早見表】で、月いくらか決めるのだ。", anim=0.8, se="pop", speed=1.2),
    # E7: 質問はループ点の5〜8秒前+N1の2人称+視聴者の数字を聞く(㉖)
    Unit("chips", "あなたなら、月いくらから始める?", anim=1.4, pad=0.15,
         speed=1.15, intonation=1.2),
    # E5/E6: ナラティブループ(→冒頭「411万円。」に接続)+ビジュアルループ(冒頭と同構図)
    Unit("loop_back", "その20年後の答えが、これなのだ。", anim=0.8, pad=0.1,
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S001.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
