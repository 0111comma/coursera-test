#!/usr/bin/env python3
"""横型(1920×1080)長尺用のシーン部品。

縦型の `scenes_common.py` と役割は同じだが、**置ける図がちがう**。
縦型は横幅1080pxしかないので棒は2本が限界だったが、
横型は1920pxあるので**6本並ぶ**し、30年ぶんの折れ線に目盛りが打てる。
その差がそのまま「長尺でやる理由」なので、ここには横型でしか描けない型を置く。

使う側は render.py の先頭で:
    import shortlib as S
    S.use_landscape()          # ← new_canvas より前に1回だけ
    import scenes_long as sl

レイアウトの約束(1920×1080):
    y 0.88〜0.96  章見出し・タイトル
    y 0.30〜0.84  図の本体
    y 0.20〜0.59  立ち絵(x 0.798〜0.990)。**図は x<0.78 に収める**
    y 0.08〜0.19  字幕
    y 0.036       チャンネル名
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

import shortlib as S
from shortlib import (
    INK, INK_2, MUTED, MUTED_BAR, GRID, BASELINE, EMPH, GOLD, SURFACE,
    draw_badge, draw_footer_brand, stroke_fx, outline_for, draw_rich_text,
)

# 図が使ってよい横幅。右端は立ち絵に譲る
PLOT_L, PLOT_R = 0.055, 0.775
TITLE_Y = 0.925


def clamp01(x):
    return max(0.0, min(1.0, x))


def _frame(fig, title, badge, brand):
    if title:
        S.text_fit(fig, (PLOT_L + PLOT_R) / 2, TITLE_Y, title, ha="center",
                 color=INK_2, fontsize=30)
    if badge:
        draw_badge(fig, badge)
    draw_footer_brand(fig, brand)


# ---------------------------------------------------------------- 文字もの

def chapter(no: int, title: str, question: str, badge: str, brand: str, total: int = 0):
    """章の入口カード。「第N章」+ 短いラベル。

    **その章が答える問いは、画面ではなくナレーションが言う。**
    最初は問いも画面に書いていたが、ナレーションと一字一句同じになり、
    Mayerの冗長性(図の中の文がナレーションと同義だと学習を妨げる)にそのまま当たった。
    かといって問いをナレーションから外すと、耳だけで追っている人に章の切れ目が
    伝わらない(W5 ラジオテスト)。**だから声が問いを言い、画面は道標だけを出す。**

    question は概要欄のチャプター行に使う値として受け取り、描画には使わない。
    title は道標なので短く(9文字以内)。長い章題は問いの言い換えであることが多い。
    """
    def painter(fig, t):
        a = clamp01(t * 2.2)
        # total を渡すと「第N章 / 全M章」になる。どこまで来たかを画面に出す
        # (合図の原則。09/07-progress.md)。分数だけなので短い語句のまま
        head = f"第{no}章 / 全{total}章" if total else f"第{no}章"
        S.text_fit(fig, (PLOT_L + PLOT_R) / 2, 0.680, head, ha="center", va="center",
                 color=EMPH, fontsize=40, alpha=a)
        draw_rich_text(fig, (PLOT_L + PLOT_R) / 2, 0.500, title, 92 * (1 + 0.04 * (1 - a)),
                       wrap=12, line_h=0.090, block_fit=0.60)
        _frame(fig, "", badge, brand)
    return painter


def hero(main: str, sub: str, badge: str, brand: str, size: int = 96, sub_fs: int = 36):
    """大きい1行 + 補足。冒頭と締めに使う。"""
    def painter(fig, t):
        a = clamp01(t * 2.2)
        draw_rich_text(fig, (PLOT_L + PLOT_R) / 2, 0.620, main, size * (1 + 0.05 * (1 - a)),
                       wrap=14, line_h=0.085, block_fit=0.68)
        if sub:
            S.text_fit(fig, (PLOT_L + PLOT_R) / 2, 0.440, sub, ha="center", va="center",
                     color=INK_2, fontsize=sub_fs, alpha=clamp01(t * 2 - 0.4))
        _frame(fig, "", badge, brand)
    return painter


def cover(top: str, main: str, bottom: str, note: str, brand: str, main_size: int = 190):
    """サムネ兼、冒頭の静止フレーム。数字を1つだけ大きく(longform-design §5)。"""
    def painter(fig, t):
        S.text_fit(fig, 0.5, 0.855, top, ha="center", va="center", color=INK_2, fontsize=44)
        draw_rich_text(fig, 0.5, 0.560, main, main_size, wrap=10, line_h=0.13, block_fit=0.86)
        # max_w は既定の0.92ではなく0.48。2026-08-22にサムネを実測したところ、
        # この金の行が**左右の立ち絵を突き抜けていた**(文字は幅の10.6%〜89.4%を使い、
        # 立ち絵の空き帯は25.5%〜77.3%しかなかった)。両端が読めず、事故に見える。
        # 画面幅ではなく**立ち絵のあいだ**に収まるまで縮める。
        S.text_fit(fig, 0.5, 0.320, bottom, ha="center", va="center", color=EMPH, fontsize=54,
                 max_w=0.48,
                 path_effects=stroke_fx(EMPH, outline=outline_for(54), fatten=2.5))
        # 字幕帯(上端 SUBTITLE_Y + 行分)より上に置く。カバーは字幕を出さないが、
        # 同じ位置に注記を置くと通常フレームと視線の置き場がずれる
        S.text_fit(fig, 0.5, 0.225, note, ha="center", va="center", color=MUTED, fontsize=30)
        draw_footer_brand(fig, brand)
    return painter


def card(headline: str, main: str, sub: str, badge: str, brand: str,
         main_size: int = 76, head_fs: int = 32, ask: str = ""):
    """見出し + 主役語 + 補足。"""
    def painter(fig, t):
        a = clamp01(t * 2.4)
        S.text_fit(fig, (PLOT_L + PLOT_R) / 2, 0.780, headline, ha="center", va="center",
                 color=INK_2, fontsize=head_fs)
        draw_rich_text(fig, (PLOT_L + PLOT_R) / 2, 0.590, main,
                       main_size * (1 + 0.06 * (1 - a)), wrap=14, line_h=0.085, block_fit=0.66)
        if sub:
            S.text_fit(fig, (PLOT_L + PLOT_R) / 2, 0.410, sub, ha="center", va="center",
                     color=MUTED, fontsize=28, alpha=clamp01(t * 2 - 0.5))
        if ask:
            S.text_fit(fig, (PLOT_L + PLOT_R) / 2, 0.320, ask, ha="center", va="center",
                     color=EMPH, fontsize=30, alpha=clamp01(t * 2 - 0.8))
        _frame(fig, "", badge, brand)
    return painter


# ---------------------------------------------------------------- 棒

def barsN(title, items, badge, brand, ymax=None, unit="", highlight=None):
    """**横型の主役**: 共通の底からの棒を最大6本。

    items = [(見出し, 値, 棒の上に書く語句), ...]
    縦型(scenes_common.bars2)では2本が限界だった。ここが横型の一番の得。
    highlight: 強調する棒の添字(その1本だけEMPH。合図は1点に絞る=Mayer)
    """
    Y0 = 0.330
    HMAX = 0.430
    top = ymax if ymax else max(v for _, v, _ in items) * 1.12
    n = len(items)
    span = PLOT_R - PLOT_L
    slot = span / n
    bw = min(0.115, slot * 0.62)

    def painter(fig, t):
        fig.add_artist(plt.Line2D([PLOT_L, PLOT_R], [Y0, Y0], transform=fig.transFigure,
                                  color=MUTED, linewidth=1.5, alpha=0.5))
        for k, (head, val, inner) in enumerate(items):
            a = clamp01(t * 2.4 - k * 0.28)
            if a <= 0:
                continue
            x = PLOT_L + slot * (k + 0.5)
            color = EMPH if (highlight is None or highlight == k) else MUTED_BAR
            h = HMAX * (val / top) * a
            fig.patches.append(Rectangle((x - bw / 2, Y0), bw, h, transform=fig.transFigure,
                                         facecolor=color, edgecolor="none", alpha=0.95))
            S.text_fit(fig, x, Y0 + h + 0.036, inner, ha="center", va="center", color=INK,
                     fontsize=30, alpha=a,
                     path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.8))
            S.text_fit(fig, x, Y0 - 0.042, head, ha="center", va="center", color=INK_2,
                     fontsize=25, alpha=a)
        if unit:
            S.text_fit(fig, PLOT_L, Y0 + HMAX + 0.030, unit, ha="left", va="center",
                     color=MUTED, fontsize=22)
        _frame(fig, title, badge, brand)
    return painter


def compare2(title, left, right, badge, brand, note_l="", note_r=""):
    """左右2列の比較(「もし〜だったら」と「実際は」)。

    left/right = (見出し, [(ラベル, 値, 色), ...], 合計ラベル)
    積み上げではなく**同じ土俵の2列**。列ごとに枠を引いて、比べる相手を明示する。
    """
    Y0, HMAX = 0.330, 0.400
    allv = [v for _, items, _ in (left, right) for _, v, _ in items]
    top = max(allv) * 1.15 if allv else 1
    cx = {0: PLOT_L + (PLOT_R - PLOT_L) * 0.27, 1: PLOT_L + (PLOT_R - PLOT_L) * 0.73}

    def painter(fig, t):
        for col, (head, items, total) in enumerate((left, right)):
            a = clamp01(t * 2.2 - col * 0.45)
            if a <= 0:
                continue
            x = cx[col]
            fig.patches.append(Rectangle((x - 0.165, Y0 - 0.075), 0.330, HMAX + 0.160,
                                         transform=fig.transFigure, facecolor="none",
                                         edgecolor=BASELINE, linewidth=1.5, alpha=a))
            S.text_fit(fig, x, Y0 + HMAX + 0.062, head, ha="center", va="center",
                     color=INK_2, fontsize=28, alpha=a)
            m = len(items)
            for k, (label, val, color) in enumerate(items):
                bx = x - 0.075 * (m - 1) + 0.150 * k / max(1, m - 1) if m > 1 else x
                h = HMAX * (val / top) * a
                fig.patches.append(Rectangle((bx - 0.055, Y0), 0.110, h,
                                             transform=fig.transFigure,
                                             facecolor=color, edgecolor="none", alpha=0.95))
                S.text_fit(fig, bx, Y0 + h + 0.030, label, ha="center", va="center",
                         color=INK, fontsize=26, alpha=a,
                         path_effects=stroke_fx(INK, outline=outline_for(26), fatten=1.6))
            S.text_fit(fig, x, Y0 - 0.048, total, ha="center", va="center", color=EMPH,
                     fontsize=34, alpha=clamp01(t * 2 - 0.6 - col * 0.4),
                     path_effects=stroke_fx(EMPH, outline=outline_for(34), fatten=2))
        # 注記は枠の外に出す(枠の下端は Y0-0.075 = 0.255)
        if note_l:
            S.text_fit(fig, cx[0], 0.212, note_l, ha="center", va="center", color=MUTED, fontsize=24)
        if note_r:
            S.text_fit(fig, cx[1], 0.212, note_r, ha="center", va="center", color=MUTED, fontsize=24)
        _frame(fig, title, badge, brand)
    return painter


def band(title, total_label, part_ratio, part_label, rest_label, badge, brand,
         show_rest=False, big=""):
    """1本の帯を塗り分ける(全体と部分)。S012 で使った形の横型版。

    棒を2本並べると「別々の額」に見える。同じ額の内訳は帯1本で見せる。
    """
    X0, X1 = PLOT_L, PLOT_R
    Y, H = 0.480, 0.110
    xm = X0 + (X1 - X0) * part_ratio

    def painter(fig, t):
        a = clamp01(t * 2.4)
        fig.patches.append(Rectangle((X0, Y), X1 - X0, H, transform=fig.transFigure,
                                     facecolor=MUTED_BAR, edgecolor="none", alpha=0.55))
        S.text_fit(fig, (X0 + X1) / 2, Y + H + 0.046, total_label, ha="center", va="center",
                 color=INK_2, fontsize=30)
        fig.patches.append(Rectangle((X0, Y), (xm - X0) * a, H, transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none", alpha=0.95))
        if a > 0.5:
            S.text_fit(fig, (X0 + xm) / 2, Y + H / 2, part_label, ha="center", va="center",
                     color=SURFACE, fontsize=32, fontweight="black")
        if show_rest:
            b = clamp01(t * 2.2 - 0.3)
            fig.patches.append(Rectangle((xm, Y), X1 - xm, H, transform=fig.transFigure,
                                         facecolor=EMPH, edgecolor="none", alpha=0.95 * b))
            S.text_fit(fig, (xm + X1) / 2, Y - 0.050, rest_label, ha="center", va="center",
                     color=EMPH, fontsize=30, alpha=b,
                     path_effects=stroke_fx(EMPH, outline=outline_for(30), fatten=2))
        if big:
            S.text_fit(fig, (X0 + X1) / 2, 0.720, big, ha="center", va="center", color=INK,
                     fontsize=56, alpha=clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(INK, outline=outline_for(56), fatten=2.6))
        _frame(fig, title, badge, brand)
    return painter


# ---------------------------------------------------------------- 線

def curve(title, xs, ys, badge, brand, xlabel="", ylabel="", reveal=1.0,
          hline=None, hline_label="", marks=(), ymin=None, ymax=None, yfmt="{:.2f}"):
    """折れ線1本(+水平線)。**横幅があるので目盛りが打てる**のが横型の得。

    marks = [(x, y, ラベル), ...] を渡すと、その点に丸と直接ラベルを置く。
    凡例は使わない(空間的近接。線の近くに直接書く)。
    """
    def painter(fig, t):
        # y軸ラベルぶん左を空ける(PLOT_L のままだと画面外に出る)
        ax = fig.add_axes([PLOT_L + 0.055, 0.300, PLOT_R - PLOT_L - 0.055, 0.520])
        ax.set_facecolor("none")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(BASELINE)
            ax.spines[s].set_linewidth(1.5)
        ax.tick_params(colors=MUTED, labelsize=22, length=0)
        ax.grid(axis="y", color=GRID, linewidth=1.2)
        ax.set_axisbelow(True)
        k = max(2, int(len(xs) * clamp01(t / max(reveal, 1e-6))))
        ax.plot(xs[:k], ys[:k], color=EMPH, linewidth=4.0, solid_capstyle="round")
        if hline is not None:
            ax.axhline(hline, color=MUTED_BAR, linewidth=2.5, linestyle=(0, (6, 5)))
            if hline_label:
                # 右端に置くと立ち絵に潜るので、線の上・左寄せで直接ラベルする
                ax.annotate(hline_label, (min(xs), hline), textcoords="offset points",
                            xytext=(6, 12), ha="left", va="bottom", color=INK_2, fontsize=24)
        for mx, my, label in marks:
            if mx <= xs[min(k, len(xs)) - 1]:
                ax.plot([mx], [my], "o", color=INK, markersize=11, zorder=5)
                ax.annotate(label, (mx, my), textcoords="offset points", xytext=(0, 22),
                            ha="center", color=INK, fontsize=27,
                            path_effects=stroke_fx(INK, outline=outline_for(27), fatten=1.8))
        ax.set_xlim(min(xs), max(xs))
        if ymin is not None or ymax is not None:
            ax.set_ylim(ymin, ymax)
        if xlabel:
            ax.set_xlabel(xlabel, color=MUTED, fontsize=24, labelpad=10)
        if ylabel:
            ax.set_ylabel(ylabel, color=MUTED, fontsize=24, labelpad=10)
        # **目盛の値そのものを整数に固定する。** yfmt="{:.0f}" だけだと、matplotlib が
        # 2.5 / 7.5 / 12.5 に格子線を引き、Python の偶数丸めで「2」「8」「12」と表示する。
        # 格子線の位置と数字が食い違い、視聴者がグラフから値を読むと直接まちがえる
        # (2026-08-22に発覚。L002は「自分の返済年数を当てて何%まで耐えられるか読む」動画)
        if yfmt.endswith(".0f}"):
            from matplotlib.ticker import MaxNLocator
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(lambda v, _: yfmt.format(v))
        _frame(fig, title, badge, brand)
    return painter


def timeline(title, years, badge, brand, arrow=None, note=""):
    """年をまたぐ話(繰越控除など)。年ごとの箱を横に並べ、矢印を架ける。

    years = [(年のラベル, 中身の文字列, 値の文字列, 強調するか), ...]
    """
    n = len(years)
    span = PLOT_R - PLOT_L
    bw = span / n * 0.78
    Y, H = 0.430, 0.230

    def painter(fig, t):
        for k, (ylab, body, val, emph) in enumerate(years):
            a = clamp01(t * 2.2 - k * 0.5)
            if a <= 0:
                continue
            x = PLOT_L + span * (k + 0.5) / n
            fig.patches.append(Rectangle((x - bw / 2, Y), bw, H, transform=fig.transFigure,
                                         facecolor=SURFACE, edgecolor=EMPH if emph else BASELINE,
                                         linewidth=2.0, alpha=a))
            S.text_fit(fig, x, Y + H + 0.040, ylab, ha="center", va="center",
                     color=INK_2, fontsize=30, alpha=a)
            S.text_fit(fig, x, Y + H * 0.62, body, ha="center", va="center",
                     color=INK, fontsize=30, alpha=a)
            S.text_fit(fig, x, Y + H * 0.26, val, ha="center", va="center",
                     color=EMPH if emph else INK_2, fontsize=36, alpha=a,
                     path_effects=stroke_fx(EMPH if emph else INK_2,
                                            outline=outline_for(36), fatten=2))
        if arrow is not None and clamp01(t * 2 - 1.0) > 0:
            a, b = arrow
            xa = PLOT_L + span * (a + 0.5) / n
            xb = PLOT_L + span * (b + 0.5) / n
            # 箱の下をくぐらせる(箱の中を通ると金額に重なる)
            fig.patches.append(FancyArrowPatch(
                (xa, Y - 0.022), (xb, Y - 0.022), transform=fig.transFigure,
                connectionstyle="arc3,rad=0.42", arrowstyle="-|>,head_width=6,head_length=10",
                color=EMPH, linewidth=3.0, alpha=clamp01(t * 2 - 1.0)))
        if note:
            S.text_fit(fig, (PLOT_L + PLOT_R) / 2, 0.232, note, ha="center", va="center",
                     color=MUTED, fontsize=26)
        _frame(fig, title, badge, brand)
    return painter


def checklist(title, items, badge, brand, lit=0):
    """箇条を「点灯するチェックリスト」として見せる(S014の herasu の横型版)。

    items = [短い見出し, ...]。lit までが点灯し、残りは沈む。
    ただの箇条書きは「箱に入った文章」にすぎない(Larkin & Simon)。
    **いま何番目の話をしているか**が位置で分かることに意味を持たせる。
    """
    n = len(items)
    H = 0.088
    top = 0.780

    def painter(fig, t):
        for k, label in enumerate(items):
            on = k < lit
            a = clamp01(t * 2.4 - k * 0.15) if on else 0.30
            y = top - H * k
            fig.patches.append(Rectangle((PLOT_L, y - H * 0.38), PLOT_R - PLOT_L, H * 0.76,
                                         transform=fig.transFigure,
                                         facecolor=EMPH if (on and k == lit - 1) else "none",
                                         edgecolor=(EMPH if (on and k == lit - 1)
                                                    else BASELINE),
                                         linewidth=1.6, alpha=(0.16 if (on and k == lit - 1)
                                                               else 0.9) * a))
            cur = on and k == lit - 1        # いま話している行だけを強調する
            S.text_fit(fig, PLOT_L + 0.035, y, f"{k + 1}", ha="center", va="center",
                     color=EMPH if cur else (INK_2 if on else MUTED), fontsize=32, alpha=a)
            S.text_fit(fig, PLOT_L + 0.075, y, label, ha="left", va="center",
                     color=INK if on else MUTED, fontsize=34, alpha=a)
        _frame(fig, title, badge, brand)
    return painter


# ---------------------------------------------------------------- 表

def table(title, headers, rows, badge, brand, highlight=None, reveal_rows=True):
    """締めの1枚。行=場合、列=数字。**横型でしか読める大きさにならない**。

    rows = [(セル, セル, ...), ...]。highlight は強調する行の添字。
    """
    n = len(rows)
    ncol = len(headers)
    ROW_H = 0.086
    # 行数に合わせて上下中央に寄せる(3行の表が画面の上半分に貼りつくのを避ける)
    Y_TOP = min(0.800, 0.520 + ROW_H * n / 2)
    NUM_FS = 34 if ncol <= 3 else 30
    colw = (PLOT_R - PLOT_L) / ncol
    # 1列目(場合の名前)は広く、数字の列は狭く
    ws = [colw * 1.5] + [(PLOT_R - PLOT_L - colw * 1.5) / (ncol - 1)] * (ncol - 1) \
        if ncol > 1 else [PLOT_R - PLOT_L]
    xs = []
    acc = PLOT_L
    for w in ws:
        xs.append(acc + w / 2)
        acc += w

    def painter(fig, t):
        for c, h in enumerate(headers):
            S.text_fit(fig, xs[c], Y_TOP + 0.048, h, ha="center", va="center",
                     color=MUTED, fontsize=26)
        fig.add_artist(plt.Line2D([PLOT_L, PLOT_R], [Y_TOP + 0.014] * 2,
                                  transform=fig.transFigure, color=BASELINE, linewidth=1.5))
        for r, row in enumerate(rows):
            a = clamp01(t * 2.2 - r * 0.35) if reveal_rows else 1.0
            if a <= 0:
                continue
            y = Y_TOP - ROW_H * (r + 0.5)
            if highlight == r:
                fig.patches.append(Rectangle((PLOT_L, y - ROW_H * 0.44),
                                             PLOT_R - PLOT_L, ROW_H * 0.88,
                                             transform=fig.transFigure, facecolor=EMPH,
                                             edgecolor="none", alpha=0.14 * a))
            for c, cell in enumerate(row):
                color = EMPH if (highlight == r and c > 0) else INK
                S.text_fit(fig, xs[c], y, str(cell), ha="center", va="center", color=color,
                         fontsize=30 if c == 0 else NUM_FS, alpha=a,
                         fontweight="black" if c > 0 else "normal")
            fig.add_artist(plt.Line2D([PLOT_L, PLOT_R], [y - ROW_H / 2] * 2,
                                      transform=fig.transFigure, color=GRID,
                                      linewidth=1.0, alpha=a))
        _frame(fig, title, badge, brand)
    return painter


# ---------------------------------------------------------------- チャプター

def chapter_lines(unit_secs, marks):
    """概要欄に貼るチャプター行を作る。

    unit_secs: render_video の返り値 result["unit_secs"]
    marks: [(ユニットの添字, 章題), ...]  ※添字0は必ず 0:00 になる
    """
    out, acc, table_ = [], 0.0, {i: title for i, title in marks}
    for i, sec in enumerate(unit_secs):
        if i in table_:
            m, s = divmod(int(acc), 60)
            out.append(f"{m}:{s:02d} {table_[i]}")
        acc += sec
    return out
