"""再利用シーンビルダー(S010〜のバッチ制作用)。

painter(fig, t) を返すファクトリ群。デザイン規格は shortlib のトークンに従う。
量産型対策(format-variation.md 層C)として、各動画は最低1つ固有シーンを持つこと。
"""
from shortlib import (
    ease_out, ease_in_out, ease_out_back,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD, SERIES_1,
)
import shortlib as S
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
            S.text_fit(fig, 0.5, 0.775, lead, ha="center", va="center", color=INK, fontsize=42,
                     path_effects=stroke_fx(INK, outline=outline_for(42), fatten=2))
        draw_glow_text(fig, 0.5, 0.62, fmt.format(round(v, decimals) if decimals else round(v)),
                       size * max(scale, 0.05))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def hero(main: str, sub: str, badge: str, brand: str, size: int = 108, sub_fs: int = 32):
    def painter(fig, t):
        draw_glow_text(fig, 0.5, 0.62, main, size)
        S.text_fit(fig, 0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=sub_fs, alpha=clamp01(t * 2))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def cover(top: str, main: str, bottom: str, note: str, brand: str, main_size: int = 128):
    def painter(fig, t):
        S.text_fit(fig, 0.5, 0.795, top, ha="center", va="center", color=INK_2,
                 fontsize=44, path_effects=stroke_fx(INK_2, outline=outline_for(44), fatten=1.5))
        draw_glow_text(fig, 0.5, 0.615, main, main_size)
        S.text_fit(fig, 0.5, 0.435, bottom, ha="center", va="center", color=INK,
                 fontsize=42, path_effects=stroke_fx(INK, outline=outline_for(42), fatten=2))
        S.text_fit(fig, 0.5, 0.88, note, ha="center", va="center", color=INK_2, fontsize=28)
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
        S.text_fit(fig, 0.5, 0.90, headline, ha="center", color=INK_2, fontsize=head_fs)
        if ask:
            S.text_fit(fig, 0.5, 0.775, ask, ha="center", color=EMPH, fontsize=31,
                     alpha=clamp01(t * 1.6 - 0.5))
        a = clamp01(t * 2)
        S.text_fit(fig, 0.5, 0.62, main, ha="center", va="center", color=main_color,
                 fontsize=main_size * max(ease_out_back(a), 0.05), alpha=a,
                 path_effects=stroke_fx(main_color, outline=outline_for(main_size), fatten=2.5))
        if sub:
            S.text_fit(fig, 0.5, 0.50, sub, ha="center", va="center",
                     color=sub_color, fontsize=sub_fs, alpha=clamp01(t * 2 - 0.8))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def quiz(headline: str, line1: str, line2: str, note: str, badge: str, brand: str):
    def painter(fig, t):
        S.text_fit(fig, 0.5, 0.88, headline, ha="center", color=INK, fontsize=36,
                 path_effects=stroke_fx(INK, outline=outline_for(36), fatten=2))
        S.text_fit(fig, 0.5, 0.68, line1, ha="center", va="center", color=INK_2, fontsize=38)
        S.text_fit(fig, 0.5, 0.60, line2, ha="center", va="center", color=INK, fontsize=44,
                 path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
        # 注記は立ち絵(y<0.465)より上に置く。「?」は細いので立ち絵の右側に落としてよい
        if note:
            S.text_fit(fig, 0.5, 0.52, note, ha="center", va="center", color=INK_2, fontsize=28)
        a = clamp01(t * 2 - 0.5)
        S.text_fit(fig, 0.5, 0.42, "?", ha="center", va="center", color=EMPH,
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
        S.text_fit(fig, 0.5, 0.565, sub, ha="center", va="center",
                 color=INK_2, fontsize=32, alpha=clamp01(t * 2 - 0.3))
        if formula:
            S.text_fit(fig, 0.5, 0.495, formula, ha="center", va="center",
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
        S.text_fit(fig, 0.5, 0.885, title, ha="center", color=INK, fontsize=40,
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
            S.text_fit(fig, xl, y, n, ha="left", va="center", alpha=a,
                     color=INK if f else INK_2, fontsize=29)
            S.text_fit(fig, xr, y, v, ha="right", va="center", alpha=a,
                     color=EMPH if f else INK, fontsize=40,
                     path_effects=stroke_fx(EMPH if f else INK,
                                            outline=outline_for(40), fatten=2) if f else None)
            if i < len(rows) - 1:
                fig.add_artist(plt.Line2D([xl, xr], [y - dy / 2, y - dy / 2],
                                          transform=fig.transFigure, color=MUTED,
                                          linewidth=1, alpha=0.35 * a))
        if note:
            S.text_fit(fig, 0.5, y0 - len(rows) * dy - 0.005, note, ha="center",
                     color=INK_2, fontsize=26, alpha=clamp01(t * 2.4 - len(rows) * 0.35))
        draw_footer_brand(fig, brand)
    return painter


def chips(question: str, options: list, badge: str, brand: str, q_fs: int = 48):
    def painter(fig, t):
        S.text_fit(fig, 0.5, 0.76, question, ha="center", color=INK, fontsize=q_fs,
                 path_effects=stroke_fx(INK, outline=outline_for(q_fs), fatten=3))
        for i, c in enumerate(options):
            a = clamp01(t * 3.2 - i * 0.7)
            if a <= 0:
                continue
            x = 0.29 + (i % 2) * 0.42
            y = 0.66 - (i // 2) * 0.10
            S.text_fit(fig, x, y, c, ha="center", va="center", color=INK, fontsize=30, alpha=a,
                     bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                               edgecolor=EMPH, linewidth=2.5, alpha=a))
        S.text_fit(fig, 0.5, 0.49, "▼ コメントで教えて ▼", ha="center", va="center",
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

def price_path(start: float, end: float, n: int = 150, vol: float = 0.30, seed: int = 11):
    """本物の値動きに見える株価の道筋(ブラウン橋)。

    正弦波を重ねただけでは滑らかすぎて「偽物のチャート」になる(ユーザー指摘)。
    乱歩を作ってから両端を start/end にぴったり合わせる(ブラウン橋)ことで、
    **始点と終点は厳密に固定したまま、途中は実際の株価のようにギザギザ**になる。
    seed を固定しているので毎回同じ形が出る(検証のたびに絵が変わらない)。
    """
    import random
    rng = random.Random(seed)
    walk, acc = [], 0.0
    for _ in range(n):
        acc += rng.gauss(0, 1)
        walk.append(acc)
    # 両端を0に固定する(ブラウン橋)
    w0, wn = walk[0], walk[-1]
    bridged = [w - (w0 + (wn - w0) * i / (n - 1)) for i, w in enumerate(walk)]
    scale = max(abs(x) for x in bridged) or 1.0
    span = abs(end - start) or abs(start) * 0.25
    amp = span * vol
    return [start + (end - start) * (i / (n - 1)) + bridged[i] / scale * amp
            for i in range(n)]


def price_chart(prices, marks, band=None, title="", badge="", brand="",
                ymin=None, ymax=None, unit="万", reveal=1.0, borrow=None):
    """株価チャートのシーン(ループ㊼)。

    prices : 株価の列(左から右へ時間)
    marks  : [(位置0〜1, ラベル, 種類)]。種類は "sell"(売る) / "buy"(買い戻す)
    band   : (価格A, 価格B, ラベル) 2つの価格のあいだを塗り、差額を示す
    reveal : 0〜1。線をどこまで描くか(ユニットごとに伸ばして見せる)
    borrow : (開始0〜1, 終了0〜1, ラベル) 株を借りている期間をチャートの下に帯で出す。
             空売りの本体は「借りて売る → 買い戻して返す」なので、これがないと図が成立しない

    実際の取引画面と同じ作りにする: 価格の目盛りは左、売買の点はチャート上、
    ラベルには背景を敷いて価格の線と食い合わせない。
    """
    X0, X1 = 0.185, 0.945
    Y0, Y1 = 0.575, 0.795
    Y_BORROW = 0.512          # 「株を借りている期間」の帯
    lo = ymin if ymin is not None else min(prices)
    hi = ymax if ymax is not None else max(prices)
    pad = (hi - lo) * 0.14 or 1.0
    lo, hi = lo - pad, hi + pad

    def px(u):
        return X0 + (X1 - X0) * u

    def py(v):
        return Y0 + (Y1 - Y0) * (v - lo) / (hi - lo)

    # ラベルの当たり判定(図の座標。1080x1920 / 100dpi なので pt→図の割合は下式)
    def _box(x, y, text, size, ha):
        w = len(text) * size / 72 / 10.8 * 1.05 + 0.020
        h = size / 72 / 19.2 + 0.024
        x0 = x - w / 2 if ha == "center" else (x if ha == "left" else x - w)
        return (x0, x0 + w, y - h / 2, y + h / 2)

    def _hit(b, placed):
        return any(b[0] < p[1] and p[0] < b[1] and b[2] < p[3] and p[2] < b[3]
                   for p in placed)

    def painter(fig, t):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle

        # 先に「動かせないもの」を占有させる(見出し・バッジ)。ラベルはここを避ける
        placed = [(0.52, 0.965, 0.800, 0.862)] if badge else []
        if title:
            S.text_fit(fig, 0.5, 0.905, title, ha="center", color=INK_2, fontsize=34)
            placed.append((0.04, 0.96, 0.882, 0.928))

        def chip(x, y, text, color, size, ha="center"):
            """線の上に置いても読めるよう、背景を敷いたラベル。"""
            S.text_fit(fig, x, y, text, ha=ha, va="center", color=color, fontsize=size,
                     bbox=dict(boxstyle="round,pad=0.28", facecolor=SURFACE,
                               edgecolor="none", alpha=0.92), zorder=8)
            placed.append(_box(x, y, text, size, ha))

        def chip_free(cands, text, color, size):
            """候補の位置を順に試し、画面内で他のラベルとぶつからない最初の場所に置く。"""
            ok = [(x, y, ha, _box(x, y, text, size, ha)) for x, y, ha in cands]
            ok = [c for c in ok if c[3][0] > 0.032 and c[3][1] < 0.968]  # 画面外に出さない
            if not ok:
                ok = [(0.5, cands[0][1], "center", _box(0.5, cands[0][1], text, size, "center"))]
            for x, y, ha, b in ok:
                if not _hit(b, placed):
                    chip(x, y, text, color, size, ha)
                    return
            x, y, ha, _ = ok[-1]
            chip(x, y, text, color, size, ha)

        a_band = clamp01(reveal * 2 - 1)

        # 目盛り線(実際のチャート画面と同じく、薄く水平に)
        for k in range(5):
            gy = Y0 + (Y1 - Y0) * k / 4
            fig.add_artist(plt.Line2D([X0, X1], [gy, gy], transform=fig.transFigure,
                                      color=MUTED, linewidth=1, alpha=0.16, zorder=0))
        fig.add_artist(plt.Line2D([X0, X0], [Y0, Y1], transform=fig.transFigure,
                                  color=MUTED, linewidth=1.2, alpha=0.35, zorder=0))

        # 差額の帯
        if band:
            va_, vb, lab = band
            ya, yb = py(va_), py(vb)
            fig.patches.append(Rectangle((X0, min(ya, yb)), X1 - X0, abs(ya - yb),
                                         transform=fig.transFigure, facecolor=EMPH,
                                         edgecolor="none", alpha=0.17 * a_band, zorder=1))
            for gy in (ya, yb):
                fig.add_artist(plt.Line2D([X0, X1], [gy, gy], transform=fig.transFigure,
                                          color=EMPH, linewidth=1.6, alpha=0.55 * a_band,
                                          zorder=2))

        # 価格の目盛り(左)。売買した価格だけを出す
        for u, lab, kind in marks:
            idx = int(u * (len(prices) - 1))
            if idx >= max(2, int(len(prices) * clamp01(reveal))):
                continue
            v = prices[idx]
            S.text_fit(fig, X0 - 0.014, py(v), f"{v:,.0f}{unit}", ha="right", va="center",
                     color=INK_2, fontsize=24)

        # 株価の線
        n = max(2, int(len(prices) * clamp01(reveal)))
        xs = [px(i / (len(prices) - 1)) for i in range(n)]
        ys = [py(v) for v in prices[:n]]
        fig.add_artist(plt.Line2D(xs, ys, transform=fig.transFigure, color=INK,
                                  linewidth=5, solid_capstyle="round",
                                  solid_joinstyle="round", zorder=4))

        # 差額のラベル(この図の主役なので、先に場所を取る)
        if band and a_band > 0:
            va_, vb, lab = band
            ymid = (py(va_) + py(vb)) / 2
            chip_free([(0.52, ymid, "center"), (0.34, ymid, "center"),
                       (0.72, ymid, "center"), (0.52, ymid + 0.045, "center"),
                       (0.52, ymid - 0.045, "center")], lab, EMPH, 34)

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
            dx, ha = (0.030, "left") if right else (-0.030, "right")
            up = 0.052 if kind == "sell" else -0.052
            cands = [(x + dx, y + d, ha) for d in (up, -up, up * 1.9, -up * 1.9)]
            cands += [(x - dx, y + d, "right" if right else "left") for d in (up, -up)]
            # 最後の逃げ場: グラフの上下(枠の外)。ここなら線とも帯とも重ならない
            cands += [(x + dx, Y0 - 0.020, ha), (x + dx, Y1 + 0.022, ha)]
            cands = [(cx, min(max(cy, Y0 - 0.020), 0.796), ch) for cx, cy, ch in cands]
            chip_free(cands, lab, color, 29)

        # 株を借りている期間(空売りの本体)。売った瞬間に借り、買い戻した瞬間に返す
        if borrow:
            bu0, bu1, blab = borrow
            n_ratio = clamp01(reveal)
            bx0, bx1 = px(bu0), px(min(bu1, n_ratio))
            if bx1 > bx0:
                a_b = clamp01(reveal * 3 - bu0 * 3)
                fig.patches.append(Rectangle((bx0, Y_BORROW - 0.014), bx1 - bx0, 0.028,
                                             transform=fig.transFigure, facecolor=GOLD,
                                             edgecolor="none", alpha=0.45 * a_b, zorder=3))
                # 両端の縦棒(いつ借りて、いつ返したか)
                for bx in ((bx0,) if n_ratio < bu1 else (bx0, bx1)):
                    fig.add_artist(plt.Line2D([bx, bx], [Y_BORROW - 0.028, Y_BORROW + 0.028],
                                              transform=fig.transFigure, color=GOLD,
                                              linewidth=4, alpha=a_b, zorder=4))
                if bx1 - bx0 > 0.30:      # 帯が十分に伸びてからラベルを出す
                    S.text_fit(fig, (bx0 + bx1) / 2, Y_BORROW, blab, ha="center", va="center",
                             color=INK, fontsize=23, alpha=a_b, zorder=5)
            S.text_fit(fig, X0 - 0.014, Y_BORROW, "株", ha="right", va="center",
                     color=INK_2, fontsize=22)
        if badge:
            draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


# ─────────────────────────────────────────────────────────────
# 図の型を足す(ループ㊿)。figure-forms.md の判定表に対応させる。
#   bars2   ... 「AとBの量が違う」/「前→後で変わった」→ 共通の底からの棒2本(+差の帯)
#   lines2  ... 「2つが時間でどう離れるか」→ 同じ軸に2本の折れ線(直接ラベル)
#   stack   ... 「積み上がっている」→ 同じ単位のブロックを積んで、総額に届かせる
# いずれも意味を担うのは長さ・位置であって、箱の中の文ではない。
# ─────────────────────────────────────────────────────────────

def bars2(title, left, right, badge, brand, gap=None, unit="", ymax=None):
    """共通の底からの棒2本。left/right = (見出し, 値, 棒の中に書く短い語句)。

    gap : (ラベル,) を渡すと、2本の差を右側に帯と数字で出す
    長さが意味を持つので、値そのものを軸のスケールにする(棒の高さ=値/ymax)。
    """
    Y0 = 0.545
    HMAX = 0.215
    top = ymax if ymax else max(left[1], right[1]) * 1.05

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        if title:
            S.text_fit(fig, 0.5, 0.905, title, ha="center", color=INK_2, fontsize=34)
        fig.add_artist(plt.Line2D([0.10, 0.90], [Y0, Y0], transform=fig.transFigure,
                                  color=MUTED, linewidth=1.5, alpha=0.5))
        cols = [(0.30, left, MUTED_BAR, clamp01(t * 2.2)),
                (0.66, right, EMPH, clamp01(t * 2.2 - 0.6))]
        tops = {}
        for x, (head, val, inner), color, a in cols:
            if a <= 0:
                continue
            h = HMAX * (val / top) * a
            fig.patches.append(Rectangle((x - 0.13, Y0), 0.26, h, transform=fig.transFigure,
                                         facecolor=color, edgecolor="none", alpha=0.95))
            tops[x] = Y0 + h
            S.text_fit(fig, x, Y0 + h + 0.032, inner, ha="center", va="center", color=INK,
                     fontsize=32, alpha=a,
                     path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
            S.text_fit(fig, x, Y0 - 0.030, head, ha="center", va="center", color=INK_2,
                     fontsize=28, alpha=a)
        if gap and len(tops) == 2 and clamp01(t * 2.2 - 1.2) > 0:
            a = clamp01(t * 2.2 - 1.2)
            y1, y2 = tops[0.30], tops[0.66]
            fig.patches.append(Rectangle((0.838, min(y1, y2)), 0.050, abs(y2 - y1),
                                         transform=fig.transFigure, facecolor=GOLD,
                                         edgecolor="none", alpha=0.55 * a))
            S.text_fit(fig, 0.863, (y1 + y2) / 2, gap, ha="center", va="center", color=INK,
                     fontsize=27, alpha=a, rotation=90,
                     path_effects=stroke_fx(INK, outline=outline_for(27), fatten=1.5))
        if badge:
            draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def lines2(title, series, badge, brand, ymin=None, ymax=None, xlabels=None, reveal=1.0):
    """同じ軸に2本の折れ線。series = [(名前, [値...], 色), ...]。

    2系列なので凡例は使わず、線の右端に直接ラベルを置く(空間的近接)。
    横位置=時間、縦位置=値。どちらが上か・どこで離れるかが形で分かる。
    """
    X0, X1 = 0.175, 0.760      # 右端はラベルの場所として空ける
    Y0, Y1 = 0.560, 0.800
    vals = [v for _, ys, _ in series for v in ys]
    lo = ymin if ymin is not None else min(vals)
    hi = ymax if ymax is not None else max(vals)
    pad = (hi - lo) * 0.16 or 1.0
    lo, hi = lo - pad, hi + pad

    def painter(fig, t):
        if title:
            S.text_fit(fig, 0.5, 0.905, title, ha="center", color=INK_2, fontsize=34)
        for k in range(5):
            gy = Y0 + (Y1 - Y0) * k / 4
            fig.add_artist(plt.Line2D([X0, X1], [gy, gy], transform=fig.transFigure,
                                      color=MUTED, linewidth=1, alpha=0.16, zorder=0))
        n_pt = len(series[0][1])
        shown = max(2, int(round(n_pt * clamp01(reveal))))
        # 右端のラベルが近すぎると読めないので、上下に押し分ける(空間的近接は保つ)
        ends = [Y0 + (Y1 - Y0) * (ys[shown - 1] - lo) / (hi - lo) for _, ys, _ in series]
        if len(ends) == 2 and abs(ends[0] - ends[1]) < 0.040:
            mid = sum(ends) / 2
            hi_i = 0 if ends[0] >= ends[1] else 1
            ends[hi_i], ends[1 - hi_i] = mid + 0.020, mid - 0.020
        for i, (name, ys, color) in enumerate(series):
            xs = [X0 + (X1 - X0) * (j / (n_pt - 1)) for j in range(shown)]
            py = [Y0 + (Y1 - Y0) * (v - lo) / (hi - lo) for v in ys[:shown]]
            fig.add_artist(plt.Line2D(xs, py, transform=fig.transFigure, color=color,
                                      linewidth=6, solid_capstyle="round", zorder=4 + i))
            fig.add_artist(plt.Line2D([xs[-1]], [py[-1]], transform=fig.transFigure, marker="o",
                                      markersize=18, color=color, markeredgecolor=SURFACE,
                                      markeredgewidth=4, linestyle="none", zorder=6))
            S.text_fit(fig, X1 + 0.022, ends[i], name, ha="left", va="center", color=color,
                     fontsize=29, zorder=8,
                     path_effects=stroke_fx(color, outline=outline_for(29), fatten=1.5))
        for j, lab in enumerate(xlabels or []):
            if j < shown:
                S.text_fit(fig, X0 + (X1 - X0) * (j / (n_pt - 1)), Y0 - 0.032, lab,
                         ha="center", va="center", color=INK_2, fontsize=25)
        if badge:
            draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def stack(title, n_blocks, block_label, total_label, badge, brand, cols=5, focus=None):
    """同じ大きさのブロックを積んで、総額に届かせる図(PERなど「○年分」)。

    1個=1年分。個数そのものが意味を持つので、数えられる大きさにする。
    """
    def painter(fig, t):
        from matplotlib.patches import Rectangle
        if title:
            S.text_fit(fig, 0.5, 0.905, title, ha="center", color=INK_2, fontsize=34)
        rows = (n_blocks + cols - 1) // cols
        # 行が増えても立ち絵(y<0.465)に届かないよう、間隔を行数に合わせて詰める
        pitch = min(0.065, 0.270 / max(rows, 1))
        bw, bh = 0.115, pitch * 0.74
        gx, gy = 0.020, pitch * 0.26
        total_w = cols * bw + (cols - 1) * gx
        x0 = 0.5 - total_w / 2
        y_top = 0.790
        shown = int(round(n_blocks * clamp01(t * 1.8)))
        for i in range(shown):
            r, c = divmod(i, cols)
            x = x0 + c * (bw + gx)
            y = y_top - r * (bh + gy) - bh
            on = focus is None or i < focus
            fig.patches.append(Rectangle((x, y), bw, bh, transform=fig.transFigure,
                                         facecolor=EMPH if on else MUTED_BAR,
                                         edgecolor="none", alpha=0.95))
        y_bottom = y_top - rows * (bh + gy)
        if block_label:
            S.text_fit(fig, 0.5, y_bottom - 0.012, block_label, ha="center", va="top",
                     color=INK_2, fontsize=27)
        if total_label:
            S.text_fit(fig, x0, 0.866, total_label, ha="left", va="center", color=INK,
                     fontsize=32, path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
        if badge:
            draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter
