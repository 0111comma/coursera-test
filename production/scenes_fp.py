#!/usr/bin/env python3
"""新デザインの場面部品(縦型ショート用)。

競合の分解(competitor-shorts-teardown-2026-08-23.md)から:
- **1カット1.6〜1.8秒**。絵は頻繁に差し替える
- 図(表)は出しっぱなしにしてよいが、**そのあいだ赤枠を1行ずつ動かす**
- 数字はその語だけ色を変える(【】で囲む)

2026-08-29 批評ループ(6人×70指摘)での全面改修:
- 赤は RED(#b32020)の1系統に統一。#e03131 は全廃(matplotlibデフォルト感)
- 白いカードは card() 経由で描く: 同一の角丸 + 薄いドロップシャドウ + CARD色
- カードの座標は CARD_L/R/TOP/BOT に固定。連続カットでパネルが跳ねない
- 数字は big_number() 経由: 第2書体の極太 + 単位は62% + カウントアップ
- 画面に出る金額は必ず F.fmt_disp()(桁区切り)を通す
- t を無視する部品を無くす(イージングは F.ease_out / F.ease_back を使う)
"""
import math
import re

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch
import matplotlib.patheffects as path_effects

import fplib as F
import shortlib as S

# ---- 配色(ブランドの1セットに集約。ここ以外で色を直書きしない)
RED = "#b32020"            # ブランドの赤(文字・線・枠)。#e03131 は全廃
RED_FILL = "#c0392b"       # 棒など「面」の赤(文字の赤より一段明るく)
RED_SOFT = "#fbeae6"       # ハイライト行の地
INK = F.INK_DARK
SUB = "#6b6459"            # 副テキスト(暖色グレー)
WARM_GRAY = "#b9ae99"      # 非強調の図形の面。青みグレー(#9aa0a6等)は全廃
CARD = F.CARD              # カードの白(#fffdf7)。純白は文字専用
CARD_EDGE = "#e0d3ba"
CARD_EDGE_STRONG = "#8f8574"   # 背景に沈みやすい左側カード等の縁
GREEN = "#5e8c3f"          # 肯定・充足(暖色寄りのブランド緑)
SHADOW = "#d9c9a8"         # カードの落ち影

# ---- カードの固定寸法。**連続カットでパネル枠を動かさない**
CARD_L, CARD_R = 0.06, 0.94
CARD_TOP, CARD_BOT = 0.72, 0.44
TITLE_Y = 0.825            # 図の小見出しの高さ(注記バーとの空帯を詰めた)

_ease = F.ease_out
_back = F.ease_back


def _halo(fs: float, color=INK):
    """ドット地に直置きする小さめの字の、薄い白フチ。"""
    return [path_effects.Stroke(linewidth=fs * 0.12, foreground="#fffdf7"),
            path_effects.Normal()]


def card(fig, x, y, w, h, face=CARD, edge=CARD_EDGE, lw=3.0, r=0.028,
         z=2.2, sc=1.0, alpha=1.0):
    """白カード+落ち影。**全部品のカードはここから描く**(仕上げを揃える)。"""
    if sc != 1.0:
        cx, cy = x + w / 2, y + h / 2
        x, y, w, h = cx - w * sc / 2, cy - h * sc / 2, w * sc, h * sc
    style = f"round,pad=0,rounding_size={r}"
    fig.add_artist(FancyBboxPatch((x + 0.004, y - 0.006), w, h, boxstyle=style,
                                  transform=fig.transFigure, facecolor=SHADOW,
                                  alpha=0.55 * alpha, edgecolor="none", zorder=z - 0.01))
    box = FancyBboxPatch((x, y), w, h, boxstyle=style, transform=fig.transFigure,
                         facecolor=face, edgecolor=edge, linewidth=lw,
                         zorder=z, alpha=alpha)
    fig.add_artist(box)
    return box


_NUM_RE = re.compile(r"^([^0-9]*)([0-9][0-9,]*)(.*)$", re.S)


def _renderer(fig):
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def big_number(fig, cx, cy, text, fs, color=RED, t=1.0, count=True,
               z=2.4, max_w=0.80, unit_scale=0.62, alpha=1.0):
    """ヒーロー数字。数字は第2書体の極太、**単位は62%に落として桁を立てる**。

    t<0.55 のあいだは 0→最終値のカウントアップ(ease_out)。
    数字を含まない文字列はそのまま1つのテキストで描く。
    """
    text = text.replace(",", "")
    m = _NUM_RE.match(text)
    fam = [F.NUM_FAMILY]
    if not m:
        S.text_fit(fig, cx, cy, F.fmt_disp(text), ha="center", va="center",
                   color=color, fontsize=fs * 0.72, max_w=max_w, zorder=z,
                   fontfamily=fam, fontweight=F.NUM_WEIGHT, alpha=alpha)
        return
    pre, digits, suf = m.groups()
    val = int(digits)
    if count:
        val = int(round(val * _ease(t / 0.55)))
        if t >= 0.55:
            val = int(digits)
    shown = f"{val:,}" if len(digits) >= 4 else str(val)
    r = _renderer(fig)
    fu = fs * unit_scale
    w_pre = F.measure_w(fig, r, pre, fu, fam, F.NUM_WEIGHT) if pre else 0.0
    w_num = F.measure_w(fig, r, shown, fs, fam, F.NUM_WEIGHT)
    w_suf = F.measure_w(fig, r, F.fmt_disp(suf), fu, fam, F.NUM_WEIGHT) if suf else 0.0
    # カウント中に幅が伸びてもはみ出さないよう、最終値の幅で縮める
    w_final = F.measure_w(fig, r, F.fmt_disp(digits), fs, fam, F.NUM_WEIGHT)
    total = w_pre + w_final + w_suf
    if total > max_w:
        k = max_w / total
        fs, fu = fs * k, fu * k
        w_pre = F.measure_w(fig, r, pre, fu, fam, F.NUM_WEIGHT) if pre else 0.0
        w_num = F.measure_w(fig, r, shown, fs, fam, F.NUM_WEIGHT)
        w_suf = F.measure_w(fig, r, F.fmt_disp(suf), fu, fam, F.NUM_WEIGHT) if suf else 0.0
    total_now = w_pre + w_num + w_suf
    x = cx - total_now / 2
    y_base = cy - 0.36 * fs * (S.DPI / 72) / S.H     # ベースライン下揃え
    kw = dict(va="baseline", color=color, fontfamily=fam, fontweight=F.NUM_WEIGHT,
              zorder=z, alpha=alpha)
    if pre:
        fig.text(x, y_base, pre, ha="left", fontsize=fu, **kw)
        x += w_pre
    fig.text(x, y_base, shown, ha="left", fontsize=fs, **kw)
    x += w_num
    if suf:
        fig.text(x, y_base, F.fmt_disp(suf), ha="left", fontsize=fu, **kw)


def person(name: str, height: float = 0.58, top: float = 0.855):
    """キャラだけ。いちばん基本の絵(ボブは draw_pose が入れる)。"""
    def painter(fig, t):
        F.draw_pose(fig, name, top=top, height=height)
    return painter


def person_bubble(name: str, text: str, height: float = 0.54, top: float = 0.855):
    """キャラ + 吹き出し(視聴者の心の声を代弁する。競合の70.8%の技法)。

    吹き出しは**しっぽの先端(口元側)からポップイン**する(2026-08-29)。
    貼り紙ではなく「心の声が湧く」に見せる。
    """
    def painter(fig, t):
        F.draw_pose(fig, name, cx=0.58, top=top, height=height)
        p = _back((t - 0.12) / 0.28)
        if p <= 0.01:
            return
        a = _ease((t - 0.12) / 0.20)
        x, y = 0.26, top - 0.08
        tipx, tipy = x + 0.20, y - 0.098          # しっぽの先端=拡大の原点
        def sc(px, py):
            return tipx + (px - tipx) * p, tipy + (py - tipy) * p
        bx, by = sc(x - 0.20, y - 0.055)
        bw, bh = 0.40 * p, 0.11 * p
        fig.add_artist(FancyBboxPatch((bx, by), bw, bh,
                                      boxstyle="round,pad=0,rounding_size=0.030",
                                      transform=fig.transFigure, facecolor=CARD,
                                      edgecolor=INK, linewidth=3.5, zorder=2.5, alpha=a))
        pts = [sc(x + 0.14, y - 0.050), sc(x + 0.20, y - 0.098), sc(x + 0.19, y - 0.044)]
        fig.add_artist(plt.Polygon(pts, transform=fig.transFigure, facecolor=CARD,
                                   edgecolor=INK, linewidth=3.5, zorder=2.55,
                                   joinstyle="miter", alpha=a))
        # しっぽの付け根の線を面色で塗りつぶして、吹き出しと一体に見せる
        rx, ry = sc(x + 0.135, y - 0.049)
        fig.add_artist(plt.Rectangle((rx, ry), 0.060 * p, 0.008 * p,
                                     transform=fig.transFigure, facecolor=CARD,
                                     edgecolor="none", zorder=2.57, alpha=a))
        tx, ty = sc(x, y)
        S.text_fit(fig, tx, ty, F.fmt_disp(text), ha="center", va="center", color=INK,
                   fontsize=38 * max(p, 0.2), max_w=0.34, zorder=2.6, alpha=a)
    return painter


def cover(line1: str, line2: str, line3: str, name: str = "01_base"):
    """カバー。**3段で役割を分け、最終行(問い)を最大にする**(2026-08-29)。

    - 背景はベタ黄ではなく帯と同じ縦グラデ(本編とブランドを揃える)
    - 帯はピンク(#ef5a7a)をやめて本編の赤。角丸+濃赤の落ち影で立体に
    - t で段階着地: 1行目→2行目スタンプ→帯が伸びる→問い→キャラ
    """
    def painter(fig, t):
        F.hide_chrome(fig)          # 全面カバー。帯とバッジは重ねない
        import numpy as np
        from matplotlib.colors import LinearSegmentedColormap
        bax = fig.add_axes([0, 0, 1, 1], zorder=1.5)
        bax.imshow(np.linspace(1, 0, 96).reshape(-1, 1), aspect="auto",
                   extent=(0, 1, 0, 1),
                   cmap=LinearSegmentedColormap.from_list(
                       "fpcover", [F.BAND_LO, F.BAND]))
        bax.axis("off")
        a1 = _ease(t / 0.15)
        S.text_fit(fig, 0.5, 0.935, F.fmt_disp(line1), ha="center", va="center",
                   color=F.BAND_INK, fontsize=60, max_w=0.86, zorder=2.4, alpha=a1)
        # 2行目: スタンプ着地(1.3→1.0)
        p2 = _ease((t - 0.08) / 0.25)
        if p2 > 0.01:
            fs2 = S.fit_fontsize(fig, line2, 92, max_w=0.90)
            fs3 = S.fit_fontsize(fig, F.fmt_disp(line3), 108, max_w=0.84)
            fs2 = min(fs2, fs3 * 0.82)          # 問い(3行目)を常に最大にする
            S.draw_rich_text(fig, 0.5, 0.848, line2, fs2 * (1.3 - 0.3 * p2),
                             base_color="#ffffff", emph_color=F.TELOP_EMPH,
                             outline=16.0, wrap=12, line_h=0.055, block_fit=0.92)
        # 帯: 左から伸びる。角丸+濃赤の影(ベタ矩形のピンクは全廃)
        pb = _ease((t - 0.28) / 0.22)
        if pb > 0.01:
            bx, bw, bh = 0.05, 0.90 * pb, 0.125
            by = 0.660
            style = "round,pad=0,rounding_size=0.035"
            fig.add_artist(FancyBboxPatch((bx + 0.004, by - 0.010), bw, bh,
                                          boxstyle=style, transform=fig.transFigure,
                                          facecolor="#7d1414", edgecolor="none",
                                          zorder=2.35))
            fig.add_artist(FancyBboxPatch((bx, by), bw, bh, boxstyle=style,
                                          transform=fig.transFigure, facecolor=RED,
                                          edgecolor="none", zorder=2.4))
            if pb > 0.92:
                S.text_fit(fig, 0.5, by + bh / 2, F.fmt_disp(line3), ha="center",
                           va="center", color="#ffffff", fontsize=108, max_w=0.84,
                           zorder=2.5)
        # キャラ: 下からスライドアップ。下端は画面外までブリード
        pc = _ease((t - 0.40) / 0.30)
        F.draw_pose(fig, name, top=0.615 - 0.05 * (1 - pc), height=0.78,
                    fade=False, bob=False)
    return painter


def table(headers, rows, highlight=None, title="", build=False, from_row=None):
    """表。**行を赤枠で1つずつ光らせる**(競合の33〜45%の型)。

    rows = [(左のセル, 右のセル), ...]
    highlight = 強調する行の添字(0始まり)。None なら枠なし。
    build = True なら行が下から順に着地する(最初に表を出すカットで使う)
    from_row = 赤枠が前のカットの行からすべってくる出発点

    2026-08-29 批評ループでの改修:
    - 金額は右揃え(桁を縦に通す)+ fmt_disp の桁区切り + 第2書体の極太
    - 行ラベルは INK(赤の常用をやめ、赤はハイライトだけに戻す)
    - 「合計」行は上に太罫・地色変え・級数1.2倍の赤で、明細と分離する
    - ハイライトは角丸枠+行の地色(#fbeae6)。枠は from_row からすべり、
      到着後に1回だけ太さがパルスする
    """
    n = len(rows)
    def painter(fig, t):
        FLOOR = 0.40
        top = 0.79
        bot = max(FLOOR, top - 0.105 * (n + 1))
        left, right = CARD_L, CARD_R
        split = left + (right - left) * 0.44
        rh = (top - bot) / (n + 1)
        card(fig, left, bot, right - left, top - bot, lw=2.5, r=0.014, z=2.0)
        # 見出し行
        hy = top - rh / 2
        fig.add_artist(plt.Rectangle((left + 0.005, top - rh), right - left - 0.010,
                                     rh - 0.004, transform=fig.transFigure,
                                     facecolor="#f6ecd8", edgecolor="none", zorder=2.1))
        fig.add_artist(plt.Line2D([left + 0.008, right - 0.008], [top - rh] * 2,
                                  transform=fig.transFigure, color="#cfc4ae",
                                  linewidth=2.5, zorder=2.4))
        if headers[0]:
            S.text_fit(fig, (left + split) / 2, hy, headers[0], ha="center",
                       va="center", color=INK, fontsize=38, max_w=0.36, zorder=2.3)
        if len(headers) > 1 and headers[1]:
            # 見出しは値と同じ右端に揃える(列として成立させる)
            S.text_fit(fig, right - 0.06, hy, headers[1], ha="right", va="center",
                       color=INK, fontsize=38, max_w=0.44, zorder=2.3)
        # 列の中で字の大きさをそろえる(いちばん長いセルに合わせる)
        r = _renderer(fig)
        fam_n = [F.NUM_FAMILY]
        fs_a = min([S.fit_fontsize(fig, a, 46, max_w=0.36) for a, _ in rows] or [46])
        fs_b = 44.0
        for _, b in rows:
            w = F.measure_w(fig, r, F.fmt_disp(b), fs_b, fam_n, F.NUM_WEIGHT)
            if w > 0.38:
                fs_b *= 0.38 / w
        is_total = [str(a) in ("合計", "計") for a, _ in rows]

        def rowy(i):
            return top - rh * (i + 2)

        # ハイライト(行の地色 + 角丸枠)。from_row からすべってくる
        if highlight is not None:
            if from_row is not None:
                u = _ease(t / 0.45)
                y_hl = rowy(from_row) * (1 - u) + rowy(highlight) * u
                a_hl = 1.0
            else:
                y_hl = rowy(highlight)
                a_hl = _ease(t / 0.30)
            pulse = math.sin(math.pi * min(1.0, max(0.0, (t - 0.55) / 0.45)))
            fig.add_artist(plt.Rectangle((left + 0.005, y_hl), right - left - 0.010,
                                         rh, transform=fig.transFigure,
                                         facecolor=RED_SOFT, edgecolor="none",
                                         zorder=2.06, alpha=a_hl))
            fig.add_artist(FancyBboxPatch((left + 0.006, y_hl + 0.002),
                                          right - left - 0.012, rh - 0.004,
                                          boxstyle="round,pad=0,rounding_size=0.012",
                                          transform=fig.transFigure, facecolor="none",
                                          edgecolor=RED, linewidth=5.0 + 2.5 * pulse,
                                          zorder=2.6, alpha=a_hl))
        for i, (a, b) in enumerate(rows):
            y0 = rowy(i)
            yc = y0 + rh / 2
            ap, dy = 1.0, 0.0
            if build:
                ap = _ease((t - 0.05 - i * 0.10) / 0.28)
                if ap <= 0.01:
                    continue
                dy = -(1 - ap) * 0.022
            if is_total[i]:
                fig.add_artist(plt.Rectangle((left + 0.005, y0), right - left - 0.010,
                                             rh, transform=fig.transFigure,
                                             facecolor="#f6ecd8", edgecolor="none",
                                             zorder=2.05, alpha=ap))
                fig.add_artist(plt.Line2D([left + 0.008, right - 0.008], [y0 + rh] * 2,
                                          transform=fig.transFigure, color=INK,
                                          linewidth=3.5, zorder=2.4, alpha=ap))
            elif i % 2 == 0:
                fig.add_artist(plt.Rectangle((left + 0.005, y0), right - left - 0.010,
                                             rh, transform=fig.transFigure,
                                             facecolor="#fdf8ee", edgecolor="none",
                                             zorder=2.05, alpha=ap))
            hl = (highlight == i)
            lab_color = RED if hl else INK
            val_color = RED if (hl or is_total[i]) else INK
            fs_v = fs_b * (1.2 if is_total[i] else 1.0)
            fs_l = fs_a * (1.1 if is_total[i] else 1.0)
            S.text_fit(fig, (left + split) / 2, yc + dy, a, ha="center", va="center",
                       color=lab_color, fontsize=fs_l, max_w=0.36, zorder=2.3, alpha=ap)
            # 金額: 右揃えで一の位を縦に通す + 桁区切り + 極太
            fig.text(right - 0.06, yc + dy, F.fmt_disp(b), ha="right", va="center",
                     color=val_color, fontsize=fs_v, fontfamily=fam_n,
                     fontweight=F.NUM_WEIGHT, zorder=2.3, alpha=ap)
        if title:
            S.text_fit(fig, 0.5, top + 0.045, F.fmt_disp(title), ha="center", va="center",
                       color=SUB, fontsize=40, max_w=0.9, zorder=2.3,
                       path_effects=_halo(40))
    return painter


def timeline(start: int, empty: float, end: int, fill_label: str, gap_label: str,
             show_gap: bool = True, title: str = "", empty_label: str = ""):
    """年齢の帯。**お金が続く区間と、足りない区間を1本の線で見せる。**

    start=65 / empty=82 / end=95 のように渡す。
    show_gap=False なら足りない側をまだ塗らない(1拍ためる)。
    """
    def painter(fig, t):
        # 帯だけを宙に置くと上下が空く。**白いパネルに載せて1つの塊にする**
        card(fig, 0.05, 0.395, 0.90, 0.365, edge=CARD_EDGE_STRONG, r=0.030, z=2.1)
        x0, x1 = 0.11, 0.89
        y, h = 0.540, 0.115
        def px(age):
            return x0 + (x1 - x0) * (age - start) / (end - start)
        xm = px(empty)
        p = _ease(t / 0.6)
        xm_t = x0 + (xm - x0) * p
        fig.add_artist(FancyBboxPatch((x0, y), xm_t - x0, h,
                                      boxstyle="round,pad=0,rounding_size=0.018",
                                      transform=fig.transFigure, facecolor=GREEN,
                                      edgecolor="none", zorder=2.2))
        S.text_fit(fig, (x0 + xm) / 2, y + h / 2, fill_label, ha="center", va="center",
                   color="#ffffff", fontsize=34, max_w=(xm - x0) * 0.92, zorder=2.4)
        if show_gap and t > 0.55:
            ag = _ease((t - 0.55) / 0.3)
            fig.add_artist(FancyBboxPatch((xm, y), x1 - xm, h,
                                          boxstyle="round,pad=0,rounding_size=0.018",
                                          transform=fig.transFigure, facecolor="#f4e0e0",
                                          edgecolor=RED, linewidth=4.0, hatch="//",
                                          zorder=2.2, alpha=ag))
            S.text_fit(fig, (xm + x1) / 2, y + h / 2, gap_label, ha="center",
                       va="center", color=RED, fontsize=38, max_w=(x1 - xm) * 0.88,
                       zorder=2.4, alpha=ag)
        # 目盛の文字。**empty は端数を持てる**(81歳8か月のような値を丸めない)
        mid_ha, mid_x = "center", xm
        if x1 - xm < 0.26:
            mid_ha, mid_x = "right", xm - 0.012
        ticks = [(f"{start}歳", x0, "left"),
                 (empty_label or f"{empty:g}歳", mid_x, mid_ha),
                 (f"{end}歳", x1, "right")]
        for lab, x, ha in ticks:
            if not show_gap and lab == f"{end}歳":
                continue
            tick_x = xm if lab == (empty_label or f"{empty:g}歳") else x
            fig.add_artist(plt.Line2D([tick_x, tick_x], [y - 0.030, y],
                                      transform=fig.transFigure,
                                      color=INK, linewidth=3.0, zorder=2.3))
            S.text_fit(fig, x, y - 0.058, lab, ha=ha, va="center",
                       color=INK, fontsize=40, max_w=0.26, zorder=2.4)
        if title:
            S.text_fit(fig, 0.5, TITLE_Y, F.fmt_disp(title), ha="center", va="center",
                       color=SUB, fontsize=40, max_w=0.84, zorder=2.3,
                       path_effects=_halo(40))
    return painter


def people(total: int, hit: int, label: str, title: str = ""):
    """人の絵を並べて、割合を数で見せる。**棒より、割合は「何人のうち何人」が速い。**

    total=10 / hit=5 なら、10人のうち5人を赤くする。
    """
    def painter(fig, t):
        card(fig, 0.05, 0.395, 0.90, 0.315, r=0.030, z=2.1)
        # **人数は声とそろえる。**声が「2人に1人」なのに絵が10人中5人だと、
        # 視聴者の頭の中で 5/10 = 1/2 の変換が起きる(2026-08-23のレビュー)
        x0, x1 = 0.10, 0.90
        span = min((x1 - x0) / total, 0.24)      # 人数が少ないときは大きくしすぎない
        left = 0.5 - span * total / 2
        cy = 0.520          # 見出しと頭がぶつからない高さ
        head_w = span * 0.42
        body_w = span * 0.50
        body_h = min(0.135, max(0.070, span * 0.62))
        n_lit = int(round(hit * _ease(t / 0.6)))
        for i in range(total):
            cx = left + span * (i + 0.5)
            col = RED_FILL if i < n_lit else WARM_GRAY
            # 頭
            fig.add_artist(Ellipse((cx, cy + body_h * 0.62), head_w,
                                   head_w * S.W / S.H, transform=fig.transFigure,
                                   facecolor=col, edgecolor="none", zorder=2.3))
            # 胴
            fig.add_artist(FancyBboxPatch((cx - body_w / 2, cy - body_h * 0.5),
                                          body_w, body_h,
                                          boxstyle="round,pad=0,rounding_size=0.018",
                                          transform=fig.transFigure, facecolor=col,
                                          edgecolor="none", zorder=2.3))
        S.text_fit(fig, 0.5, 0.432, F.fmt_disp(label), ha="center", va="center",
                   color=RED, fontsize=52, max_w=0.80, zorder=2.4)
        if title:
            S.text_fit(fig, 0.5, TITLE_Y, F.fmt_disp(title), ha="center", va="center",
                       color=SUB, fontsize=40, max_w=0.84, zorder=2.3,
                       path_effects=_halo(40))
    return painter


def formula(line: str, note: str = "", name: str = "02_point"):
    """持ち帰る式を1枚。**手順ではなく、その場で使える形**で置く。

    2026-08-29: 式は1枚絵で貼らず、**左辺 → 演算子(スタンプ)→ 右辺 → 注記**の
    順に着地させる。数字は極太・演算子と単位は小さく(演算子を数字より目立たせない)。
    カードは CARD_TOP/BOT に固定(前後のヒーローカードと同じ枠)。
    """
    def painter(fig, t):
        if name:
            F.draw_pose(fig, name, cx=0.5, top=0.845, height=0.315)
            top, bot = 0.495, 0.320
            fs_num = 60
        else:
            top, bot = CARD_TOP, CARD_BOT
            fs_num = 84
        sc = 0.88 + 0.12 * _back(t / 0.30)
        card(fig, CARD_L, bot, CARD_R - CARD_L, top - bot, edge=RED, lw=5.0,
             r=0.030, z=2.2, sc=sc)
        cy = (top + bot) / 2 + (0.030 if note else 0.0)
        # 「3162円 ÷ 30日」→ ["3162円", "÷", "30日"] に割って順に着地させる
        toks = [x for x in re.split(r"\s*([÷×+−=])\s*", line.strip()) if x]
        starts = [0.0, 0.22, 0.38, 0.50, 0.60]
        fam = [F.NUM_FAMILY]
        r = _renderer(fig)
        fs_op = fs_num * 0.55
        widths = []
        for tok in toks:
            if _NUM_RE.match(tok):
                m = _NUM_RE.match(tok)
                pre, digits, suf = m.groups()
                w = (F.measure_w(fig, r, pre, fs_num * 0.62, fam, F.NUM_WEIGHT) if pre else 0)
                w += F.measure_w(fig, r, F.fmt_disp(digits), fs_num, fam, F.NUM_WEIGHT)
                w += (F.measure_w(fig, r, suf, fs_num * 0.62, fam, F.NUM_WEIGHT) if suf else 0)
            elif tok in "÷×+−=":
                w = F.measure_w(fig, r, tok, fs_op, fam, F.NUM_WEIGHT) + 0.030
            else:
                w = F.measure_w(fig, r, tok, fs_num * 0.72, fam, F.NUM_WEIGHT)
            widths.append(w)
        total = sum(widths)
        k = min(1.0, 0.80 / total) if total else 1.0
        x = 0.5 - total * k / 2
        for j, (tok, w) in enumerate(zip(toks, widths)):
            st = starts[min(j, len(starts) - 1)]
            a = _ease((t - st) / 0.16)
            if a > 0.01:
                cx_t = x + w * k / 2
                if tok in "÷×+−=":
                    stamp = 1.0 + 0.5 * (1 - _ease((t - st) / 0.20))
                    fig.text(cx_t, cy, tok, ha="center", va="center", color=SUB,
                             fontsize=fs_op * k * stamp, fontfamily=fam,
                             fontweight=F.NUM_WEIGHT, zorder=2.4, alpha=a)
                else:
                    big_number(fig, cx_t, cy, tok, fs_num * k, color=RED,
                               t=1.0, count=False, z=2.4, max_w=w * k + 0.02,
                               alpha=a)
            x += w * k
        if note:
            an = _ease((t - 0.62) / 0.20)
            if an > 0.01:
                S.text_fit(fig, 0.5, bot + 0.045, note, ha="center", va="center",
                           color=SUB, fontsize=34, max_w=0.78, zorder=2.4, alpha=an)
    return painter


def bars(items, highlight=None, title="", ymax=None, prev_highlight=None):
    """棒。items = [(見出し, 値, 棒の上の語句), ...]

    2026-08-29: 裸の ax.bar をやめて figure 座標で自前描画。
    - 白パネルに載せ、基線(INK)を引き、上角を角丸にする
    - 伸長は ease_out_back(6%オーバーシュートして戻る)
    - 値ラベルは棒の頭に密着してカウントアップ。強調棒は極太60pt赤
    - prev_highlight を渡すと、赤がその棒からクロスフェードで移動する
    """
    vals = [v for _, v, _ in items]
    topval = ymax or max(vals) * 1.22
    n = len(items)
    def painter(fig, t):
        card(fig, 0.07, 0.415, 0.86, 0.375, r=0.030, z=2.0)
        x0i, x1i = 0.15, 0.85
        y0, y1 = 0.480, 0.720
        slot = (x1i - x0i) / n
        bw = slot * 0.60
        p = _back(t / 0.7)
        fam = [F.NUM_FAMILY]

        def mix(c1, c2, u):
            from matplotlib.colors import to_rgba
            a, b = to_rgba(c1), to_rgba(c2)
            return tuple(a[i] * (1 - u) + b[i] * u for i in range(4))

        for i, (lab, v, note) in enumerate(items):
            cx = x0i + slot * (i + 0.5)
            hl_now = (highlight == i)
            col = RED_FILL if hl_now else WARM_GRAY
            if prev_highlight is not None and prev_highlight != highlight:
                u = _ease(t / 0.35)
                was = RED_FILL if prev_highlight == i else WARM_GRAY
                col = mix(was, RED_FILL if hl_now else WARM_GRAY, u)
            h = (v / topval) * (y1 - y0) * p
            if h > 0.004:
                fig.add_artist(FancyBboxPatch((cx - bw / 2, y0), bw, h,
                                              boxstyle="round,pad=0,rounding_size=0.010",
                                              transform=fig.transFigure, facecolor=col,
                                              edgecolor="none", zorder=2.1))
            # 値ラベル: 棒の頭に密着してカウントアップ
            m = _NUM_RE.match(note or "")
            if m:
                pre, digits, suf = m.groups()
                val = int(round(int(digits) * _ease(t / 0.7)))
                shown = pre + (f"{val:,}" if len(digits) >= 4 else str(val)) + suf
            else:
                shown = note
            if hl_now:
                fig.text(cx, y0 + h + 0.012, F.fmt_disp(shown), ha="center",
                         va="bottom", color=RED, fontsize=60, fontfamily=fam,
                         fontweight=F.NUM_WEIGHT, zorder=2.4,
                         path_effects=_halo(60))
            else:
                fig.text(cx, y0 + h + 0.012, F.fmt_disp(shown), ha="center",
                         va="bottom", color=SUB, fontsize=36, fontfamily=fam,
                         fontweight=F.NUM_WEIGHT, zorder=2.4)
            S.text_fit(fig, cx, y0 - 0.020, lab, ha="center", va="top", color=INK,
                       fontsize=34, max_w=slot * 0.96, zorder=2.4)
        # 基線(地面)。棒の下角の角丸も隠れる
        fig.add_artist(plt.Line2D([x0i - 0.02, x1i + 0.02], [y0] * 2,
                                  transform=fig.transFigure, color=INK,
                                  linewidth=3.5, zorder=2.3))
        if title:
            S.text_fit(fig, 0.5, TITLE_Y, F.fmt_disp(title), ha="center", va="center",
                       color=SUB, fontsize=40, max_w=0.9, zorder=2.3,
                       path_effects=_halo(40))
    return painter


def hero(main: str, sub: str = "", name: str = "01_base"):
    """大きい数字を1つ。**キャラを上、数字を白いカードで下**に置く。

    name=None にすると数字だけになる(figure が主役の場面用)。
    カード枠の規約: **結論カード=赤(formula)、途中経過=ベージュ(hero)**。

    2026-08-29: カードは ease_out_back で着地し、数字は前半0.55でカウントアップ。
    数字は第2書体の極太、単位(円/万円/か月/%)は62%に落とす。
    """
    def painter(fig, t):
        if name:
            # バッジ(y≈0.876)より下から。上に出すと打消し表示が髪で隠れる
            F.draw_pose(fig, name, cx=0.5, top=0.845, height=0.395)
            top, bot = 0.450, 0.285
        else:
            top, bot = CARD_TOP, CARD_BOT
        sc = 0.85 + 0.15 * _back(t / 0.30)
        card(fig, CARD_L, bot, CARD_R - CARD_L, top - bot, r=0.028, z=2.2, sc=sc)
        head = 0.036 if sub else 0.0
        if sub:
            a = _ease((t - 0.15) / 0.2)
            S.text_fit(fig, 0.5, top - 0.034, F.fmt_disp(sub), ha="center",
                       va="center", color=SUB, fontsize=34, max_w=0.74, zorder=2.4,
                       alpha=a)
        big_number(fig, 0.5, (top - head + bot) / 2, main, 150, color=RED,
                   t=t, count=True, z=2.4, max_w=0.76)
    return painter


def arrow(left_val: str, right_val: str, left_lab: str = "", right_lab: str = "",
          title: str = ""):
    """左の額 → 右の額。**同じお金が別のものに変わる**ことを1枚で見せる。

    2026-08-29: 矢印は矩形+三角の継ぎ接ぎをやめて1枚のパス(比率固定)。
    左箱フェードイン → 矢印が伸びる → 右箱がパルスして文字が出る、の因果順。
    """
    def painter(fig, t):
        if title:
            S.text_fit(fig, 0.5, TITLE_Y, F.fmt_disp(title), ha="center", va="center",
                       color=SUB, fontsize=40, max_w=0.9, zorder=2.3,
                       path_effects=_halo(40))
        cy, h = 0.575, 0.185
        a_l = _ease(t / 0.18)
        # 左箱(グレー側は縁を濃くして背景に沈ませない)
        card(fig, 0.055, cy - h / 2, 0.36, h, edge=CARD_EDGE_STRONG, lw=4.0,
             r=0.024, z=2.2, alpha=a_l)
        big_number(fig, 0.055 + 0.18, cy + 0.012, left_val, 92, color=SUB,
                   t=1.0, count=False, z=2.4, max_w=0.32, alpha=a_l)
        # 右箱: 矢印到達(t=0.6)でパルス+文字の初出現
        hit = _ease((t - 0.58) / 0.22)
        pulse = math.sin(math.pi * min(1.0, max(0.0, (t - 0.58) / 0.30)))
        card(fig, 0.585, cy - h / 2, 0.36, h, edge=RED, lw=4.0 + 3.0 * pulse,
             r=0.024, z=2.2, sc=1.0 + 0.05 * pulse)
        if hit > 0.01:
            big_number(fig, 0.585 + 0.18, cy + 0.012, right_val, 92, color=RED,
                       t=1.0, count=False, z=2.4, max_w=0.32, alpha=hit)
        for x0, w, lab in ((0.055, 0.36, left_lab), (0.585, 0.36, right_lab)):
            if lab:
                S.text_fit(fig, x0 + w / 2, cy - h / 2 - 0.022, lab, ha="center",
                           va="top", color=SUB, fontsize=38, max_w=w, zorder=2.4,
                           path_effects=_halo(38))
        # 矢印: 1枚のパス。右へ伸びる(矢頭の比率は崩れない)
        x0, x1 = 0.425, 0.575
        xe = x0 + (x1 - x0) * max(0.22, _ease(t / 0.55))
        hl, hw, sh = 0.045, 0.042, 0.014
        xs = max(x0, xe - hl)
        fig.add_artist(plt.Polygon(
            [[x0, cy - sh], [xs, cy - sh], [xs, cy - hw], [xe, cy],
             [xs, cy + hw], [xs, cy + sh], [x0, cy + sh]],
            transform=fig.transFigure, facecolor=RED, edgecolor="none",
            zorder=2.5, closed=True))
    return painter


def cta(line: str, name: str = "02_point", show_button: bool = False,
        show_comment: bool = False):
    """締めの定型カット。競合は結論のあと**4カット**使っていた。

    2026-08-29: ボタン・吹き出しは ease_out_back で着地したあと呼吸パルス。
    「コメント」の吹き出しはキャラの頭の横に置き、しっぽを画面右下
    (コメント欄アイコンの方向)へ向ける。字幕の真上には置かない。
    """
    def painter(fig, t):
        F.draw_pose(fig, name, cx=0.40 if show_comment else 0.5, top=0.855,
                    height=0.40 if show_comment else 0.44)
        breath = 1.0 + 0.030 * max(0.0, math.sin(2 * math.pi * (t - 0.4) * 1.2))
        if show_button:
            p = _back((t - 0.15) / 0.25)
            if p > 0.01:
                s = p * breath
                bw, bh = 0.40 * s, 0.075 * s
                card(fig, 0.5 - bw / 2, 0.4555 - bh / 2, bw, bh, face=INK,
                     edge="none", lw=0, r=0.037, z=2.5)
                S.text_fit(fig, 0.5, 0.4555, "チャンネル登録", ha="center",
                           va="center", color="#ffffff", fontsize=40 * s,
                           max_w=0.34, zorder=2.6)
        if show_comment:
            # **声が「コメントで」なら、画面もコメントを指す**。
            # 頭の横に置き、しっぽは右下(コメント欄のUI)へ向ける
            p = _back((t - 0.15) / 0.25)
            if p > 0.01:
                s = p * breath
                bx, by, bw, bh = 0.55, 0.615, 0.37, 0.078
                cxb, cyb = bx + bw / 2, by + bh / 2
                bw2, bh2 = bw * s, bh * s
                tail = plt.Polygon(
                    [[cxb + bw2 * 0.12, cyb - bh2 * 0.45],
                     [cxb + bw2 * 0.34, cyb - bh2 * 0.45],
                     [cxb + bw2 * 0.46, cyb - bh2 * 0.45 - 0.062 * s]],
                    transform=fig.transFigure, facecolor=CARD, edgecolor=INK,
                    linewidth=3.5, zorder=2.5, joinstyle="miter")
                fig.add_artist(tail)
                fig.add_artist(FancyBboxPatch(
                    (cxb - bw2 / 2, cyb - bh2 / 2), bw2, bh2,
                    boxstyle="round,pad=0,rounding_size=0.030",
                    transform=fig.transFigure, facecolor=CARD,
                    edgecolor=INK, linewidth=3.5, zorder=2.55))
                S.text_fit(fig, cxb, cyb, "コメント", ha="center", va="center",
                           color=INK, fontsize=44 * s, max_w=0.32, zorder=2.6)
        if line:
            S.text_fit(fig, 0.5, 0.30, line, ha="center", va="center",
                       color=SUB, fontsize=34, max_w=0.86, zorder=2.3)
    return painter


def badge_head(painter):
    """このカットでは免責を先頭の一文だけにする(年5%のネタバレ防止)。"""
    def p(fig, t):
        F.badge_head(fig)
        painter(fig, t)
    return p
