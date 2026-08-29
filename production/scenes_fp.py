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

2026-08-29 批評3周目での改修(このファイルの現行):
- ヒーロー数字はカード内の幅72〜78%まで**自動拡大**(fs固定をやめた)
- 数式カードは**2段組**(上段=式・墨色 / 下段=答え・赤・1.6倍)
- 矢印比較も**共通の白カードに載せる**(3カットだけ地紋直置きだった)
- 「増える側」は GREEN の1族(赤=警告/損、緑=得。赤の意味過積載を解く)
- カード上端25%にトップライトの縦グラデ(無地白板→紙のカードに)
- 着地後アイドルの振幅を知覚閾値の上へ(0.010→0.028〜0.035+1.8秒鼓動)
"""
import math
import re

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Ellipse, FancyBboxPatch
import matplotlib.patheffects as path_effects

import fplib as F
import shortlib as S

# ---- 配色(ブランドの1セットに集約。ここ以外で色を直書きしない)
RED = "#b32020"            # ブランドの赤(文字・線・枠)。#e03131 は全廃
RED_FILL = "#c0392b"       # 棒など「面」の赤(文字の赤より一段明るく)
RED_SOFT = "#f9e6dc"       # ハイライト行の地。#fbeae6 は白寄りの桃色に見えた →
                           # 赤をわずかに橙へ回した暖色ティント(2026-08-29 批評2周目)
INK = F.INK_DARK
SUB = "#6b6459"            # 副テキスト(暖色グレー)
WARM_GRAY = "#b9ae99"      # 非強調の図形の面。青みグレー(#9aa0a6等)は全廃
CARD = F.CARD              # カードの白(#fffdf7)。純白は文字専用
CARD_TINT = "#fdf6e8"      # カード上端のトップライト(card() の縦グラデ用)
CARD_EDGE = "#e0d3ba"
# **非強調のグレーは WARM_GRAY(#b9ae99)の1族**(2026-08-29 批評3周目)。
# 縁は面(WARM_GRAY)を約20%暗くした親子関係の値。別系統の灰を足さない
CARD_EDGE_STRONG = "#948a76"
GREEN = "#5e8c3f"          # 肯定・充足・**増える側の面**(暖色寄りのブランド緑)
GREEN_DARK = "#4d7a33"     # 増える側の文字(面より一段濃く)
GREEN_SOFT = "#e8f0dc"     # 増える側の地(RED_SOFT の緑版)
SHADOW = "#d9c9a8"         # カードの落ち影


def _mix(c1, c2, u):
    """2色の線形補間(rgbaタプルを返す)。役割色の「褪せ」を親子関係で作る。"""
    from matplotlib.colors import to_rgba
    a, b = to_rgba(c1), to_rgba(c2)
    return tuple(a[i] * (1 - u) + b[i] * u for i in range(4))


# **損側の実体は、非強調のときも赤の気配を残す**(2026-08-29 批評4周目)。
# 12→14→15 で同じ114万円が赤→灰→墨と3回色を変え、同一性が切れていた。
# 完全なグレーに落とすのは「役割を持たない図形」だけ。
RED_FADE = _mix(RED_FILL, WARM_GRAY, 0.55)    # 非強調の損側の棒の面
LOSS_EDGE = _mix(RED, WARM_GRAY, 0.45)        # 非強調の損側の箱の縁
LOSS_INK = _mix(RED, SUB, 0.35)               # 非強調の損側の文字
HEAD_BG = "#efe2c8"        # 表の見出し行・合計行の地。地紋(#f6ecdb)と2段階離す
                           # (旧 #f6ecd8 は地紋と1しか違わず区別が伝わらなかった)

# ---- カードの固定寸法。**連続カットでパネル枠を動かさない**
# 2026-08-29 批評2周目: 表0.79・数式0.72・棒0.415…と部品ごとに枠が跳ねていた。
# **上辺と左右は全部品でこの1組に固定し、下辺だけ可変**にする。
# CARD_TOP/BOT も広げた(0.72→0.79 / 0.44→0.40)。カード上下の死んだドット帯
# (画面の約3割)を figure に食わせる。
CARD_L, CARD_R = 0.06, 0.94
CARD_TOP, CARD_BOT = 0.79, 0.40
TITLE_Y = 0.84             # 図の文脈見出し(カード外・注記バー直下)。全部品共通

_ease = F.ease_out
_back = F.ease_back


def _halo(fs: float, color=INK):
    """ドット地に直置きする小さめの字の、薄い白フチ。"""
    return [path_effects.Stroke(linewidth=fs * 0.12, foreground="#fffdf7"),
            path_effects.Normal()]


def idle(period: float = 0.9, phase: float = 0.0) -> float:
    """着地後も止まらないための共通の呼吸(-1〜1)。
    2026-08-29 批評2周目: 全部品が t=0.35〜0.7 で着地して以降静止していた。
    動画内時刻(F.LAST_T)で回すので、ユニットの後半でも必ずどこかが動く。"""
    return math.sin(2 * math.pi * (F.LAST_T / period) + phase)


def beat(period: float = 1.8, amp: float = 0.030) -> float:
    """周期の鼓動(1.0を下回らない)。常時ゆらゆらより上品に、周期に1回だけ膨らむ。
    2026-08-29 批評3周目: idle 0.010 は200px級の数字で約2pxの揺れ=静止に見えた。"""
    return 1.0 + amp * max(0.0, math.sin(2 * math.pi * F.LAST_T / period)) ** 3


def head_title(fig, title: str, t: float = 1.0):
    """カード外・上部の文脈見出し。全painter共通(上部の視線アンカーを揃える)。"""
    if not title:
        return
    a = _ease((t - 0.04) / 0.18)
    if a <= 0.01:
        return
    S.text_fit(fig, 0.5, TITLE_Y, F.fmt_disp(title), ha="center", va="center",
               color=SUB, fontsize=40, max_w=0.9, zorder=2.3, alpha=a,
               path_effects=_halo(40))


def _ma() -> float:
    """FancyBboxPatch の mutation_aspect。figure座標の rounding_size は
    9:16 のキャンバスで縦に1.78倍伸び、角丸が楕円弧になっていた
    (実測 横30px×縦40px。2026-08-29 批評5周目)。W/H を渡してスクリーン上の
    真円に戻す。**scenes_fp の FancyBboxPatch は必ずこれを渡す**。"""
    return S.W / S.H


def drop_shadow(fig, x, y, w, h, r=0.028, z=2.19, alpha=1.0, clip_y=None):
    """疑似ガウスの落ち影(3枚重ね)。**カードも棒もここから落とす。**

    2026-08-29 批評5周目: 単発のオフセット複製(SHADOW一色・alpha0.55)は
    拡大すると「板を2枚ずらして置いただけ」に見えた。オフセットと pad を
    広げながら薄くする3層で減衰を作る。
    - 影のオフセットは超低速で±1.5px揺れる(カードだけのユニットでも
      完全静止フレームを作らない)
    - clip_y: その高さより下を描かない(棒の影が基線=地面を貫通しない)
    """
    wob = 0.0015 * idle(period=1.4)
    clip = None
    if clip_y is not None:
        clip = plt.Rectangle((0.0, clip_y), 1.0, 1.0, transform=fig.transFigure)
    for dx, dy, a, pad in ((0.002, -0.003, 0.18, 0.0),
                           (0.004, -0.005, 0.12, 0.002),
                           (0.006, -0.008, 0.07, 0.005)):
        p = FancyBboxPatch((x + dx + wob, y + dy - wob), w, h,
                           boxstyle=f"round,pad={pad},rounding_size={r}",
                           transform=fig.transFigure, facecolor=SHADOW,
                           alpha=a * alpha, edgecolor="none", zorder=z,
                           mutation_aspect=_ma())
        if clip is not None:
            p.set_clip_path(clip)
        fig.add_artist(p)


def card(fig, x, y, w, h, face=CARD, edge=CARD_EDGE, lw=3.0, r=0.028,
         z=2.2, sc=1.0, alpha=1.0, ls="solid"):
    """白カード+落ち影。**全部品のカードはここから描く**(仕上げを揃える)。

    2026-08-29 批評5周目の全面改修:
    - **面(edgecolor=none)→ トップライト勾配 → 枠線専用パッチ**の3層に分離。
      勾配を枠線の上に被せていたため、枠の上25%だけ細く退色し、
      辺の途中に幅3px→6pxの段差ノッチが全カードで見えていた
    - トップライトの向きを修正: **上端=白(最も明るい)→ 下端=CARD**。
      前は上端が暗いクリーム=下光源で、影(左上光源)ともヘッダー帯とも逆だった
    - 落ち影は drop_shadow()(3枚重ねの疑似ガウス)
    - mutation_aspect=W/H で角丸をスクリーン上の真円にする
    返り値は枠線パッチ(最上層)。
    """
    if sc != 1.0:
        cx, cy = x + w / 2, y + h / 2
        x, y, w, h = cx - w * sc / 2, cy - h * sc / 2, w * sc, h * sc
    style = f"round,pad=0,rounding_size={r}"
    drop_shadow(fig, x, y, w, h, r=r, z=z - 0.01, alpha=alpha)
    box = FancyBboxPatch((x, y), w, h, boxstyle=style, transform=fig.transFigure,
                         facecolor=face, edgecolor="none",
                         zorder=z, alpha=alpha, mutation_aspect=_ma())
    fig.add_artist(box)
    if face == CARD and h > 0.10:
        gh = h * 0.25
        gax = fig.add_axes([x, y + h - gh, w, gh], zorder=z + 0.001)
        gax.axis("off")
        im = gax.imshow(np.linspace(1, 0, 48).reshape(-1, 1), aspect="auto",
                        extent=(0, 1, 0, 1), interpolation="bilinear",
                        cmap=LinearSegmentedColormap.from_list(
                            "cardtop", [CARD, "#ffffff"]),
                        alpha=0.9 * alpha)
        im.set_clip_path(box.get_path(), box.get_transform())
    border = FancyBboxPatch((x, y), w, h, boxstyle=style,
                            transform=fig.transFigure, facecolor="none",
                            edgecolor=edge, linewidth=lw, zorder=z + 0.002,
                            alpha=alpha, linestyle=ls, mutation_aspect=_ma())
    fig.add_artist(border)
    return border


_NUM_RE = re.compile(r"^([^0-9]*)([0-9][0-9,]*)(.*)$", re.S)
_WORD = re.compile(r"[^0-9]*[0-9]")


def _renderer(fig):
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def _num_w(fig, r, text: str, fs: float, unit_scale: float = 0.62) -> float:
    """big_number と同じ組み方(単位62%)での実測幅。"""
    text = text.replace(",", "")
    fam = [F.NUM_FAMILY]
    m = _NUM_RE.match(text)
    if not m:
        return F.measure_w(fig, r, F.fmt_disp(text), fs * 0.72, fam, F.NUM_WEIGHT)
    pre, digits, suf = m.groups()
    fu = fs * unit_scale
    w = F.measure_w(fig, r, pre, fu, fam, F.NUM_WEIGHT) if pre else 0.0
    w += F.measure_w(fig, r, F.fmt_disp(digits), fs, fam, F.NUM_WEIGHT)
    w += F.measure_w(fig, r, F.fmt_disp(suf), fu, fam, F.NUM_WEIGHT) if suf else 0.0
    return w


def _fit_num_fs(fig, text: str, fs: float, max_w: float) -> float:
    """big_number の組みで max_w に収まる最大の fs(fs を上限とする)。"""
    r = _renderer(fig)
    w = _num_w(fig, r, text, fs)
    return fs * min(1.0, max_w / w) if w > 0 else fs


def big_number(fig, cx, cy, text, fs, color=RED, t=1.0, count=True,
               z=2.4, max_w=0.80, unit_scale=0.62, alpha=1.0):
    """ヒーロー数字。数字は第2書体の極太、**単位は62%に落として桁を立てる**。

    t<0.55 のあいだは 0→最終値のカウントアップ(ease_out)。
    数字を含まない文字列はそのまま1つのテキストで描く。
    """
    text = text.replace(",", "")
    m = _NUM_RE.match(text)
    fam = [F.NUM_FAMILY]
    # 着地後は常時の呼吸パルス(±1.2%)。カウント完了からユニット末までの
    # 0.7〜1.2秒が完全静止になっていた(2026-08-29 批評5周目・実測 変化画素0.0%)
    boost = 1.0
    if t >= 0.55:
        boost *= 1.0 + 0.012 * math.sin(2 * math.pi * F.LAST_T / 0.9)
    if count and t >= 0.55:
        # 着地ポップ: 着地の瞬間に+22%膨らんで0.12秒で戻る。同時に色を
        # 一瞬白へ振る(音のdonだけ鳴って絵が素通りしていた)
        land = max(0.0, 1.0 - (t - 0.55) / 0.12)
        if land > 0.0:
            boost *= 1.0 + 0.22 * land
            color = _mix(color, "#ffffff", 0.35 * land)
    fs = fs * boost
    max_w = max_w * boost
    if not m:
        S.text_fit(fig, cx, cy, F.fmt_disp(text), ha="center", va="center",
                   color=color, fontsize=fs * 0.72, max_w=max_w, zorder=z,
                   fontfamily=fam, fontweight=F.NUM_WEIGHT, alpha=alpha)
        return
    pre, digits, suf = m.groups()
    val = int(digits)
    if count:
        # **expo減速**(2026-08-29 批評5周目)。前半70%線形の二段カーブは
        # 等速で駆け上がって安っぽかった。頭は速く・尻は粘る 1-(1-u)^2.8
        u = min(1.0, max(0.0, t / 0.55))
        frac = 1.0 - (1.0 - u) ** 2.8
        val = int(round(val * frac))
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


def person_bubble(name: str, text: str, height: float = 0.54, top: float = 0.855,
                  rows=None):
    """キャラ + 吹き出し(視聴者の心の声を代弁する。競合の70.8%の技法)。

    吹き出しは**しっぽの先端(口元側)からポップイン**する(2026-08-29)。
    貼り紙ではなく「心の声が湧く」に見せる。

    rows: [(ラベル, 金額), ...] を渡すと、キャラの左に明細アプリ風のミニカード
    を添える(2026-08-29 批評3周目。「明細を開く」と言うのに明細の絵が無く、
    立ち絵の下に画面の約22%の無人地帯があった)。
    """
    def painter(fig, t):
        F.draw_pose(fig, name, cx=0.58, top=top, height=height)
        p = _back((t - 0.12) / 0.28)
        if p <= 0.01:
            return
        a = _ease((t - 0.12) / 0.20)
        # 着地後も吹き出しがごく小さく膨縮する(完全静止のしっぽを作らない)
        if t > 0.50:
            p = p * (1.0 + 0.020 * idle(period=1.3))
        x, y = 0.26, top - 0.08
        tipx, tipy = x + 0.20, y - 0.098          # しっぽの先端=拡大の原点
        def sc(px, py):
            return tipx + (px - tipx) * p, tipy + (py - tipy) * p
        # 吹き出しの面はカード白(F.CARD)・縁は CARD_EDGE_STRONG。
        # 純白+INK縁は「2種類の白と別ブランドの声」に見えた(2026-08-29 批評2周目)
        bx, by = sc(x - 0.20, y - 0.055)
        bw, bh = 0.40 * p, 0.11 * p
        fig.add_artist(FancyBboxPatch((bx, by), bw, bh,
                                      boxstyle="round,pad=0,rounding_size=0.030",
                                      transform=fig.transFigure, facecolor=CARD,
                                      edgecolor=CARD_EDGE_STRONG, linewidth=4.0,
                                      zorder=2.5, alpha=a, mutation_aspect=_ma()))
        pts = [sc(x + 0.14, y - 0.050), sc(x + 0.20, y - 0.098), sc(x + 0.19, y - 0.044)]
        fig.add_artist(plt.Polygon(pts, transform=fig.transFigure, facecolor=CARD,
                                   edgecolor=CARD_EDGE_STRONG, linewidth=4.0,
                                   zorder=2.55, joinstyle="miter", alpha=a))
        # しっぽの付け根の線を面色で塗りつぶして、吹き出しと一体に見せる
        rx, ry = sc(x + 0.135, y - 0.049)
        fig.add_artist(plt.Rectangle((rx, ry), 0.060 * p, 0.008 * p,
                                     transform=fig.transFigure, facecolor=CARD,
                                     edgecolor="none", zorder=2.57, alpha=a))
        # **本体の下辺の枠線を、しっぽの内側だけ面色で消す**(2026-08-29 批評5周目)。
        # しっぽの縁取りが本体の枠線と別描きのため、接合部に小さなノッチ(段差)が
        # 出ていた。しっぽの2辺が下辺(y-0.055)と交わる範囲の内側を塗りつぶし、
        # 本体としっぽの輪郭を1本に繋げる
        seam = [sc(x + 0.147, y - 0.052), sc(x + 0.187, y - 0.052),
                sc(x + 0.188, y - 0.058), sc(x + 0.154, y - 0.058)]
        fig.add_artist(plt.Polygon(seam, transform=fig.transFigure, facecolor=CARD,
                                   edgecolor="none", zorder=2.58, alpha=a))
        tx, ty = sc(x, y)
        # 文字は「素のゴシック細字」をやめ、帯の文字色(BAND_INK)+級数1.2倍
        S.text_fit(fig, tx, ty, F.fmt_disp(text), ha="center", va="center",
                   color=F.BAND_INK, fontsize=46 * max(p, 0.2), max_w=0.36,
                   zorder=2.6, alpha=a)
        # 明細アプリ風のミニカード(行は表と同じ値。値・文言は足さない)
        # 2026-08-29 批評4周目:
        # - **容器が固まってから中身が灯る**(カードのフェードと行の点灯が同時で、
        #   中間フレームが未完成品に見えていた)
        # - ラベルの級数は**全行で1つに固定**(text_fit の行別縮小で
        #   「Amazonプライム」だけ縮み、同一テーブル内で級数が揺れていた)
        # - 数値は本編の表と同じ INK・Black・ラベルより大きく(主従を数値優位に)
        # - カード幅+0.06・行高1.15倍で下端を字幕側へ下げ、右下の死帯を詰める
        if rows:
            ac = _ease(t / 0.15)
            if ac > 0.01:
                rhh = 0.076
                mw = 0.46
                mh = rhh * len(rows) + 0.030
                mx, my = 0.045, 0.285
                card(fig, mx, my, mw, mh, lw=2.5, r=0.020, z=2.2, alpha=ac)
                # 全行の実測幅から共通のラベル級数を1つ決める
                r = _renderer(fig)
                fam_l = [F.FONT_FAMILY, F.FONT_FALLBACK_FAMILY]
                fs_lab = 28.0
                for la, _vb in rows:
                    wla = F.measure_w(fig, r, str(la), fs_lab, fam_l, F.FONT_WEIGHT)
                    if wla > 0.24:
                        fs_lab *= 0.24 / wla
                # 行のリズムは本編の表と同じ「罫なし・帯なし」に統一
                # (2026-08-29 批評5周目: ヘアライン罫は本編の表に無い第3の
                # リスト文法で、同じデータが別ジオメトリで再登場していた)。
                # ラベル左端・数値右端のインセットも表と同じ比率(幅の6.1% / 6.8%)
                ins_l = mw * 0.061
                ins_r = mw * 0.068
                for i, (la, vb) in enumerate(rows):
                    ai = _ease((t - 0.18 - i * 0.10) / 0.18)
                    if ai <= 0.01:
                        continue
                    yy = my + mh - 0.018 - (i + 0.5) * rhh
                    fig.text(mx + ins_l, yy, str(la), ha="left", va="center",
                             color=INK, fontsize=fs_lab, fontfamily=fam_l,
                             fontweight=F.FONT_WEIGHT, zorder=2.4, alpha=ai)
                    fig.text(mx + mw - ins_r, yy, F.fmt_disp(str(vb)), ha="right",
                             va="center", color=INK, fontsize=30,
                             fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT,
                             zorder=2.4, alpha=ai)
    return painter


def person_cards(name: str, labels, height: float = 0.50, top: float = 0.855):
    """キャラ(困り顔)+左に積み上がるカード列。冒頭0秒目の「積み上がる感」用。
    2026-08-29 批評2周目: 0秒目が笑顔の立ち絵と羅列テロップだけで緊張が無かった。"""
    def painter(fig, t):
        F.draw_pose(fig, name, cx=0.66, top=top, height=height)
        n = len(labels)
        y0, step = 0.455, 0.105
        for i, lab in enumerate(labels):
            p = _back((t - 0.08 - i * 0.16) / 0.24)
            if p <= 0.01:
                continue
            a = _ease((t - 0.08 - i * 0.16) / 0.16)
            bx = -0.30 + (0.05 + 0.30) * p       # 左から滑り込む
            card(fig, bx, y0 + i * step, 0.40, 0.088, edge=CARD_EDGE_STRONG,
                 lw=3.0, r=0.024, z=2.2, alpha=a)
            S.text_fit(fig, bx + 0.20, y0 + i * step + 0.044, str(lab), ha="center",
                       va="center", color=INK, fontsize=40, max_w=0.36,
                       zorder=2.4, alpha=a)
    return painter


def cover(line1: str, line2: str, line3: str, name: str = "01_base",
          disclaimer: str = "", count_from: str = "", badge_color: str = RED,
          flip: bool = False):
    """カバー。**3段で役割を分け、最終行(赤バッジの中身)を最大にする**。

    2026-08-29 批評2周目の改修:
    - 背景をオレンジの縦グラデから**本編と同じクリーム+ドット**に変更。
      タップの前後で別ブランドに見える断絶を消す(角丸・影の言語も本編と共有)
    - 1行目も**テロップと同じ4層縁取り**で描く。「素の文字」をカバーに置かない
    - disclaimer: 仮定に基づく数字をカバーに出すときの打消し表示(戦略§6-2)

    2026-08-29 批評3周目の改修:
    - バッジの登場を前倒し(t=0.10)。前半ほぼ半分が空の赤い板だった
    - 数字は遅くとも t≈0.12 で着地し、以後は鼓動し続ける(完全凍結を無くす)
    - バッジの高さ1.4倍・数字1.3倍。売り物の面積が画面高の約15%しか無かった

    2026-08-29 批評5周目の改修:
    - **y<0.08 の帯にはテキストを置かない**(Shorts実機のキャプション・
      シークバー帯に掛かる)。打消し表示はバッジ直下のクリーム角丸プレートに
      fontsize>=26 で載せる(素の22pt灰字はタイル寸で字高2px=実質不可視だった)
    - 1行目の基準級数 56→76(タイル寸で判読できる字高に。9字前後に収める運用)
    - バッジは常に中央合わせ(左右マージンが3px非対称だった分岐を除去)
    - カウント窓を前倒し(t=0.12までに最終値着地。フィードの静止切り取りに
      中途の値が晒される時間を尺の12%未満にする)
    - 背景ドットは減光(縮小時のスペックルノイズ)。badge_color でAB検証可
    - flip: 立ち絵を左右反転(視線・指先をバッジへ向ける構図用)
    """
    def painter(fig, t):
        F.hide_chrome(fig)      # 帯・バッジは重ねない(背景のクリーム+ドットは残る)
        F.dim_dots(fig)         # 水玉はカバーだけ半減光(72px縮小でノイズになる)
        # 1行目: 白抜き+4層縁取り(本編テロップと同じ描画)
        a1 = _ease(t / 0.15)
        if a1 > 0.01:
            fs1 = S.fit_fontsize(fig, F.fmt_disp(line1), 76, max_w=0.88)
            txt = fig.text(0.5, 0.940, F.fmt_disp(line1), ha="center", va="center",
                           color=F.TELOP, fontsize=fs1, zorder=2.4, alpha=a1,
                           fontfamily=[F.FONT_FAMILY, F.FONT_FALLBACK_FAMILY])
            txt.set_path_effects(F.fx(F.TELOP, fs1))
        # 2行目: スタンプ着地(1.3→1.0)。白抜き+縁取り
        p2 = _ease((t - 0.08) / 0.22)
        if p2 > 0.01:
            fs2 = S.fit_fontsize(fig, F.fmt_disp(line2), 84, max_w=0.90)
            S.draw_rich_text(fig, 0.5, 0.855, F.fmt_disp(line2), fs2 * (1.3 - 0.3 * p2),
                             base_color="#ffffff", emph_color=F.TELOP_EMPH,
                             outline=16.0, wrap=12, line_h=0.055, block_fit=0.92)
        # 赤バッジ: 左から伸びる。角丸+濃赤の影(本編カードと同じ立体言語)。
        # 前半を空の板で流さない: t=0.10 で伸び始め、0.32 で着地する
        pb = _ease((t - 0.10) / 0.22)
        if pb > 0.01:
            bs = beat(period=1.6, amp=0.014) if t > 0.55 else 1.0
            bh = 0.225 * bs
            bw = 0.90 * pb * bs
            by0 = 0.560
            # バッジは**常に中央合わせ**(pb<0.99 で 0.05 固定になる分岐が
            # 左右マージンを3px非対称にしていた。2026-08-29 批評5周目)
            bx, by = 0.5 - bw / 2, by0 - (bh - 0.225) / 2
            style = "round,pad=0,rounding_size=0.035"
            fig.add_artist(FancyBboxPatch((bx + 0.004, by - 0.010), bw, bh,
                                          boxstyle=style, transform=fig.transFigure,
                                          facecolor=_mix(badge_color, "#000000", 0.38),
                                          edgecolor="none",
                                          zorder=2.35, mutation_aspect=_ma()))
            fig.add_artist(FancyBboxPatch((bx, by), bw, bh, boxstyle=style,
                                          transform=fig.transFigure,
                                          facecolor=badge_color,
                                          edgecolor="none", zorder=2.4,
                                          mutation_aspect=_ma()))
            if pb > 0.55:
                # - カウントは count_from → 最終値。0からだと途中の値など
                #   動画のどこにも無い数字が最初の1秒に立つ
                # - 窓は (t-0.03)/0.09 = **t=0.12 で着地**(2026-08-29 批評5周目。
                #   正しい値で立っている時間を尺の88%以上にする)
                nb = beat(period=1.6) if t > 0.60 else 1.0
                shown3 = line3
                m1 = _NUM_RE.match(line3.replace(",", ""))
                m0 = _NUM_RE.match(count_from.replace(",", "")) if count_from else None
                if m0 and m1:
                    v0, v1 = int(m0.group(2)), int(m1.group(2))
                    if t >= 0.12:
                        vv = v1
                    else:
                        vv = int(round(v0 + (v1 - v0)
                                       * _ease(max(0.0, (t - 0.03) / 0.09))))
                    shown3 = m1.group(1) + str(vv) + m1.group(3)
                # 光学センタリング: ベースライン組みの数字は幾何中心より
                # やや上に見えるので、中心を8px下げる(2026-08-29 批評5周目)
                big_number(fig, 0.5, by + bh / 2 - 0.008, shown3, 200 * nb,
                           color="#ffffff", t=1.0, count=False,
                           z=2.5, max_w=min(0.84, 0.80 * nb))
            if disclaimer:
                # 打消し表示は**バッジ直下のクリーム角丸プレート**に置く
                # (2026-08-29 批評5周目)。画面最下部(y=0.032)は
                # (a) ShortsのタイトルUI帯に被る (b) 素の灰22ptで
                # コントラスト比≈1.5:1 (c) タイル寸で字高2px、の三重で
                # 実質不可視だった。戦略§6-2の打消しは読めなければ意味がない。
                # **y<0.08 の帯にはテキストを置かない。**
                ad = _ease((t - 0.40) / 0.20)
                if ad > 0.01:
                    ph = 0.045
                    fig.add_artist(FancyBboxPatch(
                        (0.5 - 0.42, 0.531 - ph / 2), 0.84, ph,
                        boxstyle="round,pad=0,rounding_size=0.014",
                        transform=fig.transFigure, facecolor="#fff8ec",
                        edgecolor="none", alpha=0.92 * ad, zorder=2.52,
                        mutation_aspect=_ma()))
                    S.text_fit(fig, 0.5, 0.531, disclaimer, ha="center",
                               va="center", color=F.DISCLAIM, fontsize=28,
                               max_w=0.80, zorder=2.55, alpha=ad)
        # キャラ: 下からスライドアップ。バッジ下端(0.560)と頭頂の間に
        # 24px以上の空きを取る(2026-08-29 批評5周目: バッジ下端y=863、
        # 頭頂y=864 の1px接触が「頭に載った看板」に見えていた)
        pc = _ease((t - 0.30) / 0.35)
        F.draw_pose(fig, name, top=0.585 - 0.05 * (1 - pc), height=0.76,
                    fade=False, bob=True, flip=flip)
    return painter


def table(headers, rows, highlight=None, title="", build=False, from_row=None,
          total_mode="red", wave_role="warn", focus=None):
    """表。**行を赤枠で1つずつ光らせる**(競合の33〜45%の型)。

    rows = [(左のセル, 右のセル), ...]
    highlight = 強調する行の添字(0始まり)。None なら枠なし。
                "sweep" なら赤枠が明細行を**往復し続ける**(問いのカット用。
                最終行に停めない: 停めると答えを指すのと同じになる)。
                "wave" なら明細行の地色が順に点灯していく(全部やめなくていい、用)
    build = True なら行が下から順に着地する(最初に表を出すカットで使う)
    from_row = 赤枠が前のカットの行からすべってくる出発点
    total_mode = "red"(合計を赤で出す)/ "dim"(答えをまだ明かさない)。
                 2026-08-29 批評3周目: dim をグレー淡色にしても数値は完全に読めて
                 いた(「伏せ」ではなく「少し暗い正解」)。**dim は数字を ?,???円 に
                 マスクする**。開示(total_mode="red")のカットで初めて数字が出る

    2026-08-29 批評3周目の改修:
    - ハイライトの地色もカードの内側パディングにインセット(カード縁まで
      食い出して、行ハイライトでなく「カードに刺さった別の枠」に見えていた)
    - from_row 遷移は移動元の地色をフェードアウトしながら移動先をフェードイン
      (中間フレームの単独完全強調=情報の嘘、を作らない)
    - wave の点灯間隔は行数から逆算(前倒し着地で尻尾が死んでいた)
    - 縞模様(#fdf8ee)を全廃。カード白と2段階未満の差で「白の2種混在」だった

    2026-08-29 批評4周目:
    - wave_role="keep": 点灯の地を GREEN_SOFT・ラベルを GREEN_DARK にする。
    - total_mode="dim" は highlight が合計行でも**マスクを保つ**
      (問いのカットで合計行に枠を滑らせても答えが漏れない)

    2026-08-29 批評5周目:
    - focus=行index: その行を中心に表全体を 1.0→1.12 へ ease_out でパンチイン
      (冒頭3〜10秒が同一構図の静止テーブル4連発だった。トップは2〜3秒ごとに
      必ずリフレームする)。赤枠の移動(0.6)とスケール到達を同時に着地させる
    - ヘッダー帯・合計帯のインセットを行ハイライト帯と**同一の定数**に統一
      (全幅帯とインセット帯の2系統が混在していた)。角丸も帯と同じ 0.012
    - wave_role="keep" は赤側と同じ band+frame ジオメトリで、色だけ緑
      (タイル3枚に見えていた)。値も点灯後は GREEN_DARK
    - build 中のハイライト枠は当該行テキストの出現+0.06秒に遅らせる
      (空の赤枠だけが先に立つフレームがエラー表示に見えていた)
    """
    n = len(rows)
    def painter(fig, t):
        top = CARD_TOP
        bot = max(CARD_BOT, top - 0.105 * (n + 1))
        left, right = CARD_L, CARD_R
        rh = (top - bot) / (n + 1)

        def rowy_b(i):
            return top - rh * (i + 2)

        # focus: 対象行を中心とした等方スケール(パンチイン)。
        # 位置は zx/zy、寸法・級数は *zk を通す
        zk = 1.0
        fcx, fcy = 0.5, (top + bot) / 2
        if focus is not None:
            zk = 1.0 + 0.12 * _ease(t / 0.60)
            fcy = rowy_b(focus) + rh / 2
            if zk > 1.001:
                # ズーム後のカード上辺が文脈見出し(TITLE_Y)に食い込まないよう、
                # 拡大の中心を必要なぶんだけ上へ寄せる(上辺 <= 0.806)
                fcy = max(fcy, (0.806 - top * zk) / (1.0 - zk))

        def zx(v):
            return fcx + (v - fcx) * zk

        def zy(v):
            return fcy + (v - fcy) * zk

        x_lab = zx(left + 0.045)      # ラベル列の共通の行頭
        x_val = zx(right - 0.06)      # 数値列の共通の右端
        card(fig, zx(left), zy(bot), (right - left) * zk, (top - bot) * zk,
             lw=2.5 * zk, r=0.024 * zk, z=2.0)
        # 帯(ヘッダー・合計・ハイライト)の共通ジオメトリ。
        # インセット量は1系統に統一する(pad_in)
        fx0_b = (left + 0.045) - 0.022
        fw_b = ((right - 0.06) + 0.022) - fx0_b
        bx0_b, bw_bd = fx0_b - 0.006, fw_b + 0.012

        def hband(y_b, h_b, a_b, color=HEAD_BG, z_b=2.05):
            fig.add_artist(FancyBboxPatch(
                (zx(bx0_b), zy(y_b)), bw_bd * zk, h_b * zk,
                boxstyle=f"round,pad=0,rounding_size={0.012 * zk:.4f}",
                transform=fig.transFigure, facecolor=color, edgecolor="none",
                zorder=z_b, alpha=a_b, mutation_aspect=_ma()))

        # 見出し行
        hy = zy(top - rh / 2)
        hband(top - rh + 0.002, rh - 0.006, 1.0, z_b=2.1)
        fig.add_artist(plt.Line2D([zx(bx0_b), zx(bx0_b + bw_bd)],
                                  [zy(top - rh)] * 2,
                                  transform=fig.transFigure, color="#cfc4ae",
                                  linewidth=2.5 * zk, zorder=2.4))
        if headers[0]:
            S.text_fit(fig, x_lab, hy, headers[0], ha="left",
                       va="center", color=INK, fontsize=38 * zk, max_w=0.36 * zk,
                       zorder=2.3)
        if len(headers) > 1 and headers[1]:
            # 見出しは値と同じ右端に揃える(列として成立させる)
            S.text_fit(fig, x_val, hy, headers[1], ha="right", va="center",
                       color=INK, fontsize=38 * zk, max_w=0.44 * zk, zorder=2.3)
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
        detail_idx = [i for i in range(n) if not is_total[i]]

        def rowy(i):
            return rowy_b(i)

        def band(y_hl, a_hl, color=RED_SOFT):
            hband(y_hl + 0.004, rh - 0.008, a_hl, color=color, z_b=2.06)

        def frame(y_hl, a_hl, lw, squash=1.0, color=RED):
            hh = (rh - 0.004) * squash
            yy = y_hl + 0.002 + (rh - 0.004 - hh) / 2
            fig.add_artist(FancyBboxPatch(
                (zx(fx0_b), zy(yy)), fw_b * zk, hh * zk,
                boxstyle=f"round,pad=0,rounding_size={0.012 * zk:.4f}",
                transform=fig.transFigure, facecolor="none",
                edgecolor=color, linewidth=lw,
                zorder=2.6, alpha=a_hl, mutation_aspect=_ma()))

        hl_row = highlight if isinstance(highlight, int) else None
        if hl_row is not None:
            # build 中は、枠の出現を当該行テキストの出現(0.05+i*0.10)+0.06 に
            # 遅らせる(空の赤枠が先に立たない)
            gate_st = (0.05 + hl_row * 0.10 + 0.06) if build else 0.0
            if from_row is not None:
                u = _ease(t / 0.60)
                y_hl = rowy(from_row) * (1 - u) + rowy(hl_row) * u
                a_hl = 1.0
                squash = 0.94 + 0.06 * u        # 移動中はつぶして、動きを読ませる
                # 地色は両行のクロスフェード(枠だけがすべる。移動中の中間位置に
                # 「どの行でもない場所の単独強調」を作らない)
                band(rowy(from_row), 1.0 - u)
                band(rowy(hl_row), u)
            else:
                y_hl = rowy(hl_row)
                a_hl = _ease((t - gate_st) / 0.30)
                squash = 1.0
                band(y_hl, a_hl)
            if t > 0.60:
                # 到着後は連続の低振幅パルス(着地後の完全静止を作らない)
                lw = 5.0 + 1.2 * idle(period=0.7)
            else:
                lw = 5.0 + 2.5 * math.sin(math.pi * min(1.0, max(0.0, (t - 0.30) / 0.30)))
            if a_hl > 0.01:
                frame(y_hl, a_hl, lw * zk, squash)
        elif highlight == "sweep" and detail_idx:
            # 問いのカット: 赤枠が明細行を**往復し続ける**(答えの行を指さない・
            # 最終行に停めない)
            span = max(1, len(detail_idx) - 1)
            ph = (t / 0.85) * span
            k = ph % (2 * span)
            seg = 2 * span - k if k > span else k
            i0 = min(int(seg), span - 1) if span > 0 else 0
            u = _ease(min(1.0, seg - i0))
            i1 = min(i0 + 1, len(detail_idx) - 1)
            y_hl = rowy(detail_idx[i0]) * (1 - u) + rowy(detail_idx[i1]) * u
            a_hl = _ease(t / 0.20)
            band(y_hl, a_hl)
            frame(y_hl, a_hl, (5.0 + 1.2 * idle(period=0.7)) * zk)
        # wave の点灯は行数から逆算して尺いっぱいに配分(最終行が t≈0.75 で着地)
        wave_step = (0.55 / max(1, len(detail_idx))) if detail_idx else 0.22
        wave_col = GREEN_SOFT if wave_role == "keep" else RED_SOFT
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
                hband(y0, rh, ap)
                fig.add_artist(plt.Line2D([zx(bx0_b), zx(bx0_b + bw_bd)],
                                          [zy(y0 + rh)] * 2,
                                          transform=fig.transFigure, color=INK,
                                          linewidth=3.5 * zk, zorder=2.4, alpha=ap))
            wave_lit = False
            if highlight == "wave" and not is_total[i]:
                # 明細行が順に点灯していく(点いたら消さない。点灯済みの行も
                # 地色がごく薄く呼吸して、表全体が生きて見える)。
                # keep は赤側と同じ band+frame の文法で、色だけ緑
                di = detail_idx.index(i)
                aw = _ease((t - 0.12 - di * wave_step) / wave_step)
                wave_lit = aw > 0.5
                if aw > 0.01:
                    breathe = 0.94 + 0.06 * (0.5 + 0.5 * idle(period=1.1,
                                                              phase=di * 0.8))
                    band(y0, min(1.0, aw * breathe), color=wave_col)
                    if wave_role == "keep":
                        frame(y0, min(1.0, aw), 4.0 * zk, color=GREEN)
            hl = (hl_row == i)
            # dim は highlight が合計行でもマスクを保つ(問いのカットで枠を
            # 合計行へ滑らせても、開示は total_mode="red" のカットまで起きない)
            dim_total = (is_total[i] and total_mode == "dim")
            lab_color = RED if hl else INK
            val_color = SUB if dim_total else (RED if (hl or is_total[i]) else INK)
            if highlight == "wave" and wave_role == "keep" and wave_lit:
                lab_color = GREEN_DARK   # 「残してよい」行は緑で点灯
                val_color = GREEN_DARK   # 値も同じ文法(赤側の「値も赤」と対称)
            fs_v = fs_b * (1.05 if dim_total else (1.2 if is_total[i] else 1.0))
            fs_l = fs_a * (1.1 if is_total[i] else 1.0)
            # ラベル: 左揃えで行頭を縦に通す(合計行も同じ行頭に載せる)
            S.text_fit(fig, x_lab, zy(yc + dy), a, ha="left", va="center",
                       color=lab_color, fontsize=fs_l * zk, max_w=0.40 * zk,
                       zorder=2.3, alpha=ap)
            # 金額: 右揃えで一の位を縦に通す + 桁区切り + 極太。
            # **dim の合計は数字そのものをマスクする**(?,???円)。
            if dim_total:
                shown_v = re.sub(r"\d", "?", F.fmt_disp(b))
            elif is_total[i] and hl:
                # 開示のカット(合計行が強調行のとき)だけ、合計を 0→最終値の
                # カウントアップで初出しする
                mv = _NUM_RE.match(str(b).replace(",", ""))
                if mv:
                    pre_v, dig_v, suf_v = mv.groups()
                    vv = int(round(int(dig_v) * _ease(t / 0.55)))
                    if t >= 0.55:
                        vv = int(dig_v)
                    shown_v = pre_v + f"{vv:,}" + F.fmt_disp(suf_v)
                else:
                    shown_v = F.fmt_disp(b)
            else:
                shown_v = F.fmt_disp(b)
            fig.text(x_val, zy(yc + dy), shown_v, ha="right", va="center",
                     color=val_color, fontsize=fs_v * zk, fontfamily=fam_n,
                     fontweight=F.NUM_WEIGHT, zorder=2.3, alpha=ap)
        head_title(fig, title, t)
    return painter


def timeline(start: int, empty: float, end: int, fill_label: str, gap_label: str,
             show_gap: bool = True, title: str = "", empty_label: str = "",
             fill_color: str = GREEN, fill_ink: str = "#ffffff"):
    """年齢の帯。**お金が続く区間と、足りない区間を1本の線で見せる。**

    start=65 / empty=82 / end=95 のように渡す。
    show_gap=False なら足りない側をまだ塗らない(1拍ためる)。
    fill_color/fill_ink: 塗る側の役割色(既定は「お金がある」=緑。
    「払い続ける」のような損側の帯には褪せ赤を渡す。2026-08-29 批評5周目)。
    """
    def painter(fig, t):
        # 帯だけを宙に置くと上下が空く。**白いパネルに載せて1つの塊にする**
        # (カード枠は全部品共通の CARD_L/R/TOP/BOT。カット間で枠を跳ねさせない)
        card(fig, CARD_L, CARD_BOT, CARD_R - CARD_L, CARD_TOP - CARD_BOT,
             edge=CARD_EDGE_STRONG, r=0.028, z=2.1)
        x0, x1 = 0.12, 0.88
        y, h = 0.575, 0.125
        def px(age):
            return x0 + (x1 - x0) * (age - start) / (end - start)
        xm = px(empty)
        p = _ease(t / 0.6)
        xm_t = x0 + (xm - x0) * p
        fig.add_artist(FancyBboxPatch((x0, y), xm_t - x0, h,
                                      boxstyle="round,pad=0,rounding_size=0.018",
                                      transform=fig.transFigure, facecolor=fill_color,
                                      edgecolor="none", zorder=2.2,
                                      mutation_aspect=_ma()))
        S.text_fit(fig, (x0 + xm) / 2, y + h / 2, fill_label, ha="center", va="center",
                   color=fill_ink, fontsize=34, max_w=(xm - x0) * 0.92, zorder=2.4,
                   alpha=_ease((t - 0.25) / 0.25))
        if show_gap and t > 0.55:
            ag = _ease((t - 0.55) / 0.3)
            fig.add_artist(FancyBboxPatch((xm, y), x1 - xm, h,
                                          boxstyle="round,pad=0,rounding_size=0.018",
                                          transform=fig.transFigure, facecolor=RED_SOFT,
                                          edgecolor=RED, linewidth=4.0, hatch="//",
                                          zorder=2.2, alpha=ag,
                                          mutation_aspect=_ma()))
            S.text_fit(fig, (xm + x1) / 2, y + h / 2, gap_label, ha="center",
                       va="center", color=RED, fontsize=38, max_w=(x1 - xm) * 0.88,
                       zorder=2.4, alpha=ag)
        # 目盛の文字。**empty は端数を持てる**(81歳8か月のような値を丸めない)
        mid_ha, mid_x = "center", xm
        if x1 - xm < 0.26:
            mid_ha, mid_x = "right", xm - 0.012
        mid_lab = empty_label or f"{empty:g}歳"
        ticks = [(f"{start}歳", x0, "left"), (mid_lab, mid_x, mid_ha)]
        # 端の目盛は、まだ塗っていない側があるときだけ出す。
        # empty == end(帯が右端まで届く使い方)では mid が端の目盛を兼ねる
        # (2026-08-29 批評5周目: 旧実装はラベル文字列の一致で伏せていたので、
        #  empty == end のとき「65歳」が mid ごと消えていた)
        if show_gap and empty != end:
            ticks.append((f"{end}歳", x1, "right"))
        for lab, x, ha in ticks:
            tick_x = xm if lab == mid_lab else x
            fig.add_artist(plt.Line2D([tick_x, tick_x], [y - 0.030, y],
                                      transform=fig.transFigure,
                                      color=INK, linewidth=3.0, zorder=2.3))
            S.text_fit(fig, x, y - 0.058, lab, ha=ha, va="center",
                       color=INK, fontsize=40, max_w=0.26, zorder=2.4)
        head_title(fig, title, t)
    return painter


def people(total: int, hit: int, label: str, title: str = ""):
    """人の絵を並べて、割合を数で見せる。**棒より、割合は「何人のうち何人」が速い。**

    total=10 / hit=5 なら、10人のうち5人を赤くする。
    """
    def painter(fig, t):
        card(fig, CARD_L, CARD_BOT, CARD_R - CARD_L, CARD_TOP - CARD_BOT,
             r=0.028, z=2.1)
        # **人数は声とそろえる。**声が「2人に1人」なのに絵が10人中5人だと、
        # 視聴者の頭の中で 5/10 = 1/2 の変換が起きる(2026-08-23のレビュー)
        x0, x1 = 0.10, 0.90
        span = min((x1 - x0) / total, 0.24)      # 人数が少ないときは大きくしすぎない
        left = 0.5 - span * total / 2
        cy = 0.590          # 見出しと頭がぶつからない高さ
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
                                          edgecolor="none", zorder=2.3,
                                          mutation_aspect=_ma()))
        S.text_fit(fig, 0.5, 0.462, F.fmt_disp(label), ha="center", va="center",
                   color=RED, fontsize=52, max_w=0.80, zorder=2.4)
        head_title(fig, title, t)
    return painter


def formula(line: str, note: str = "", name: str = "02_point", answer: str = "",
            title: str = ""):
    """持ち帰る式を1枚。**手順ではなく、その場で使える形**で置く。

    2026-08-29 批評3周目: name=None は**2段組に再設計**。
    - 上段=数式(3,162円 × 360か月)。**被演算数も演算子も墨色**(どれが結論か
      色で迷わせない。同じ赤の羅列は階層ゼロだった)
    - 下段=答え(= 114万円)。**赤・上段の1.6倍・カウントアップ**で、式の
      クライマックスをカード内に立てる。1行の式が高さ300pxのカードの中央に
      浮いて上下60%が空白、も同時に解消(カードが縦に埋まる)
    - answer が無いときは note(「= 30年で出ていく額」)が下段に立つ
    - 着地後は答えが1.8秒周期で鼓動する(0.010の呼吸は知覚閾値未満だった)
    """
    def painter(fig, t):
        fam = [F.NUM_FAMILY]
        fam_w = [F.FONT_FAMILY, F.FONT_FALLBACK_FAMILY]
        if name:
            # 立ち絵つきの旧レイアウト(1行組)。S033では未使用だが互換で残す
            F.draw_pose(fig, name, cx=0.5, top=0.845, height=0.315)
            top, bot = 0.495, 0.320
            fs_num = 60
            sc = 0.88 + 0.12 * _back(t / 0.30)
            card(fig, CARD_L, bot, CARD_R - CARD_L, top - bot, edge=RED, lw=5.0,
                 r=0.028, z=2.2, sc=sc)
            cy = (top + bot) / 2 + (0.030 if note else 0.0)
            toks = [x for x in re.split(r"\s*([÷×+−=])\s*", line.strip()) if x]
            if answer:
                toks += ["=", answer]
            ans_j = len(toks) - 1 if answer else None
            starts = [0.0, 0.20, 0.34, 0.50, 0.62]
            r = _renderer(fig)
            fs_op = fs_num * 0.55
            widths = []
            for tok in toks:
                if tok in "÷×+−=":
                    w = F.measure_w(fig, r, tok, fs_op, fam, F.NUM_WEIGHT) + 0.030
                elif _WORD.match(tok):
                    w = _num_w(fig, r, tok, fs_num)
                else:
                    w = F.measure_w(fig, r, tok, fs_num * 0.72, fam_w, F.FONT_WEIGHT)
                widths.append(w)
            total = sum(widths)
            k = min(1.0, 0.82 / total) if total else 1.0
            x = 0.5 - total * k / 2
            for j, (tok, w) in enumerate(zip(toks, widths)):
                st = 0.62 + (j - ans_j + 1) * 0.10 if (ans_j and j >= ans_j - 1) \
                    else starts[min(j, len(starts) - 1)]
                a = _ease((t - st) / 0.16)
                if a > 0.01:
                    cx_t = x + w * k / 2
                    if tok in "÷×+−=":
                        stamp = 1.0 + 0.5 * (1 - _ease((t - st) / 0.20))
                        fig.text(cx_t, cy, tok, ha="center", va="center", color=INK,
                                 fontsize=fs_op * k * stamp, fontfamily=fam,
                                 fontweight=F.NUM_WEIGHT, zorder=2.4, alpha=a)
                    elif _WORD.match(tok):
                        fs_t = fs_num * k
                        tt = 1.0
                        if j == ans_j:
                            fs_t *= 1.28 - 0.28 * _back((t - st) / 0.22)
                            tt = max(0.0, (t - st) * (0.55 / 0.26))
                            if t > 0.95:
                                fs_t *= beat()
                        big_number(fig, cx_t, cy, tok, fs_t, color=RED,
                                   t=tt, count=(j == ans_j), z=2.4,
                                   max_w=w * k * 1.30 + 0.02, alpha=a)
                    else:
                        fig.text(cx_t, cy, tok, ha="center", va="center", color=INK,
                                 fontsize=fs_num * 0.72 * k, fontfamily=fam_w,
                                 fontweight=F.FONT_WEIGHT, zorder=2.4, alpha=a)
                x += w * k
            if note:
                an = _ease((t - 0.62) / 0.20)
                if an > 0.01:
                    S.text_fit(fig, 0.5, cy - 0.085, note, ha="center", va="center",
                               color=SUB, fontsize=36, max_w=0.78, zorder=2.4,
                               alpha=an)
            head_title(fig, title, t)
            return
        # ---- name=None: 2段組(上段=式・墨 / 下段=答え・赤・1.6倍)
        # 2026-08-29 批評4周目:
        # - 答えの出現を前倒し(0.50→0.36)+それまで答えの定位置に「= ?」を
        #   薄く置く(カード下半分が無地白のまま尺の4割待つ中弛みを消す。
        #   「?」は答えの直前に膨らみながら消え、入れ替わりにスタンプが押される)
        # - answer 無しのときは y1/y2 を詰め、note を式と同じ Black 900・
        #   大きめで立てる(2行が別要素に見える290pxの無地を消す)
        # - 語トークン(月額)も Black 900 に統一(行内で「月額」400と
        #   「360」900が混ざり、数字だけ浮いていた)
        # 2026-08-29 批評5周目: 上下段の間が約292px空いて「=」が孤立し、
        # 答えの下にも約190pxの無地が残っていた。2段を(0.672, 0.558)へ詰めて
        # ブロックをカード中央(cy≈0.615)に置き、answer 無しのカードは
        # 下辺を内容に追従させる(bot 0.45→0.475)
        top = CARD_TOP
        bot = 0.45 if answer else 0.475
        y1, y2 = (0.672, 0.558) if answer else (0.680, 0.585)
        sc = 0.88 + 0.12 * _back(t / 0.30)
        card(fig, CARD_L, bot, CARD_R - CARD_L, top - bot, edge=RED, lw=5.0,
             r=0.028, z=2.2, sc=sc)
        fs1 = 64.0
        fs_op = fs1 * 0.60
        toks = [x for x in re.split(r"\s*([÷×+−=])\s*", line.strip()) if x]
        starts = [0.02, 0.16, 0.28, 0.38, 0.46]
        r = _renderer(fig)
        widths = []
        for tok in toks:
            if tok in "÷×+−=":
                w = F.measure_w(fig, r, tok, fs_op, fam, F.NUM_WEIGHT) + 0.034
            elif _WORD.match(tok):
                w = _num_w(fig, r, tok, fs1)
            else:
                w = F.measure_w(fig, r, tok, fs1 * 0.82, fam, F.NUM_WEIGHT)
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
                    fig.text(cx_t, y1, tok, ha="center", va="center", color=INK,
                             fontsize=fs_op * k * stamp, fontfamily=fam,
                             fontweight=F.NUM_WEIGHT, zorder=2.4, alpha=a)
                elif _WORD.match(tok):
                    big_number(fig, cx_t, y1, tok, fs1 * k, color=INK,
                               t=1.0, count=False, z=2.4,
                               max_w=w * k + 0.02, alpha=a)
                else:
                    fig.text(cx_t, y1, tok, ha="center", va="center", color=INK,
                             fontsize=fs1 * 0.82 * k, fontfamily=fam,
                             fontweight=F.NUM_WEIGHT, zorder=2.4, alpha=a)
            x += w * k
        # 下段: 答え(または note)。式の1.6倍・赤。カードの下半分を埋める
        st2 = 0.36
        a2 = _ease((t - st2) / 0.16)
        if answer and t < st2 + 0.04:
            # 答えの予告「= ?」。1行目の着地直後から定位置でふわっと待ち、
            # スタンプ開始で即座に退場する(次に何かが起こる予告を絶やさない。
            # 2026-08-29 批評4周目。退場を引き延ばすと答えと二重写しになる)
            aq = _ease((t - 0.16) / 0.14) * 0.35
            qs = 1.0
            if t >= st2:
                uo = (t - st2) / 0.04
                qs = 1.0 + 0.30 * uo
                aq *= max(0.0, 1.0 - uo)
            if aq > 0.01:
                fig.text(0.5, y2 + 0.005 * idle(period=0.9), "= ?",
                         ha="center", va="center", color=SUB,
                         fontsize=fs1 * 1.1 * qs, fontfamily=fam,
                         fontweight=F.NUM_WEIGHT, zorder=2.35, alpha=aq)
        if answer and a2 > 0.01:
            fs2 = fs1 * 1.6
            w_eq = F.measure_w(fig, r, "=", fs2 * 0.55, fam, F.NUM_WEIGHT) + 0.042
            w_ans = _num_w(fig, r, answer, fs2)
            k2 = min(1.0, 0.74 / (w_eq + w_ans))
            pop = 1.22 - 0.22 * _back((t - st2) / 0.24)
            b = beat() if t > 0.85 else 1.0
            # **答えは上段の式と同じ中心線(x=0.5)に載せ、「=」はその左に
            # ぶら下げる**(2026-08-29 批評5周目。「=+答え」を塊で中央寄せすると
            # 答えの軸が式の軸からずれ、等式が1つの視線移動で読めなかった)
            ans_cx = 0.5
            fig.text(ans_cx - w_ans * k2 / 2 - (w_eq - 0.042 / 2) * k2 / 2, y2, "=",
                     ha="center", va="center",
                     color=INK, fontsize=fs2 * 0.55 * k2, fontfamily=fam,
                     fontweight=F.NUM_WEIGHT, zorder=2.4, alpha=a2)
            big_number(fig, ans_cx, y2, answer,
                       fs2 * k2 * pop * b, color=RED,
                       t=max(0.0, (t - st2) * 2.2), count=True, z=2.4,
                       max_w=w_ans * k2 * 1.35 + 0.02, alpha=a2)
        elif note and a2 > 0.01:
            # answer が無い式(月額 × 360か月)は note が下段に立つ。
            # 【】の語は赤(他の shiki の「答え=赤・大」と同じ視線誘導)。
            # 書体は式と同じ Black 900 の1種に固定する
            b = beat(amp=0.020) if t > 0.85 else 1.0
            segs = S.parse_rich(F.fmt_disp(note))
            fs_n = fs1 * 1.1 * b
            sizes = [fs_n * (1.3 if em else 1.0) for _s2, em in segs]
            wsn = [F.measure_w(fig, r, s2, fz, fam, F.NUM_WEIGHT)
                   for (s2, _e), fz in zip(segs, sizes)]
            kn = min(1.0, 0.80 / sum(wsn)) if sum(wsn) else 1.0
            xn = 0.5 - sum(wsn) * kn / 2
            pop_n = 1.15 - 0.15 * _back((t - st2) / 0.22)
            for (s2, em), fz, wn in zip(segs, sizes, wsn):
                fig.text(xn + wn * kn / 2, y2, s2, ha="center", va="center",
                         color=(RED if em else INK),
                         fontsize=fz * kn * (pop_n if em else 1.0),
                         fontfamily=fam, fontweight=F.NUM_WEIGHT,
                         zorder=2.4, alpha=a2)
                xn += wn * kn
        if answer and note:
            an = _ease((t - 0.70) / 0.20)
            if an > 0.01:
                S.text_fit(fig, 0.5, bot + 0.040, note, ha="center", va="center",
                           color=SUB, fontsize=30, max_w=0.78, zorder=2.4, alpha=an)
        head_title(fig, title, t)
    return painter


def bars(items, highlight=None, title="", ymax=None, prev_highlight=None,
         tease=None, gain=None, ghost=None):
    """棒。items = [(見出し, 値, 棒の上の語句), ...]

    ghost = [(値, ラベル) or None, ...](スロット順)。前のカットの棒を
    破線の輪郭で背後に残す(2026-08-29 批評5周目: hitotsu2 は目盛を
    263万に揃えた結果、90万の棒がカード内高の1/3でスカスカに見えた。
    参照物=「さっきの263万円」を薄く置けば、空いた高さが比較として意味を持つ)。
    いちばん高いゴーストの高さには破線の水平参照線を1本引く。

    2026-08-29: 裸の ax.bar をやめて figure 座標で自前描画。
    - 白パネルに載せ、基線(INK)を引き、上角を角丸にする
    - 伸長は ease_out_back(6%オーバーシュートして戻る)
    - 値ラベルは棒の頭に密着してカウントアップ。強調棒は極太60pt赤
    - prev_highlight を渡すと、赤がその棒からクロスフェードで移動する

    2026-08-29 批評3周目:
    - tease=添字: その棒を**予告扱い**にする(破線の輪郭のみ+値は「?」)。
      「積んだらどうなるか」と問うカットで答えの263万円が満尺で立っていた。
      高さは本物のまま=形は見えるが数字は伏せる(むしろ引きが強い)
    - gain=添字: その棒が強調されたとき**緑(増える側の色)**にする。
      出ていく114万も増える263万も同じ赤で、売り物に固有の色が無かった
    - 伸長・カウントの窓 0.55→0.72(着地が早すぎて伸びる棒を見られる時間が
      1/3しか無かった)。着地後は値ラベル±2.5%+棒の頭±0.3%が同位相で呼吸
    """
    vals = [v for _, v, _ in items]
    topval = ymax or max(vals) * 1.22
    n = len(items)
    WIN = 0.72
    def painter(fig, t):
        card(fig, CARD_L, CARD_BOT, CARD_R - CARD_L, CARD_TOP - CARD_BOT,
             r=0.028, z=2.0)
        x0i, x1i = 0.16, 0.84
        y0, y1 = 0.475, 0.700
        slot = (x1i - x0i) / n
        bw = slot * 0.60
        # **棒の伸長とカウントは同じ窓で着地させる**(2026-08-29 批評2周目)
        p = _back(t / WIN)
        fam = [F.NUM_FAMILY]
        # ゴースト棒(前カットの値)。破線の輪郭+薄いラベル+水平参照線
        if ghost:
            ag = _ease((t - 0.10) / 0.25)
            if ag > 0.01:
                for gi, gv in enumerate(ghost):
                    if not gv or gi >= n:
                        continue
                    gval, glab = gv
                    gh_ = (gval / topval) * (y1 - y0)
                    cxg = x0i + slot * (gi + 0.5)
                    grs = min(0.012, gh_ * 0.45)
                    fig.add_artist(FancyBboxPatch(
                        (cxg - bw / 2, y0), bw, gh_,
                        boxstyle=f"round,pad=0,rounding_size={grs:.4f}",
                        transform=fig.transFigure, facecolor="none",
                        edgecolor=WARM_GRAY, linewidth=2.5,
                        linestyle=(0, (4, 3)), zorder=2.05, alpha=0.55 * ag,
                        mutation_aspect=_ma()))
                    if glab:
                        fig.text(cxg, y0 + gh_ + 0.006, F.fmt_disp(glab),
                                 ha="center", va="bottom", color=WARM_GRAY,
                                 fontsize=30, fontfamily=fam,
                                 fontweight=F.NUM_WEIGHT, zorder=2.06,
                                 alpha=0.8 * ag)
                gmax = max(gv[0] for gv in ghost if gv)
                ygl = y0 + (gmax / topval) * (y1 - y0)
                fig.add_artist(plt.Line2D([x0i - 0.02, x1i + 0.02], [ygl] * 2,
                                          transform=fig.transFigure,
                                          color=WARM_GRAY, linewidth=2.0,
                                          linestyle=(0, (5, 4)), zorder=2.05,
                                          alpha=0.5 * ag))

        def mix(c1, c2, u):
            from matplotlib.colors import to_rgba
            a, b = to_rgba(c1), to_rgba(c2)
            return tuple(a[i] * (1 - u) + b[i] * u for i in range(4))

        def bar_color(idx, hl_idx):
            # 役割ベース(2026-08-29 批評4周目): gain の文法があるカットでは、
            # 損側の棒は非強調でも褪せた赤(RED_FADE)を返す。同じ114万円が
            # カットごとに赤→灰と色を変え、同一性が切れて見えていた。
            # gain 未指定の図(役割の文法が無い比較)は従来どおり WARM_GRAY
            if hl_idx == idx:
                return GREEN if gain == idx else RED_FILL
            if gain is not None and gain != idx:
                return RED_FADE
            return WARM_GRAY

        for i, (lab, v, note) in enumerate(items):
            cx = x0i + slot * (i + 0.5)
            hl_now = (highlight == i)
            teased = (tease == i)
            col = bar_color(i, highlight)
            if prev_highlight is not None and prev_highlight != highlight:
                u = _ease(t / 0.35)
                col = mix(bar_color(i, prev_highlight), col, u)
            h = (v / topval) * (y1 - y0) * p
            if hl_now and t >= WIN:
                h *= 1.0 + 0.003 * idle(period=0.9)   # 頭がラベルと同位相で揺れる
            if teased and h > 0.004:
                # 予告棒: 破線の輪郭のみ(面は塗らない)。数字は下で「?」になる
                rs = min(0.012, h * 0.45)
                fig.add_artist(FancyBboxPatch(
                    (cx - bw / 2, y0), bw, h,
                    boxstyle=f"round,pad=0,rounding_size={rs:.4f}",
                    transform=fig.transFigure, facecolor="none",
                    edgecolor=WARM_GRAY, linewidth=3.5,
                    linestyle=(0, (5, 3)), zorder=2.1, mutation_aspect=_ma()))
            elif h > 0.004:
                # 上角だけ角丸+カードと同じ落ち影。
                # 影は**基線(y0)から上だけ**に落とす(2026-08-29 批評5周目:
                # 影パッチが y0-0.004 始まりで、地面の線の下に丸い塊が
                # 突き抜けていた=地面に立つ棒の影が地面を貫通する物理破綻)。
                # drop_shadow の clip_y で基線より下を描かない
                rs = min(0.012, h * 0.45)
                drop_shadow(fig, cx - bw / 2, y0, bw, h, r=rs, z=2.08, clip_y=y0)
                fig.add_artist(FancyBboxPatch(
                    (cx - bw / 2, y0), bw, h,
                    boxstyle=f"round,pad=0,rounding_size={rs:.4f}",
                    transform=fig.transFigure, facecolor=col,
                    edgecolor="none", zorder=2.1, mutation_aspect=_ma()))
                # 下角の丸みは矩形で埋めて「上角だけ丸い棒」にする
                fig.add_artist(plt.Rectangle((cx - bw / 2, y0), bw, min(h, rs * 1.2),
                                             transform=fig.transFigure, facecolor=col,
                                             edgecolor="none", zorder=2.1))
            # 値ラベル: 棒の頭に密着してカウントアップ(棒の頂点到達と同フレーム)
            m = _NUM_RE.match(note or "")
            if teased:
                shown = "?"
            elif m:
                pre, digits, suf = m.groups()
                val = int(round(int(digits) * _ease(t / WIN)))
                if t >= WIN:
                    val = int(digits)
                shown = pre + (f"{val:,}" if len(digits) >= 4 else str(val)) + suf
            else:
                shown = note
            # 値ラベルは棒トップに詰める(0.012≈23pxの空隙で帰属が一瞬迷う。
            # 2026-08-29 批評4周目: 棒トップ+約10pxに固定。追従は現行のまま)
            y_v = y0 + h + 0.005
            if teased:
                # 予告の「?」: 数値ラベルと同級の64pt・濃色でどっしり置く
                # (40pt・薄灰では左の赤ラベルと釣り合わず、目に入らなかった)
                fs_q = 64.0 * (1.0 + 0.030 * max(0.0, idle(period=1.1)))
                fig.text(cx, y_v, "?", ha="center", va="bottom", color=SUB,
                         fontsize=fs_q, fontfamily=fam,
                         fontweight=F.NUM_WEIGHT, zorder=2.4)
            elif hl_now:
                fs_v = 60.0
                if t > WIN:         # 着地後の呼吸(完全静止を作らない)
                    fs_v *= 1.0 + 0.025 * idle(period=0.9)
                v_col = GREEN_DARK if gain == i else RED
                fig.text(cx, y_v, F.fmt_disp(shown), ha="center",
                         va="bottom", color=v_col, fontsize=fs_v, fontfamily=fam,
                         fontweight=F.NUM_WEIGHT, zorder=2.4,
                         path_effects=_halo(60))
            else:
                # 非強調の級数 36→44(最大値の棒に最小の文字、の逆転を緩和)
                fig.text(cx, y_v, F.fmt_disp(shown), ha="center",
                         va="bottom", color=SUB, fontsize=44, fontfamily=fam,
                         fontweight=F.NUM_WEIGHT, zorder=2.4)
            S.text_fit(fig, cx, y0 - 0.020, lab, ha="center", va="top", color=INK,
                       fontsize=36, max_w=slot * 0.96, zorder=2.4)
        # 基線(地面)
        fig.add_artist(plt.Line2D([x0i - 0.02, x1i + 0.02], [y0] * 2,
                                  transform=fig.transFigure, color=INK,
                                  linewidth=3.5, zorder=2.3))
        head_title(fig, title, t)
    return painter


def hero(main: str, sub: str = "", name: str = "01_base", stamp: bool = False,
         caption: str = "", role: str = "loss", count: bool = True):
    """大きい数字を1つ。**キャラを上、数字を白いカードで下**に置く。

    name=None にすると数字だけになる(figure が主役の場面用)。
    カード枠の規約: **結論カード=赤(formula)、途中経過=ベージュ(hero)**。

    2026-08-29 批評3周目の改修(name=None のとき):
    - **fs=165固定をやめ、カード内幅78%まで自動拡大**(上限は高さから逆算)。
      「105円」のような短い文字列がカードの25%しか占めず、白い虚空だった
    - caption: カード内・数字の直下の補助行(「あくまで仮定。元本保証では
      ありません」等を注記帯から降ろす受け皿。注記帯は全ユニット1行に保つ)
    - 着地後は 1.8秒周期の鼓動(0.010の呼吸は200px級で約2px=静止に見えた)

    2026-08-29 批評4周目: role("loss"|"gain"|"neutral")を追加。
    赤(RED)は損・警告の色なのに「大きい数字なら何でも赤」に戻っていた。
    増える側の仮定(年5%)は GREEN_DARK、中立な期間(360か月)は INK。

    2026-08-29 批評5周目:
    - count=False: **既に開示済みの数字を数え直さない**(答えを知っている数を
      1.5秒かけて再発表すると情報密度がゼロになる)。数字は即置きで、
      カードのポップと着地後の鼓動が動きを担う
    - fs 上限 0.60→0.70・max_w 0.78→0.84(数字1つがカード内高の35%しか
      占めず「大きな白い長方形の中の1語」が4カット続いていた)
    - caption の無い name=None のヒーローはカード高を82%に縮めて中央に置く
    """
    hero_col = {"gain": GREEN_DARK, "neutral": INK}.get(role, RED)
    def painter(fig, t):
        if name:
            # バッジ(y≈0.876)より下から。上に出すと打消し表示が髪で隠れる
            F.draw_pose(fig, name, cx=0.5, top=0.845, height=0.395)
            top, bot = 0.450, 0.285
            fs = 150
            head = 0.036 if sub else 0.0
            if sub:
                a = _ease((t - 0.15) / 0.2)
                S.text_fit(fig, 0.5, top - 0.034, F.fmt_disp(sub), ha="center",
                           va="center", color=SUB, fontsize=34, max_w=0.74,
                           zorder=2.4, alpha=a)
        else:
            top, bot = CARD_TOP, CARD_BOT
            if not caption:
                # 短い1語のヒーローは、カード高を82%に縮めて中央に置く
                # (充填率を上げる。2026-08-29 批評5周目)
                sq = (CARD_TOP - CARD_BOT) * 0.09
                top, bot = top - sq, bot + sq
            # 数字はカードを圧するまで拡大: 幅は big_number が max_w で締めるので、
            # ここでは**高さからの上限**だけ決める(カード内高の約70%)
            fs = min(280.0, (top - bot) * 0.70 * S.H * 72 / S.DPI)
            head = 0.0
            # 文脈見出しはカードの外(上の帯を埋め、視線アンカーを揃える)
            head_title(fig, sub, t)
        sc = 0.85 + 0.15 * _back(t / 0.30)
        dx = 0.0
        if stamp and 0.32 < t < 0.55:
            # スタンプ着地の瞬間だけカードを微シェイク
            dx = 0.003 * math.sin(40.0 * t) * (1.0 - _ease((t - 0.32) / 0.23))
        card(fig, CARD_L + dx, bot, CARD_R - CARD_L, top - bot, r=0.028,
             z=2.2, sc=sc)
        cy = (top - head + bot) / 2
        if caption and not name:
            cy += 0.026
            ac = _ease((t - 0.45) / 0.20)
            if ac > 0.01:
                S.text_fit(fig, 0.5, bot + 0.062, F.fmt_disp(caption), ha="center",
                           va="center", color=INK, fontsize=34, max_w=0.78,
                           zorder=2.4, alpha=ac)
        # 鼓動は fs と max_w を同率で伸ばす(幅いっぱいの数字でも脈が見える)
        b = beat() if t > 0.60 else 1.0
        if stamp:
            p = _back((t - 0.10) / 0.28)
            if p <= 0.01:
                return
            fs_t = fs * (1.5 - 0.5 * p) * b
            # スタンプでも数字部分は短いカウント(窓0.25)で駆け上がる
            # (2026-08-29 批評4周目: katei はカウントが無く、ポップ後は
            # 鼓動だけで相対的に最も静的に写っていた)
            big_number(fig, 0.5 + dx, cy, main, fs_t,
                       color=hero_col, t=max(0.0, (t - 0.10) * 2.2), count=count,
                       z=2.4, max_w=0.84 * b,
                       alpha=_ease((t - 0.10) / 0.14))
        else:
            big_number(fig, 0.5, cy, main, fs * b, color=hero_col,
                       t=t if count else 1.0, count=count, z=2.4, max_w=0.84 * b)
    return painter


def arrow(left_val: str, right_val: str, left_lab: str = "", right_lab: str = "",
          title: str = "", scale_right: float = 1.0, role: str = "loss",
          accent: str = "right", arrow_color: str = INK):
    """左の額 → 右の額。**同じお金が別のものに変わる**ことを1枚で見せる。

    2026-08-29 批評3周目の再設計:
    - **全部品共通の白カードに載せる**(この3カットだけ地紋直置きで、カット
      切替のたびに背景の質感が白→ドット→白と明滅していた)
    - 左右の箱はサイズ差があっても **cy(カード中心)で垂直センタリング**。
      矢印も cy に固定(どちらの箱の中心線にも乗っていなかった)
    - ラベルは箱下端でなく**カード下端からの共通ベースライン**に置く
    - 右の数字は左の約1.3倍(級数の手がかり)。scale_right は箱の拡大率
    - role="gain": 右を緑(増える側の固有色)。loss: 赤。赤の意味過積載を解く
    - accent="arrow": 右箱を非強調(ベージュ縁+墨字)にする。矢印の強調は
      **色ではなく太さ**(1.3倍)で表す(2026-08-29 批評5周目: 方向記号の
      既定色を INK に統一。中立な時間遷移だけが赤い矢印を持ち、
      赤=出ていく側の意味系が逆転していた)
    - 因果順で動く: 左箱 → 矢印が伸びる(0.28秒ドローオン)→ 右箱 →
      その0.12以内に数字がポップ(空の赤枠が長く待たない)
    """
    def painter(fig, t):
        head_title(fig, title, t)
        card(fig, CARD_L, CARD_BOT, CARD_R - CARD_L, CARD_TOP - CARD_BOT,
             r=0.028, z=2.0)
        cy = (CARD_TOP + CARD_BOT) / 2 + 0.026    # 下にラベルの共通ベースライン
        hi_edge = GREEN if role == "gain" else RED
        hi_ink = GREEN_DARK if role == "gain" else RED
        wl, hb = 0.30, 0.185
        # 語トークン(左右とも数字を含まない)は箱を低くし、語を箱幅80%まで
        # 拡大する(2026-08-29 批評4周目: 「出ていく」約40ptが200px級の箱で
        # 泳ぎ、数字カットと同じ部品なのに充填率が半分以下だった)
        is_word = not _WORD.match(left_val) and not _WORD.match(right_val)
        if is_word:
            hb, wl = 0.13, 0.34      # 低く・広く(語の字数に容器を合わせる)
            cy -= 0.020              # 箱+直下ラベルの塊をカード中央に置き直す
        wr, hr = wl * scale_right, hb * scale_right
        xl = 0.075 if is_word else 0.095
        xr = (0.925 if is_word else 0.905) - wr
        emph = accent != "arrow"
        if is_word:
            # big_number の非数字パスは fs*0.72 で描く。箱の短辺の約58%を
            # 目標高さに、幅80%でクランプ。**左右で同じ級数を共有する**
            fs_h = (hb * 0.58) * S.H * 72.0 / S.DPI / 0.72
            fs_l = min(_fit_num_fs(fig, left_val, fs_h, wl * 0.80),
                       _fit_num_fs(fig, right_val, fs_h, wr * 0.80))
            fs_r = fs_l
        else:
            # 右の数字の級数を先に決め、左はその 1/1.3(比較の答えを書体で語らせる)
            fs_r = _fit_num_fs(fig, right_val, 108.0, wr - 0.05)
            fs_l = (fs_r / 1.3) if emph else min(fs_r,
                                                 _fit_num_fs(fig, left_val, fs_r,
                                                             wl - 0.05))
            if not emph:
                fs_r = fs_l
        # 左箱。role="gain" のとき左は損側の実体なので、非強調でも赤の気配
        # (褪せた赤の縁・文字)を残す(赤=出ていく側、の文法を切らさない)
        l_edge, l_ink = ((LOSS_EDGE, LOSS_INK) if role == "gain"
                         else (CARD_EDGE_STRONG, SUB))
        a_l = _ease(t / 0.16)
        card(fig, xl, cy - hb / 2, wl, hb, edge=l_edge, lw=4.0,
             r=0.022, z=2.2, alpha=a_l)
        big_number(fig, xl + wl / 2, cy + 0.008, left_val, fs_l, color=l_ink,
                   t=1.0, count=False, z=2.4, max_w=wl * 0.80 if is_word
                   else wl - 0.05, alpha=a_l)
        # 矢印: 左箱の着地後、左→右へドローオン(先端の比率は崩れない)
        x0, x1 = xl + wl + 0.012, xr - 0.012
        u = _ease((t - 0.16) / 0.28)
        # 右箱: 矢先の到達(見た目上 t≈0.33)と同時にポップを始め、
        # **0.10以内に数字**が入る(2026-08-29 批評4周目: 矢印が完成済みなのに
        # 右箱不在=矢印が空白を指す静止フレームが約14%の窓で出ていた)
        pr = _back((t - 0.34) / 0.20)
        pulse = math.sin(math.pi * min(1.0, max(0.0, (t - 0.34) / 0.28)))
        if pr > 0.01:
            lw_r = 4.0 + 3.0 * pulse
            if t > 0.80:
                lw_r = 4.0 + 1.5 * (0.5 + 0.5 * idle(period=0.8))
            if emph:
                card(fig, xr, cy - hr / 2, wr, hr, edge=hi_edge, lw=lw_r,
                     r=0.022, z=2.2, sc=min(1.0, pr) + 0.04 * pulse)
            else:
                card(fig, xr, cy - hr / 2, wr, hr, edge=CARD_EDGE_STRONG, lw=4.0,
                     r=0.022, z=2.2, sc=min(1.0, pr))
            a_r = _ease((t - 0.44) / 0.12)
            if a_r > 0.01:
                pop = 1.18 - 0.18 * _back((t - 0.44) / 0.18)
                b = beat() if t > 0.85 else 1.0
                big_number(fig, xr + wr / 2, cy + 0.008, right_val,
                           fs_r * pop * b, color=(hi_ink if emph else INK),
                           t=1.0, count=False, z=2.4,
                           max_w=(wr * 0.80 * 1.20) if is_word
                           else (wr - 0.05) * 1.20, alpha=a_r)
        # ラベル: 数値版はカード下端からの共通ベースライン(箱の高さ差で
        # ずらさない)。**語トークン版は各箱の直下**(2026-08-29 批評5周目:
        # 箱を低くしたのに共通ベースラインのままで、箱とラベルの間に
        # 約200pxの断絶があり、ラベルの帰属が切れていた)
        for x0b, wb, hbx, lab, al in ((xl, wl, hb, left_lab, a_l),
                                      (xr, wr, hr, right_lab,
                                       _ease((t - 0.44) / 0.14))):
            if lab and al > 0.01:
                y_lab = (cy - hbx / 2 - 0.045) if is_word else (CARD_BOT + 0.052)
                S.text_fit(fig, x0b + wb / 2, y_lab, lab, ha="center",
                           va="center", color=SUB, fontsize=38, max_w=wb + 0.04,
                           zorder=2.4, alpha=al)
        # 矢印本体(常に cy に乗る)。既定色は INK(方向記号は無彩の墨。
        # 赤=出ていく側/緑=増える側の役割色を方向記号に流用しない)
        if u > 0.02:
            xe = x0 + (x1 - x0) * u
            if t > 0.80:
                xe += 0.004 * idle(period=0.7)
            hl_, hw, sh = 0.045, 0.042, 0.014
            if accent == "arrow":
                # 矢印が主役のカットの強調は太さで(色は変えない)
                hl_, hw, sh = hl_ * 1.3, hw * 1.3, sh * 1.3
            xs = max(x0, xe - hl_)
            fig.add_artist(plt.Polygon(
                [[x0, cy - sh], [xs, cy - sh], [xs, cy - hw], [xe, cy],
                 [xs, cy + hw], [xs, cy + sh], [x0, cy + sh]],
                transform=fig.transFigure, facecolor=arrow_color, edgecolor="none",
                zorder=2.5, closed=True))
    return painter


def compare(left_val: str, right_word: str, left_lab: str = "",
            right_lab: str = "", title: str = ""):
    """左=数字、右=比較対象(語)の並置比較。あいだに「<」を置く。

    2026-08-29 批評5周目: 「缶コーヒーより安い」と言うのに比較対象の絵が無く、
    直前のヒーロー数字の再掲になっていた。右カードが ease_back でポップインし、
    「<」がスタンプされる(比較対象の出現がこのカットの動きの主役)。
    値の無い対象(缶コーヒー)に価格は書かない(出典の無い数字を画面に出さない)。
    """
    def painter(fig, t):
        head_title(fig, title, t)
        card(fig, CARD_L, CARD_BOT, CARD_R - CARD_L, CARD_TOP - CARD_BOT,
             r=0.028, z=2.0)
        cy = (CARD_TOP + CARD_BOT) / 2 + 0.016
        wl, hb = 0.34, 0.16
        xl, xr = 0.085, 0.915 - wl
        # 左(数字)は即置き。開示済みの数字なのでカウントしない
        a_l = _ease(t / 0.16)
        fs_l = _fit_num_fs(fig, left_val, 96.0, wl - 0.06)
        card(fig, xl, cy - hb / 2, wl, hb, edge=CARD_EDGE_STRONG, lw=4.0,
             r=0.022, z=2.2, alpha=a_l)
        big_number(fig, xl + wl / 2, cy + 0.006, left_val, fs_l, color=INK,
                   t=1.0, count=False, z=2.4, max_w=wl - 0.06, alpha=a_l)
        # 「<」: 比較の向き(左のほうが小さい)。0.30でスタンプ
        a_m = _ease((t - 0.30) / 0.14)
        if a_m > 0.01:
            stamp = 1.0 + 0.5 * (1 - _ease((t - 0.30) / 0.20))
            fig.text(0.5, cy, "<", ha="center", va="center", color=INK,
                     fontsize=64 * stamp, fontfamily=[F.NUM_FAMILY],
                     fontweight=F.NUM_WEIGHT, zorder=2.4, alpha=a_m)
        # 右(比較対象の語)がポップイン=このカットの主役の動き
        pr = _back((t - 0.40) / 0.22)
        if pr > 0.01:
            a_r = _ease((t - 0.40) / 0.14)
            b = beat() if t > 0.85 else 1.0
            card(fig, xr, cy - hb / 2, wl, hb, edge=CARD_EDGE_STRONG, lw=4.0,
                 r=0.022, z=2.2, sc=min(1.0, pr))
            fs_r = _fit_num_fs(fig, right_word, 96.0, wl - 0.08)
            big_number(fig, xr + wl / 2, cy + 0.006, right_word, fs_r * b,
                       color=INK, t=1.0, count=False, z=2.4,
                       max_w=(wl - 0.08) * 1.1, alpha=a_r)
        # ラベルは各箱の直下
        for x0b, lab, al in ((xl, left_lab, a_l),
                             (xr, right_lab, _ease((t - 0.46) / 0.14))):
            if lab and al > 0.01:
                S.text_fit(fig, x0b + wl / 2, cy - hb / 2 - 0.042, lab,
                           ha="center", va="center", color=SUB, fontsize=36,
                           max_w=wl + 0.04, zorder=2.4, alpha=al)
    return painter


def cta(line: str, name: str = "02_point", show_button: bool = False,
        show_comment: bool = False, bubble: str = "月いくら?"):
    """締めの定型カット。競合は結論のあと**4カット**使っていた。

    2026-08-29: ボタン・吹き出しは ease_out_back で着地したあと呼吸パルス。
    「コメント」の吹き出しはキャラの頭の横に置き、しっぽを画面右下
    (コメント欄アイコンの方向)へ向ける。字幕の真上には置かない。
    2026-08-29 批評3周目: 呼吸を動画内時刻(idle)で回す(tだと尺の後半で
    止まる)。「コメント」バッジは0.9秒周期のスケールパルスでタップ対象と示す。
    """
    def painter(fig, t):
        F.draw_pose(fig, name, cx=0.40 if show_comment else 0.5, top=0.855,
                    height=0.40 if show_comment else 0.44)
        breath = 1.0 + 0.020 * idle(period=1.3)
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
            # 吹き出しの中身は画面の問いと呼応する「月いくら?」。
            # 「コメント」は機能表示なのでバッジ状の小ラベルに格下げ(2026-08-29
            # 批評2周目)。しっぽは**話者(左の立ち絵の顔)へ向ける**。右下の
            # 何もない空間を指していて、話者から切り離れて見えていた
            p = _back((t - 0.15) / 0.25)
            if p > 0.01:
                s = p * breath
                bx, by, bw, bh = 0.55, 0.615, 0.37, 0.082
                # 吹き出しは±2px級の縦揺れも足す(最後のカットこそ動かす。
                # 2026-08-29 批評4周目: t0.40以降ほぼ静止していた)
                cxb = bx + bw / 2
                cyb = by + bh / 2 + 0.002 * idle(period=1.1)
                bw2, bh2 = bw * s, bh * s
                tail = plt.Polygon(
                    [[cxb - bw2 * 0.34, cyb + bh2 * 0.45],
                     [cxb - bw2 * 0.12, cyb + bh2 * 0.45],
                     [cxb - bw2 * 0.52, cyb + bh2 * 0.45 + 0.058 * s]],
                    transform=fig.transFigure, facecolor=CARD,
                    edgecolor=CARD_EDGE_STRONG, linewidth=4.0, zorder=2.5,
                    joinstyle="miter")
                fig.add_artist(tail)
                fig.add_artist(FancyBboxPatch(
                    (cxb - bw2 / 2, cyb - bh2 / 2), bw2, bh2,
                    boxstyle="round,pad=0,rounding_size=0.030",
                    transform=fig.transFigure, facecolor=CARD,
                    edgecolor=CARD_EDGE_STRONG, linewidth=4.0, zorder=2.55,
                    mutation_aspect=_ma()))
                # 本体上辺の枠線を、しっぽの内側だけ面色で消す(接合部の
                # ノッチを消して輪郭を1本に繋げる。person_bubble と同じ処置)
                yE = cyb + bh2 / 2
                fig.add_artist(plt.Rectangle(
                    (cxb - 0.346 * bw2, yE - 0.0035),
                    0.168 * bw2, 0.0070,
                    transform=fig.transFigure, facecolor=CARD,
                    edgecolor="none", zorder=2.56))
                S.text_fit(fig, cxb, cyb, F.fmt_disp(bubble), ha="center",
                           va="center", color=F.BAND_INK, fontsize=46 * s,
                           max_w=0.32, zorder=2.6)
                # 機能ラベル「コメント」: 吹き出し**左下**の小さいバッジ。
                # 右下アンカーだと右端が x≈0.93 に達し、Shorts実機の右レール
                # UI(いいね/コメント/共有)に食われる(2026-08-29 批評4周目)。
                # **x>0.888(右120px)にはインタラクティブ要素を置かない。**
                # タップ対象であることは 1.6秒周期のスケール鼓動で示す
                # ピルの色はブランドの帯文字色(BAND_INK)+クリーム文字に接続
                # (2026-08-29 批評5周目: 黒充填チップはシステム内唯一の一点物
                # だった)。角丸もカード系の 0.022 に揃える
                sb = s * beat(period=1.6, amp=0.05)
                chw, chh = 0.155 * sb, 0.042 * sb
                chx, chy = cxb - bw2 / 2, cyb - bh2 / 2 - chh * 0.55
                chx = min(chx, 0.82 - chw)
                fig.add_artist(FancyBboxPatch(
                    (chx, chy), chw, chh,
                    boxstyle="round,pad=0,rounding_size=0.022",
                    transform=fig.transFigure, facecolor=F.BAND_INK,
                    edgecolor="none", zorder=2.58, mutation_aspect=_ma()))
                S.text_fit(fig, chx + chw / 2, chy + chh / 2, "コメント",
                           ha="center", va="center", color=F.CREAM,
                           fontsize=26 * sb, max_w=chw * 0.9, zorder=2.6)
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
