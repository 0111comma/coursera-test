"""再利用シーンビルダー(S010〜のバッチ制作用)。

painter(fig, t) を返すファクトリ群。デザイン規格は shortlib のトークンに従う。
量産型対策(format-variation.md 層C)として、各動画は最低1つ固有シーンを持つこと。
"""
from shortlib import (
    ease_out, ease_in_out, ease_out_back,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD, SERIES_1,
)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def clamp01(x):
    return max(0.0, min(1.0, x))


def hero_count(value: float, fmt: str, badge: str, brand: str, size: int = 112, decimals: int = 0,
               lead: str = ""):
    """冒頭の数字カウントアップ。fmt例: "{:,.0f}万円"

    lead: 数字の上に出す「前置き」= 視聴者の課題を自分ごと化する問い(ループ㊳・P1)。
    音声のフックは数字のまま(結果フックが最強)、画面で「これはあなたの話」を同時に伝える。
    """
    def painter(fig, t):
        appear = ease_out_back(clamp01(t * 3.4))
        scale = 0.25 + 0.75 * appear
        v = value * ease_out(clamp01(t * 1.15))
        if lead:
            fig.text(0.5, 0.775, lead, ha="center", va="center", color=INK, fontsize=42,
                     path_effects=stroke_fx(INK, outline=outline_for(42), fatten=2))
        draw_glow_text(fig, 0.5, 0.62, fmt.format(round(v, decimals) if decimals else round(v)),
                       size * max(scale, 0.05))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def hero(main: str, sub: str, badge: str, brand: str, size: int = 108, sub_fs: int = 32):
    def painter(fig, t):
        draw_glow_text(fig, 0.5, 0.62, main, size)
        fig.text(0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=sub_fs, alpha=clamp01(t * 2))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def cover(top: str, main: str, bottom: str, note: str, brand: str, main_size: int = 128):
    def painter(fig, t):
        fig.text(0.5, 0.795, top, ha="center", va="center", color=INK_2,
                 fontsize=44, path_effects=stroke_fx(INK_2, outline=outline_for(44), fatten=1.5))
        draw_glow_text(fig, 0.5, 0.615, main, main_size)
        fig.text(0.5, 0.435, bottom, ha="center", va="center", color=INK,
                 fontsize=42, path_effects=stroke_fx(INK, outline=outline_for(42), fatten=2))
        fig.text(0.5, 0.88, note, ha="center", va="center", color=INK_2, fontsize=28)
        draw_footer_brand(fig, brand)
    return painter


def card(headline: str, main: str, sub: str, badge: str, brand: str,
         main_color=EMPH, main_size: int = 54, sub_color=INK_2, sub_fs: int = 30,
         head_fs: int = 34, ask: str = ""):
    """見出し+ポップインする主役語+補足の汎用カード。

    ask: 中盤に重ねる二人称の問い(P4)。締めの4択と同趣旨の問いを先出しし、
    視聴者に「自分はどうだろう」と考えさせながら最後まで見せる。
    """
    def painter(fig, t):
        fig.text(0.5, 0.90, headline, ha="center", color=INK_2, fontsize=head_fs)
        if ask:
            fig.text(0.5, 0.775, ask, ha="center", color=EMPH, fontsize=31,
                     alpha=clamp01(t * 1.6 - 0.5))
        a = clamp01(t * 2)
        fig.text(0.5, 0.62, main, ha="center", va="center", color=main_color,
                 fontsize=main_size * max(ease_out_back(a), 0.05), alpha=a,
                 path_effects=stroke_fx(main_color, outline=outline_for(main_size), fatten=2.5))
        if sub:
            fig.text(0.5, 0.50, sub, ha="center", va="center",
                     color=sub_color, fontsize=sub_fs, alpha=clamp01(t * 2 - 0.8))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def quiz(headline: str, line1: str, line2: str, note: str, badge: str, brand: str):
    def painter(fig, t):
        fig.text(0.5, 0.88, headline, ha="center", color=INK, fontsize=36,
                 path_effects=stroke_fx(INK, outline=outline_for(36), fatten=2))
        fig.text(0.5, 0.68, line1, ha="center", va="center", color=INK_2, fontsize=38)
        fig.text(0.5, 0.60, line2, ha="center", va="center", color=INK, fontsize=44,
                 path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
        # 注記は立ち絵(y<0.465)より上に置く。「?」は細いので立ち絵の右側に落としてよい
        if note:
            fig.text(0.5, 0.52, note, ha="center", va="center", color=INK_2, fontsize=28)
        a = clamp01(t * 2 - 0.5)
        fig.text(0.5, 0.42, "?", ha="center", va="center", color=EMPH,
                 fontsize=110 * max(ease_out_back(a), 0.05), alpha=a,
                 path_effects=stroke_fx(EMPH, outline=outline_for(110), fatten=4))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def reveal(main: str, sub: str, formula: str, badge: str, brand: str, size: int = 96):
    """フリーズ演出つきリベール用(金額グロー+補足+根拠式)。

    立ち絵(y 0.245-0.465)に被らないよう、最下段の formula も y>0.48 に置く。
    """
    def painter(fig, t):
        draw_glow_text(fig, 0.5, 0.66, main, size)
        fig.text(0.5, 0.565, sub, ha="center", va="center",
                 color=INK_2, fontsize=32, alpha=clamp01(t * 2 - 0.3))
        if formula:
            fig.text(0.5, 0.495, formula, ha="center", va="center",
                     color=INK_2, fontsize=28, alpha=clamp01(t * 2 - 0.7))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def hayami(title: str, rows: list, note: str, badge: str, brand: str,
           col1: str = "", col2: str = "", focal: int | None = None):
    """まとめ表(ループ㊱で再設計。調査36ソース)。rows=[(名前, 値), ...] 5行推奨。

    - タイトルは名詞句でなく「結論を述べる文」(Assertion-Evidence法)
    - 枠・「スクショ用」ラベルは廃止(非データインク/ベイト構文)。密度と出典で保存価値を作る
    - 値は右揃え・太字・ラベルの約1.4倍(桁比較の定石)。強調はfocalの1セルのみ
    - 行はナレーションに合わせ順に点灯(セグメント化原理)
    - note には出典・時点(・仮定)を必ず入れる(スクショは単独で流通するため)
    """
    def painter(fig, t):
        fig.text(0.5, 0.885, title, ha="center", color=INK, fontsize=40,
                 path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2))
        y0 = 0.795
        dy = 0.066
        xl, xr = 0.14, 0.86
        for i, (n, v) in enumerate(rows):
            a = clamp01(t * 2.4 - i * 0.35)
            if a <= 0:
                continue
            y = y0 - i * dy
            f = (focal == i)
            fig.text(xl, y, n, ha="left", va="center", alpha=a,
                     color=INK if f else INK_2, fontsize=29)
            fig.text(xr, y, v, ha="right", va="center", alpha=a,
                     color=EMPH if f else INK, fontsize=40,
                     path_effects=stroke_fx(EMPH if f else INK,
                                            outline=outline_for(40), fatten=2) if f else None)
            if i < len(rows) - 1:
                fig.add_artist(plt.Line2D([xl, xr], [y - dy / 2, y - dy / 2],
                                          transform=fig.transFigure, color=MUTED,
                                          linewidth=1, alpha=0.35 * a))
        if note:
            fig.text(0.5, y0 - len(rows) * dy - 0.005, note, ha="center",
                     color=INK_2, fontsize=26, alpha=clamp01(t * 2.4 - len(rows) * 0.35))
        draw_footer_brand(fig, brand)
    return painter


def chips(question: str, options: list, badge: str, brand: str, q_fs: int = 48):
    def painter(fig, t):
        fig.text(0.5, 0.76, question, ha="center", color=INK, fontsize=q_fs,
                 path_effects=stroke_fx(INK, outline=outline_for(q_fs), fatten=3))
        for i, c in enumerate(options):
            a = clamp01(t * 3.2 - i * 0.7)
            if a <= 0:
                continue
            x = 0.29 + (i % 2) * 0.42
            y = 0.66 - (i // 2) * 0.10
            fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=30, alpha=a,
                     bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                               edgecolor=EMPH, linewidth=2.5, alpha=a))
        fig.text(0.5, 0.49, "▼ コメントで教えて ▼", ha="center", va="center",
                 color=MUTED, fontsize=30, alpha=clamp01(t * 2 - 1.0))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


# ── 株価チャート(ループ㊼) ──────────────────────────────────────────
# ユーザー指摘:「株価のこのタイミングで買って、どのタイミングで売って、
# どのタイミングで買い戻すとか、チャートでわかりやすくして欲しい」
#
# 投資テーマの図は、原則この「株価チャート」を土台にする。
# 横=時間、縦=株価。売買のタイミングはチャート上の点として打つ。
# 抽象的なトークンや棒グラフに置き換えない(視聴者の心的モデルはチャートである)。

def price_path(start: float, end: float, n: int = 56, wiggle: float = 1.0):
    """始点と終点を厳密に固定したまま、途中だけ揺らした株価の道筋。

    数値の根拠になるのは始点と終点だけ(verify.pyで検算する)。
    途中の形はイメージなので、バッジに「イメージ」と明記して使う。
    """
    import math
    pts = []
    span = abs(end - start)
    for i in range(n):
        u = i / (n - 1)
        base = start + (end - start) * u
        w = (math.sin(u * 9.4) * 0.035 + math.sin(u * 21.7) * 0.015) * span * wiggle
        w *= math.sin(math.pi * u)          # 両端では揺れを0にする
        pts.append(base + w)
    return pts


def price_chart(prices, marks, band=None, title="", badge="", brand="",
                ymin=None, ymax=None, unit="万", reveal=1.0):
    """株価チャートのシーン(ループ㊼)。

    prices : 株価の列(左から右へ時間)
    marks  : [(位置0〜1, ラベル, 種類)]。種類は "sell"(売る) / "buy"(買い戻す)
    band   : (価格A, 価格B, ラベル) 2つの価格のあいだを塗り、差額を示す
    reveal : 0〜1。線をどこまで描くか(ユニットごとに伸ばして見せる)

    実際の取引画面と同じ作りにする: 価格の目盛りは左、売買の点はチャート上、
    ラベルには背景を敷いて価格の線と食い合わせない。
    """
    X0, X1 = 0.205, 0.940
    Y0, Y1 = 0.520, 0.790
    lo = ymin if ymin is not None else min(prices)
    hi = ymax if ymax is not None else max(prices)
    pad = (hi - lo) * 0.14 or 1.0
    lo, hi = lo - pad, hi + pad

    def px(u):
        return X0 + (X1 - X0) * u

    def py(v):
        return Y0 + (Y1 - Y0) * (v - lo) / (hi - lo)

    def chip(fig, x, y, text, color, size, ha="center"):
        """線の上に置いても読めるよう、背景を敷いたラベル。"""
        fig.text(x, y, text, ha=ha, va="center", color=color, fontsize=size,
                 bbox=dict(boxstyle="round,pad=0.28", facecolor=SURFACE,
                           edgecolor="none", alpha=0.92), zorder=8)

    def painter(fig, t):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        if title:
            fig.text(0.5, 0.905, title, ha="center", color=INK_2, fontsize=34)
        a_band = clamp01(reveal * 2 - 1)

        # 差額の帯
        if band:
            va_, vb, lab = band
            ya, yb = py(va_), py(vb)
            fig.patches.append(Rectangle((X0, min(ya, yb)), X1 - X0, abs(ya - yb),
                                         transform=fig.transFigure, facecolor=EMPH,
                                         edgecolor="none", alpha=0.15 * a_band, zorder=1))

        # 価格の目盛り(左)と、その水平の点線
        for u, lab, kind in marks:
            idx = int(u * (len(prices) - 1))
            if idx >= max(2, int(len(prices) * clamp01(reveal))):
                continue
            v = prices[idx]
            fig.add_artist(plt.Line2D([X0, X1], [py(v), py(v)], transform=fig.transFigure,
                                      color=MUTED, linewidth=1.4, linestyle=(0, (5, 5)),
                                      alpha=0.6, zorder=2))
            fig.text(X0 - 0.014, py(v), f"{v:,.0f}{unit}", ha="right", va="center",
                     color=INK, fontsize=26,
                     path_effects=stroke_fx(INK, outline=outline_for(26), fatten=1.5))

        # 株価の線
        n = max(2, int(len(prices) * clamp01(reveal)))
        xs = [px(i / (len(prices) - 1)) for i in range(n)]
        ys = [py(v) for v in prices[:n]]
        fig.add_artist(plt.Line2D(xs, ys, transform=fig.transFigure, color=INK,
                                  linewidth=5, solid_capstyle="round", zorder=4))

        # 売買のタイミング(チャート上の点)
        for u, lab, kind in marks:
            idx = int(u * (len(prices) - 1))
            if idx >= n:
                continue
            x, y = px(u), py(prices[idx])
            color = EMPH if kind == "sell" else GOLD
            fig.add_artist(plt.Line2D([x], [y], transform=fig.transFigure, marker="o",
                                      markersize=22, color=color, markeredgecolor=SURFACE,
                                      markeredgewidth=4, linestyle="none", zorder=6))
            right = u <= 0.5
            chip(fig, x + (0.030 if right else -0.030), y + (0.045 if kind == "sell" else -0.045),
                 lab, color, 29, ha="left" if right else "right")

        # 差額のラベル(帯の中央。背景を敷いて線と分離する)
        if band and a_band > 0:
            va_, vb, lab = band
            chip(fig, (X0 + X1) / 2, (py(va_) + py(vb)) / 2, lab, EMPH, 34)

        fig.text(0.075, (Y0 + Y1) / 2, "株\n価", ha="center", va="center",
                 color=MUTED, fontsize=21, linespacing=1.2)
        fig.text((X0 + X1) / 2, Y0 - 0.030, "時間 →", ha="center", va="center",
                 color=MUTED, fontsize=21)
        if badge:
            draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter
