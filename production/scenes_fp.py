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
from matplotlib.patches import Ellipse, FancyBboxPatch, PathPatch
import matplotlib.patheffects as path_effects

import fplib as F
import shortlib as S

# ---- 配色(ブランドの1セットに集約。ここ以外で色を直書きしない)
#
# **赤は1色相・3段のラダー**(2026-08-30 artdirection/high)。
# 実測で赤が5値(#b32020 / #9a3834 / #b66056 / #bc7968 / #834d46)に散り、
# S値 .82〜.45・色相 0〜12°で揺れていた。決定的だったのは 13_fueru で、
# 同じ「114万円/ただ貯める」の棒のラベル(#9a3834)と面(#bc7968)が
# 明度で30段離れ、ラベルと対象物が別物の赤になっていたこと。
# 以後、褪せは _mix(別色との混合=色相が動く)ではなく **HSV の S だけを落とす**。
RED = "#b32020"            # ブランドの赤(文字・線・枠)。#e03131 は全廃
RED_FILL = "#c0392b"       # 棒など「面」の赤(文字の赤より一段明るく)
RED_SOFT = "#f9e6dc"       # ハイライト行の地。#fbeae6 は白寄りの桃色に見えた →
                           # 赤をわずかに橙へ回した暖色ティント(2026-08-29 批評2周目)
INK = F.INK_DARK


def _hsv(base: str, s_mul: float = 1.0, v_mul: float = 1.0) -> str:
    """base の**色相を固定したまま**彩度・明度だけ動かす(赤のラダー生成用)。"""
    import colorsys
    from matplotlib.colors import to_rgb, to_hex
    h, s, v = colorsys.rgb_to_hsv(*to_rgb(base))
    return to_hex(colorsys.hsv_to_rgb(h, min(1.0, s * s_mul), min(1.0, v * v_mul)))
SUB = "#6b6459"            # 副テキスト(暖色グレー)
WARM_GRAY = "#b9ae99"      # 非強調の図形の面。青みグレー(#9aa0a6等)は全廃
CARD = F.CARD              # カードの白(#fffdf7)。純白は文字専用
CARD_TINT = "#fdf6e8"      # カード上端のトップライト(card() の縦グラデ用)
# カードの枠線。**影のピーク値(#e8dcc8=232,220,200)と同値**だったため、
# 右辺・下辺で輪郭が影に溶け、左辺は 243→232→255 で立つのに右辺は
# 255→232,232→232,233,…,243 という20pxの茶色いにじみになっていた
# (2026-08-30 craft/medium)。影の初段から8段以上離した値にする。
CARD_EDGE = "#dccbb0"
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
# **褪せの1軸は彩度のみ**(2026-08-30 artdirection/high)。色相・明度は動かさない。
RED_FADE = _hsv(RED_FILL, s_mul=0.58)         # 非強調の損側の棒の面(S .78→.45)
LOSS_EDGE = _hsv(RED_FILL, s_mul=0.67, v_mul=0.93)   # 非強調の損側の箱の縁
LOSS_INK = _hsv(RED_FILL, s_mul=0.64, v_mul=0.80)    # 非強調の損側の文字
HEAD_BG = "#efe2c8"        # 表の見出し行・合計行の地。地紋(#f6ecdb)と2段階離す
                           # (旧 #f6ecd8 は地紋と1しか違わず区別が伝わらなかった)
# 中立ハイライト専用の地(2026-08-30 artdirection/medium)。旧実装は HEAD_BG を
# 流用していたが、それは見出し行・合計行と同色なので「ハイライト」に見えなかった。
NEUTRAL_SOFT = "#eae2d2"
NEUTRAL_RING = "#6f6653"   # 中立ハイライトのリング。地(NEUTRAL_SOFT)より1段濃い
                           # 同系色にする。旧 #3a3a3a の墨リングは、01だけが持つ
                           # 第4の視覚言語だった(2026-08-30 artdirection/medium)

# **強調枠の線幅トークンは1つ**(2026-08-29 批評6周目)。表の行ハイライト3.5pt・
# formulaカード5.0pt・arrowの箱4.0pt・waveの緑枠と、同じ「ここを見ろ」の枠が
# 4系統の重さに分裂していた。鼓動・ポップの増分はこの値の上に乗せる。
# **増分もトークン化する**(2026-08-30 consistency/medium): 実測で強調枠の線幅が
# 5px / 5px / 6px(最大7px)/ 6px(最大8px)の4系統に割れていた。原因は各部品が
# 個別に足す pulse/beat の増分。以後は必ず `EMPH_LW + EMPH_LW_PULSE * φ`(φ=0〜1)
# の形にし、**着地後は線幅を動かさない**(呼吸は alpha か色の明度で表す)。
EMPH_LW = 4.0
EMPH_LW_PULSE = 1.5

# ---- カードの固定寸法。**連続カットでパネル枠を動かさない**
# 2026-08-29 批評2周目: 表0.79・数式0.72・棒0.415…と部品ごとに枠が跳ねていた。
# **上辺と左右は全部品でこの1組に固定し、下辺だけ可変**にする。
# CARD_TOP/BOT も広げた(0.72→0.79 / 0.44→0.40)。カード上下の死んだドット帯
# (画面の約3割)を figure に食わせる。
# **これが全 painter が例外なく使う唯一のパネル矩形**(2026-08-30 consistency/high)。
# card() を CARD_L / CARD_BOT 以外の矩形で呼んでよいのは、次の3つだけ:
#   (1) person_bubble の rows ミニカード  (2) cover のチップ
#   (3) arrow / compare の内箱
# 中身が余るぶんはパネルを縮めるのではなく、cy を (CARD_TOP+CARD_BOT)/2 に置いて
# 上下対称の余白として残す。実測で下辺が 894/999/1004/1052/1149 の5種類に割れ、
# パネル下端〜字幕上端の空きが 55px〜462px(8倍)で脈動していた。
CARD_L, CARD_R = 0.06, 0.94
CARD_TOP, CARD_BOT = 0.79, 0.40
CARD_CY = (CARD_TOP + CARD_BOT) / 2
TITLE_Y = 0.84             # 図の文脈見出し(カード外・注記バー直下)。全部品共通

# 図の最下端と字幕ブロック上端のあいだの最小クリアランス(2026-08-30
# artdirection/high)。実測で 10px(20_meisai)〜466px(17_hitotsu)の46倍ばらつき、
# うち複数箇所で 0〜1px の衝突が出ていた。SUB_TOP は字幕の白アウトライン込みの上端。
CLEAR_MIN = 0.030          # ≒58px


def sub_top() -> float:
    """字幕ブロックの上端(白アウトライン込み)。図の下端はここより上に置く。"""
    fs = float(getattr(F, "SUB_FS_LOCK", None) or S.SUB_FS)
    half = fs * (S.DPI / 72.0) * 0.62 / S.H          # 字面の半分
    outline = fs * 0.12 * 1.55 / 2 * (S.DPI / 72.0) / S.H   # 白外縁の半分
    return S.SUBTITLE_Y + half + outline


# カードの落ち影は下へ約20px伸びるので、その分も見込む
SHADOW_ALLOW = 0.014


def clamp_above_subtitle(y_bottom: float) -> float:
    """図の下端(落ち影を含む)を、字幕から CLEAR_MIN 以上離す。"""
    return max(y_bottom, sub_top() + CLEAR_MIN + SHADOW_ALLOW)

# 図に従属するラベル(棒のカテゴリ名・矢印/比較の下ラベル・目盛)の1トークン。
# 実測で INK/36pt・SUB/38pt・SUB/36pt・INK/40pt の4系統に割れていた
# (2026-08-30 consistency/medium)。見出しが SUB なので、従属ラベルも SUB。
AXIS_INK = SUB
AXIS_FS = 38
TITLE_INK = "#4a4438"      # 文脈見出し(head_title)。免責注記より濃く置く

# 吹き出しの寸法(person_bubble と cta が共有する)。同じ部品なのに
# 0.40×0.11 と 0.37×0.082 で幅-8%・高さ-25%ちがっていた(consistency/medium)
BUBBLE_W, BUBBLE_H = 0.40, 0.11
BUBBLE_FS = 46
# サービス名チップ(cover と person_cards が共有する)。カバーと本編1カット目で
# 幅が154px違い、同じ3枚が0秒の継ぎ目で寸法まで変えていた(thumbnail/medium)
CHIP_W, CHIP_H, CHIP_STEP = 0.40, 0.070, 0.088
# 角丸は2段だけ(2026-08-30 thumbnail/low: 1枚のカバーに25px/14px/6pxの3系統)
R_LG, R_MD = 0.035, 0.024

_ease = F.ease_out
_back = F.ease_back


def _back_soft(t: float) -> float:
    """棒グラフ専用の緩いオーバーシュート(約3%)。retention/medium。"""
    return S.ease_out_back_soft(min(1.0, max(0.0, t)))


def _halo(fs: float, color=INK):
    """ドット地に直置きする小さめの字の、薄い白フチ。"""
    return [path_effects.Stroke(linewidth=fs * 0.12, foreground="#fffdf7"),
            path_effects.Normal()]


def idle(period: float = 0.9, phase: float = 0.0) -> float:
    """着地後も止まらないための共通の呼吸(-1〜1)。
    2026-08-29 批評2周目: 全部品が t=0.35〜0.7 で着地して以降静止していた。
    動画内時刻(F.LAST_T)で回すので、ユニットの後半でも必ずどこかが動く。"""
    return math.sin(2 * math.pi * (F.LAST_T / period) + phase)


def tri(period: float = 1.2) -> float:
    """三角波(-1〜1)。**速度が一定**なので、どの瞬間にも同じだけ動く。

    2026-08-30: 正弦の呼吸は山と谷で速度が0になり、その瞬間のフレーム対では
    「完全静止」に見える(check_design の M1 が拾う)。着地後の生存を
    位置の揺れで担保する場所には、正弦ではなく三角波を使う。
    """
    u = (F.LAST_T / period) % 1.0
    return 4.0 * abs(u - 0.5) - 1.0


def beat(period: float = 1.8, amp: float = 0.030) -> float:
    """周期の鼓動(1.0を下回らない)。常時ゆらゆらより上品に、周期に1回だけ膨らむ。
    2026-08-29 批評3周目: idle 0.010 は200px級の数字で約2pxの揺れ=静止に見えた。"""
    return 1.0 + amp * max(0.0, math.sin(2 * math.pi * F.LAST_T / period)) ** 3


def float_dy(amp: float = 0.003, period: float = 1.6) -> float:
    """図の塊をごく小さく上下に流す(**速度一定**の三角波)。

    2026-08-30 retention/high: 表・帯のように「着地したら本当に何も動かない」
    部品は、正弦の呼吸を足しても山と谷で速度が0になり、そのフレーム対が
    完全静止として残る(check_design の M1 は最後の2フレームで見る)。
    位置を一定速度で流せば、どの瞬間でもすべての輪郭が動く。
    位相は動画内時刻(F.LAST_T)なので、カット境界で跳ばない。
    """
    return amp * tri(period)


def _prog(t: float) -> float:
    """ナレーション内の進行度(0〜1)。**第2の拍はこれで刻む。**

    painter の t は anim 窓(約1〜1.2秒)で1.0に飽和するため、ナレーションが
    2.5秒を超えるユニットでは中盤から絵が止まっていた(2026-08-29 批評6周目)。
    shortlib が emit のたびに S.SUB_TIME=(ユニット内時刻, ユニット尺) を
    セットするので、そこから実時間の進行度を出す。無ければ t で代用。"""
    st = getattr(S, "SUB_TIME", None)
    if st and st[1] > 0:
        return min(1.0, max(0.0, st[0] / st[1]))
    return t


def head_title(fig, title: str, t: float = 1.0):
    """カード外・上部の文脈見出し。全painter共通(上部の視線アンカーを揃える)。"""
    if not title:
        return
    a = _ease((t - 0.04) / 0.18)
    if a <= 0.01:
        return
    # **常設クロームをヒエラルキーの頂点に置かない**(2026-08-30 artdirection/high)。
    # 免責注記(26pt・CR 8.1)がカットの主題ラベル(40pt・CR 4.78)より1.7倍濃く、
    # しかも白ハローがグリフのエッジを内側から削って40ptを弱く見せていた。
    # ハローを外し、色を SUB(#6b6459)から #4a4438 へ上げる。
    S.text_fit(fig, 0.5, TITLE_Y, F.fmt_disp(title), ha="center", va="center",
               color=TITLE_INK, fontsize=40, max_w=0.9, zorder=2.3, alpha=a)


def _ma() -> float:
    """FancyBboxPatch の mutation_aspect。figure座標の rounding_size は
    9:16 のキャンバスで縦に1.78倍伸び、角丸が楕円弧になっていた
    (実測 横30px×縦40px。2026-08-29 批評5周目)。W/H を渡してスクリーン上の
    真円に戻す。**scenes_fp の FancyBboxPatch は必ずこれを渡す**。"""
    return S.W / S.H


_SHADOW_CACHE: dict = {}
SHADOW_BLUR_PX = 11.0      # 実測(右18px − オフセット7px ≒ 11px)の見た目を保つ
SHADOW_PEAK = 0.34         # ぼかす前のマスク濃度。裾の最大値が旧6層と同じになる値


def _shadow_rgba(wpx: int, hpx: int, rpx: float, blur: float):
    """角丸矩形のアルファマスクを**実ガウス**でぼかした RGBA 配列を返す。

    2026-08-30 craft/medium・artdirection/medium: 6層の手打ちアルファ
    (0.10/0.08/0.06/0.045/0.03/0.02)は各段差が約2/255の量子化で、角に
    同心の等高線リングが6本数えられた。位置によっては 232→237→240→243→
    239→241→243 と一度明るくなってから再び暗くなる非単調ささえ出ていた。
    """
    from PIL import Image as _Im, ImageDraw, ImageFilter
    pad = int(math.ceil(blur * 3)) + 2
    key = (wpx, hpx, round(rpx, 1), round(blur, 2), pad)
    a = _SHADOW_CACHE.get(key)
    if a is None:
        m = _Im.new("L", (wpx + 2 * pad, hpx + 2 * pad), 0)
        d = ImageDraw.Draw(m)
        rr = max(0.0, min(rpx, min(wpx, hpx) / 2.0 - 0.5))
        d.rounded_rectangle([pad, pad, pad + wpx - 1, pad + hpx - 1],
                            radius=rr, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(radius=blur))
        a = np.asarray(m, dtype=np.float32) / 255.0
        if len(_SHADOW_CACHE) > 64:
            _SHADOW_CACHE.clear()
        _SHADOW_CACHE[key] = a
    return a, pad


def drop_shadow(fig, x, y, w, h, r=0.028, z=2.19, alpha=1.0, clip_y=None):
    """**実ガウス**の落ち影。カードも棒も箱も矢印もここから落とす。

    - 影のオフセットは超低速で±1.5px揺れる(カードだけのユニットでも
      完全静止フレームを作らない)
    - clip_y: その高さより下を描かない(棒の影が基線=地面を貫通しない)
    """
    from matplotlib.colors import to_rgb
    wob = 0.0015 * idle(period=1.4)
    wpx = max(2, int(round(w * S.W)))
    hpx = max(2, int(round(h * S.H)))
    if wpx * hpx > 6_000_000:                 # 保険(巨大矩形は描かない)
        return
    a, pad = _shadow_rgba(wpx, hpx, r * S.W, SHADOW_BLUR_PX)
    # 影のオフセット(旧6層の重心 ≒ +4px / -6.5px)
    ox = int(round((x + wob) * S.W + 0.0040 * S.W)) - pad
    oy = int(round((y - wob) * S.H - 0.0065 * S.H)) - pad
    a = a[::-1]                            # 行0を下端に(origin="lower")
    if clip_y is not None:
        # 基線より下は**マスクの側で**消す(地面に立つ棒の影が地面を貫通しない)
        cut = int(round(clip_y * S.H)) - oy
        if cut > 0:
            a = a.copy()
            a[:min(cut, a.shape[0])] = 0.0
    rgba = np.zeros(a.shape + (4,), dtype=np.float32)
    rgba[..., :3] = np.array(to_rgb(SHADOW), dtype=np.float32)
    rgba[..., 3] = a * SHADOW_PEAK * alpha
    # **figimage で1枚のラスタとして敷く。** add_axes を使うと
    # check_overlap が「グラフ」として拾い、影が禁止領域判定に掛かってしまう
    im = fig.figimage(rgba, xo=ox, yo=oy, origin="lower", zorder=z)
    im.set_gid("fp_shadow")


def card(fig, x, y, w, h, face=CARD, edge=CARD_EDGE, lw=2.0, r=0.028,
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


def _is_num_token(tok: str) -> bool:
    """「数字+短い単位」だけを数トークンとみなす。

    2026-08-30: 「止める1つの月額」のような**句**まで数として組むと、
    big_number が「1」だけ極太・「つの月額」を52%に落とし、
    句の中の無関係な数字が主役になってしまう。
    """
    m = _NUM_RE.match(tok)
    return bool(m) and len(m.group(3) or "") <= 3 and len(m.group(1) or "") <= 3


def _renderer(fig):
    fig.canvas.draw()
    return fig.canvas.get_renderer()


_CJK = re.compile(r"[ぁ-んァ-ヶ一-龥]")


def unit_scale_for(unit: str) -> float:
    """単位グリフの縮小率。**CJK1字の単位は 0.52、ラテン/記号は 0.62**。

    2026-08-30 consistency/medium: 62%は CJK 字形では光学的に効かない。
    08_kikan の実測で、数字が rows545-828(283px)なのに「回」は 211px(75%)
    あり、階層が立っていなかった(CJKは字面が正方形いっぱいに来るため)。
    """
    if unit and _CJK.search(unit):
        return 0.52
    return 0.62


def _num_w(fig, r, text: str, fs: float, unit_scale: float = None) -> float:
    """big_number と同じ組み方(単位はCJK52%/ラテン62%)での実測幅。"""
    text = text.replace(",", "")
    fam = [F.NUM_FAMILY]
    m = _NUM_RE.match(text)
    if not m:
        return F.measure_w(fig, r, F.fmt_disp(text), fs * 0.72, fam, F.NUM_WEIGHT)
    pre, digits, suf = m.groups()
    if unit_scale is None:
        unit_scale = unit_scale_for((pre or "") + (suf or ""))
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


COUNT_WIN = 0.80           # big_number のカウント窓(t=0.8 で9割)
BARS_WIN = 0.90            # bars の伸長・カウント窓
FORMULA_ANS_ST = 0.36      # formula の答えがスタンプされ始める t
ARROW_ARRIVE = 0.55        # arrow の値が右箱へ到達する t


def landing_sec(kind: str, anim: float) -> float:
    """**図の着地時刻**(ユニット頭からの秒)。Unit.se_at はここに合わせる。

    2026-08-30 retention/medium: SE の時刻と絵の着地が別の時計で決まっていた。
    Unit.se_at は「ユニット頭からの秒」、bars の着地は anim 窓の割合、
    table の合計リビールはナレーション進行度(_prog)。実測で
    fueru は90〜130ms遅れ、hyo_g は約0.9秒早く鳴っていた。
    **ナレーション進行度で動くカット(table)は Unit.se_at_frac を使う。**
    """
    return {
        "bars": BARS_WIN,
        "hero": COUNT_WIN,
        "formula": FORMULA_ANS_ST + COUNT_WIN / 2.2,
        "arrow": ARROW_ARRIVE,
    }[kind] * anim

_INKGAP_CACHE: dict = {}


def _ink_bottom_gap(fig, r, s: str, fs: float) -> float:
    """文字列のインク下端が、ベースラインからどれだけ下(figure座標)にあるか。

    単位グリフを数字のインク下端に揃えるために使う(consistency/medium)。
    """
    if not s:
        return 0.0
    key = (s, round(fs, 2), S.H)
    v = _INKGAP_CACHE.get(key)
    if v is None:
        tmp = fig.text(0.0, 0.5, s, fontsize=fs, fontfamily=[F.NUM_FAMILY],
                       fontweight=F.NUM_WEIGHT, va="baseline")
        e = tmp.get_window_extent(renderer=r)
        v = (0.5 * S.H - e.y0) / S.H
        tmp.remove()
        _INKGAP_CACHE[key] = v
    return v


def big_number(fig, cx, cy, text, fs, color=RED, t=1.0, count=True,
               z=2.4, max_w=0.80, unit_scale=None, alpha=1.0, ha="center",
               path_effects=None):
    """ヒーロー数字。数字は第2書体の極太、**単位は62%に落として桁を立てる**。

    t<0.55 のあいだは 0→最終値のカウントアップ(ease_out)。
    数字を含まない文字列はそのまま1つのテキストで描く。
    """
    text = text.replace(",", "")
    # **「数字+短い単位」以外は語として組む**(2026-08-30)。
    # 「缶コーヒー1本」のような句まで数として組むと、句の中の無関係な「1」だけが
    # 極太になり、前後が52%に落ちて階層が逆転する
    m = _NUM_RE.match(text) if _is_num_token(text) else None
    fam = [F.NUM_FAMILY]
    # 着地後は常時の呼吸パルス(±1.2%)。カウント完了からユニット末までの
    # 0.7〜1.2秒が完全静止になっていた(2026-08-29 批評5周目・実測 変化画素0.0%)
    boost = 1.0
    if t >= COUNT_WIN:
        boost *= 1.0 + 0.012 * math.sin(2 * math.pi * F.LAST_T / 0.9)
    if count and t >= COUNT_WIN:
        # 着地ポップ: 着地の瞬間に+22%膨らんで0.12秒で戻る。同時に色を
        # 一瞬白へ振る(音のdonだけ鳴って絵が素通りしていた)
        land = max(0.0, 1.0 - (t - COUNT_WIN) / 0.12)
        if land > 0.0:
            boost *= 1.0 + 0.22 * land
            color = _mix(color, "#ffffff", 0.35 * land)
    fs = fs * boost
    max_w = max_w * boost
    if not m:
        S.text_fit(fig, cx, cy, F.fmt_disp(text), ha=ha, va="center",
                   color=color, fontsize=fs * 0.72, max_w=max_w, zorder=z,
                   fontfamily=fam, fontweight=F.NUM_WEIGHT, alpha=alpha,
                   path_effects=path_effects)
        return
    pre, digits, suf = m.groups()
    if unit_scale is None:
        unit_scale = unit_scale_for((pre or "") + (suf or ""))
    val = int(digits)
    if count:
        # **カウントの9割を t=0.8 まで引き延ばす**(2026-08-30 retention/high)。
        # 旧 `1-(1-u)^2.8` を窓0.55で回すと、実測で値の90%に t≈0.29 で到達し、
        # 残り40%の時間は3%しか動かない=判別不能な静止だった。
        # 窓0.80・指数1.7なら t=0.8 で0.90、t=1.0 で1.00 になる。
        u = min(1.0, max(0.0, t / COUNT_WIN))
        frac = 1.0 - (1.0 - u) ** 1.7
        val = int(round(val * frac))
        if t >= COUNT_WIN:
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
        w_final = F.measure_w(fig, r, F.fmt_disp(digits), fs, fam, F.NUM_WEIGHT)
    # **中央揃えの基準は「数字部分の中心」**(2026-08-30 artdirection/low)。
    # 文字列全体の bbox 中心で揃えると、単位グリフのサイドベアリングぶん数字が
    # 押され、17_hitotsu で左42px・右31px、08_kikan で左31px・右37px ずれていた。
    # カウント中に軸が動かないよう、幅は**最終値**(w_final)で取る。
    # ただし max_w を食い切っている文字列(カバーの114万円など)では、
    # 数字中心に寄せると単位が枠から出るので、ブロック全体を窓内にクランプする。
    if ha == "right":
        x = cx - (w_pre + w_num + w_suf)
    elif ha == "left":
        x = cx
    else:
        x = cx - w_final / 2 - w_pre + (w_final - w_num) / 2
        lo, hi = cx - max_w / 2, cx + max_w / 2
        x = min(max(x, lo), hi - (w_pre + w_final + w_suf))
    y_base = cy - 0.36 * fs * (S.DPI / 72) / S.H     # 数字のベースライン
    kw = dict(color=color, fontfamily=fam, fontweight=F.NUM_WEIGHT,
              zorder=z, alpha=alpha)
    if path_effects is not None:
        kw["path_effects"] = path_effects
    # 単位は **ベースライン揃えではなく、数字のインク下端に揃える**
    # (2026-08-30 consistency/medium: 08_kikan の「回」がベースラインより
    #  18px下に沈み、数字と別の行に載って見えていた)
    y_unit = y_base + _ink_bottom_gap(fig, r, digits, fs) \
        - _ink_bottom_gap(fig, r, (pre or "") + (suf or ""), fu)
    if pre:
        fig.text(x, y_unit, pre, ha="left", va="baseline", fontsize=fu, **kw)
        x += w_pre
    fig.text(x, y_base, shown, ha="left", va="baseline", fontsize=fs, **kw)
    x += w_num
    if suf:
        fig.text(x, y_unit, F.fmt_disp(suf), ha="left", va="baseline",
                 fontsize=fu, **kw)


POSE_TOP_STD = 0.795       # 立ち絵の上端。head_title(TITLE_Y=0.84)の下に置く


def person(name: str, height: float = 0.45, top: float = POSE_TOP_STD,
           title: str = ""):
    """キャラだけ。いちばん基本の絵(ボブは draw_pose が入れる)。

    **top は立ち絵4部品で共有し、height だけで大きさを変える**
    (2026-08-30 artdirection/medium: 裾の終端が 21=y1005 / 10=y1245 /
     20=y1292 とユニットごとに違い、同じ人物の立ち位置が定まらなかった)。
    """
    def painter(fig, t):
        F.draw_pose(fig, name, top=top, height=height)
        head_title(fig, title, t)
    return painter


def chip_fs(fig, labels) -> float:
    """チップ列**全体で1つの級数**を決める(いちばん長いラベルに合わせる)。

    2026-08-30 thumbnail/low: 幅と max_w だけで組むと、実測グリフ高が
    Netflix 73px / Spotify 92px / プライム 82px と揃わなかった。
    person_bubble の rows が既に採っている「全行の実測幅から共通の fs を
    1つ決める」ループを、カバーと本編のチップにも適用する。
    """
    r = _renderer(fig)
    fam, wt = [F.NUM_FAMILY], F.NUM_WEIGHT
    fs = 58.0
    for la in labels:
        w = F.measure_w(fig, r, F.fmt_disp(str(la)), fs, fam, wt)
        if w > CHIP_W - 0.05:
            fs *= (CHIP_W - 0.05) / w
    return fs


def service_chip(fig, x, y, label, alpha=1.0, sc_=1.0, z=2.3, fs=None,
                 shadow=True):
    """サービス名チップ。**cover と person_cards が同じ寸法・書体で描く**。

    2026-08-30 consistency/medium・thumbnail/medium: カバーは 0.55×0.088 の
    Noto Black 64pt、本編は 0.40×0.088 の RocknRoll 40pt で、同じ3枚が
    0秒の継ぎ目でラベル・順序・位置・幅・書体を同時に変えていた。
    """
    if shadow:
        card(fig, x, y, CHIP_W, CHIP_H, edge=CARD_EDGE_STRONG, lw=3.0,
             r=R_MD, z=z, sc=sc_, alpha=alpha)
    else:
        # **人物の上に UI の影を落とさない**(2026-08-30 artdirection/low)。
        # 描き絵の上にドロップシャドウが乗ると様式が混ざる
        w, h = CHIP_W * sc_, CHIP_H * sc_
        cx0, cy0 = x + CHIP_W / 2 - w / 2, y + CHIP_H / 2 - h / 2
        fig.add_artist(FancyBboxPatch(
            (cx0, cy0), w, h, boxstyle=f"round,pad=0,rounding_size={R_MD}",
            transform=fig.transFigure, facecolor=CARD,
            edgecolor=CARD_EDGE_STRONG, linewidth=3.0, zorder=z, alpha=alpha,
            mutation_aspect=_ma()))
    if fs is None:
        fs = 52 if _CJK.search(str(label)) else 58
    S.text_fit(fig, x + CHIP_W / 2, y + CHIP_H / 2, F.fmt_disp(str(label)),
               ha="center", va="center", color=INK, fontsize=fs * sc_,
               max_w=(CHIP_W - 0.05) * sc_, zorder=z + 0.1, alpha=alpha,
               fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)


def person_bubble(name: str, text: str, height: float = 0.45,
                  top: float = POSE_TOP_STD, rows=None, title: str = ""):
    """キャラ + 吹き出し(視聴者の心の声を代弁する。競合の70.8%の技法)。

    吹き出しは**しっぽの先端(口元側)からポップイン**する(2026-08-29)。
    貼り紙ではなく「心の声が湧く」に見せる。

    rows: [(ラベル, 金額), ...] を渡すと、キャラの左に明細アプリ風のミニカード
    を添える(2026-08-29 批評3周目。「明細を開く」と言うのに明細の絵が無く、
    立ち絵の下に画面の約22%の無人地帯があった)。
    """
    def painter(fig, t):
        F.draw_pose(fig, name, cx=0.58, top=top, height=height)
        head_title(fig, title, t)
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
        # **本体としっぽは1本の閉じた輪郭**(2026-08-30 craft/high)。
        # 面色パッチ3枚で接合部を塗り潰す旧実装は、フル解像度で見ると
        # 本体下辺の枠線が「断ち切られたスタブ」として残っていた。
        bx, by = sc(x - BUBBLE_W / 2, y - BUBBLE_H / 2)
        bw, bh = BUBBLE_W * p, BUBBLE_H * p
        tail = [sc(x + 0.14, y - BUBBLE_H / 2), (tipx, tipy),
                sc(x + 0.19, y - BUBBLE_H / 2)]
        # 吹き出しにも他のカードと同じ落ち影を通す(consistency/medium:
        # 影を持つカードと平らな容器が同じ画面に同居していた)
        drop_shadow(fig, bx, by, bw, bh, r=0.030, z=2.49, alpha=a)
        fig.add_artist(PathPatch(
            F.bubble_path(bx, by, bw, bh, 0.030 * p, tail),
            transform=fig.transFigure, facecolor=CARD,
            edgecolor=CARD_EDGE_STRONG, linewidth=4.0, joinstyle="round",
            capstyle="round", zorder=2.5, alpha=a))
        tx, ty = sc(x, y)
        # 文字は「素のゴシック細字」をやめ、帯の文字色(BAND_INK)+級数1.2倍
        S.text_fit(fig, tx, ty, F.fmt_disp(text), ha="center", va="center",
                   color=F.BAND_INK, fontsize=BUBBLE_FS * max(p, 0.2), max_w=0.36,
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
                # **字幕から CLEAR_MIN 以上離す**(2026-08-30 consistency/high)。
                # 旧 my=0.285 ではミニカードの下枠と字幕の白アウトラインの空きが
                # 0〜1px(実測 x=300: 枠 1371-1377 / アウトライン 1378-1381)で、
                # 前ラウンドで名指しされた1px接触が別ユニットで再発していた
                mx, my = 0.045, clamp_above_subtitle(0.285)
                gap_px = (my - sub_top()) * S.H
                assert gap_px >= 24, f"明細ミニカードと字幕の空きが {gap_px:.0f}px"
                card(fig, mx, my, mw, mh, lw=2.5, r=R_MD, z=2.2, alpha=ac)
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
                    big_number(fig, mx + mw - ins_r, yy, str(vb), 30.0,
                               color=INK, t=1.0, count=False, z=2.4,
                               max_w=mw * 0.5, alpha=ai, ha="right")
    return painter


def person_cards(name: str, labels, height: float = 0.44,
                 top: float = POSE_TOP_STD, title: str = ""):
    """キャラ(困り顔)+左に積み上がるカード列。冒頭0秒目の「積み上がる感」用。
    2026-08-29 批評2周目: 0秒目が笑顔の立ち絵と羅列テロップだけで緊張が無かった。

    2026-08-30 の厳格審査:
    - チップは service_chip() 共通部品(cover と寸法・書体・角丸を共有)
    - チップの影を落とさない(描き絵の上に UI の影が乗る様式混在を解消)
    - 積む向きを cover と揃える(labels[0] が**いちばん上**)
    - カード列の下端は字幕から CLEAR_MIN 以上離す
    """
    def painter(fig, t):
        F.draw_pose(fig, name, cx=0.66, top=top, height=height)
        n = len(labels)
        step = CHIP_STEP
        y_bot = clamp_above_subtitle(0.455)
        fs_c = chip_fs(fig, labels)
        for i, lab in enumerate(labels):
            p = _back((t - 0.08 - i * 0.16) / 0.24)
            if p <= 0.01:
                continue
            a = _ease((t - 0.08 - i * 0.16) / 0.16)
            bx = -0.30 + (0.05 + 0.30) * p       # 左から滑り込む
            # labels[0] を最上段に(cover のチップと同じ並び順・同じ積み方向)
            yy = y_bot + (n - 1 - i) * step
            service_chip(fig, bx, yy, lab, alpha=a, shadow=False, fs=fs_c)
        head_title(fig, title, t)
    return painter


def cover(line1: str, line2: str, line3: str, name: str = "01_base",
          disclaimer: str = "", count_from: str = "", badge_color: str = RED,
          flip: bool = False, badge_sub: str = "", teaser: str = ""):
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

    2026-08-29 批評6周目の全面改修:
    - **サービス名は上帯のテキストをやめ、下帯の3チップ(白カード)に**。
      72pxタイル寸で字高5.7pxに潰れ、Shorts再生UIの上部アイコン帯
      (y40〜150px)にも刺さっていた。チップなら字高≈90pxで判読できる
    - 問い(line2)を最上段 y=0.885 に置く。**y>0.92 と y<0.08 には
      テキストを置かない**(上下のUI帯)
    - バッジの影を本編カードと同じ drop_shadow() に統一(濃赤の
      オフセット複製は縮小時に赤の二重輪郭に見えていた)
    - 立ち絵は**胸上クロップ(crop="bust")で顔を拡大**し右へ寄せる。
      下51%が無地のジャケットの塊で、顔が全高18%しか無かった。
      視線は画面内側(チップ・バッジの側)を向く。下端は画面外に落とす
    - 打消しプレートは不透明(旧 alpha0.92 は背後の髪がにじんだ)。
      プレート・バッジ・頭頂の全ペアで**空き24px以上を assert**
      (同じ衝突を3回目に持ち込まない)
    """
    # ---- 版面(すべて実測から決めた figure 座標)
    # 縦の配分は「72pxタイルで字高8px以上」から逆算している。1080px幅で
    # ink 120px を出すには CJK 1行あたり6字以下でなければ物理的に届かないので、
    # フックは**2行**にし、帯の高さを2行ぶん取る(line2 は改行で渡す)。
    HOOK_Y, HOOK_H = 0.745, 0.165        # 上端 0.910 < 1-UI_TOP_FRAC(0.915)
    BADGE_Y, BADGE_H = 0.520, 0.190
    TEASE_Y, TEASE_H = 0.446, 0.056
    CHIP_X = 0.028
    CHIP_BOT = 0.182                     # 最下段チップの下端(下から349px)
    # 立ち絵: 目が右レール(x>=0.87)に入らず、かつチップ帯の行で
    # 左シルエットがチップの文字(右端 0.403)より右に来る唯一の帯。
    # 実測: 目=画像幅の 0.488/0.610、左シルエット=下段行で 0.187
    POSE_TOP, POSE_H, POSE_CX = 0.500, 0.46, 0.74

    def painter(fig, t):
        F.hide_chrome(fig)      # 帯・バッジは重ねない(背景のクリーム+ドットは残る)
        F.dim_dots(fig)         # 水玉はカバーだけ半減光(72px縮小でノイズになる)
        services = [x for x in re.split(r"[・×]", line1) if x]
        # ---- 1段目: フックは**墨の帯の上の白文字**(2026-08-30 thumbnail/high)。
        # 白フィル+16pxの茶縁は、クリーム地に対しコントラスト比1.22:1で、
        # 判読を縁だけが担保していた。72pxタイルに縮小すると縁が1px以下になり、
        # 字が地に溶ける(実測 字高5.7px)。帯に載せれば 13:1 で縁が要らなくなる。
        hook_lines = _hook_lines(fig, str(line2))
        fs2 = min([S.fit_fontsize(fig, F.fmt_disp(ln), HOOK_FS_MAX, max_w=0.86)
                   for ln in hook_lines] or [HOOK_FS_MAX])
        p2 = _ease((t - 0.04) / 0.20)
        if p2 > 0.01:
            hs = 1.25 - 0.25 * p2
            drop_shadow(fig, 0.5 - 0.46, HOOK_Y, 0.92, HOOK_H, r=R_MD, z=2.28)
            fig.add_artist(FancyBboxPatch(
                (0.5 - 0.46, HOOK_Y), 0.92, HOOK_H,
                boxstyle=f"round,pad=0,rounding_size={R_MD}",
                transform=fig.transFigure, facecolor=INK, edgecolor="none",
                zorder=2.30, mutation_aspect=_ma()))
            cy_h = HOOK_Y + HOOK_H / 2
            for li, ln in enumerate(hook_lines):
                yy_h = cy_h + (len(hook_lines) - 1) * HOOK_LINE_H / 2 \
                    - li * HOOK_LINE_H
                S.text_fit(fig, 0.5, yy_h, F.fmt_disp(ln),
                           ha="center", va="center", color="#fff8ec",
                           fontsize=fs2 * hs, max_w=0.86, zorder=2.34,
                           fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)
        # ---- 2段目: 赤バッジ。数字・読み下し・打消しの3行を**バッジの中**に積む
        # (2026-08-30 thumbnail/medium: 免責プレートは画面のいちばん高い帯を
        #  コントラスト比1.16:1の死荷重で占めていた。赤地の上なら4:1以上が出る)
        pb = _ease((t - 0.10) / 0.22)
        if pb > 0.01:
            bs = beat(period=1.6, amp=0.014) if t > 0.55 else 1.0
            bh = BADGE_H * bs
            bw = 0.96 * pb * bs
            # バッジは**常に中央合わせ**(2026-08-29 批評5周目)
            bx, by = 0.5 - bw / 2, BADGE_Y - (bh - BADGE_H) / 2
            drop_shadow(fig, bx, by, bw, bh, r=R_LG, z=2.34)
            fig.add_artist(FancyBboxPatch(
                (bx, by), bw, bh, boxstyle=f"round,pad=0,rounding_size={R_LG}",
                transform=fig.transFigure, facecolor=badge_color,
                edgecolor="none", zorder=2.4, mutation_aspect=_ma()))
            if pb > 0.55:
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
                # 字高を約300px(画面高の15.6%)へ。旧 200pt/max_w0.84 では
                # 222px(11.6%)しかなく、バッジ内部の充填率が51%だった
                # 字高を約230px(バッジ内の充填率63%→上下余白が等しくなる位置)。
                # 旧 200pt / by+bh/2-0.008 は、ディセンダを持たない数字組に
                # 逆向きの光学補正を掛けていて、上余白125px対下余白84pxだった
                big_number(fig, 0.5, BADGE_Y + 0.1135, shown3, 230 * nb,
                           color="#ffffff", t=1.0, count=False,
                           z=2.5, max_w=min(0.92, 0.88 * nb))
            if badge_sub:
                as_ = _ease((t - 0.30) / 0.18)
                if as_ > 0.01:
                    S.text_fit(fig, 0.5, BADGE_Y + 0.0175, F.fmt_disp(badge_sub),
                               ha="center", va="center", color="#ffffff",
                               fontsize=30, max_w=0.84, zorder=2.5,
                               alpha=0.85 * as_)
            elif disclaimer:
                ad = _ease((t - 0.40) / 0.20)
                if ad > 0.01:
                    S.text_fit(fig, 0.5, BADGE_Y + 0.0175, disclaimer,
                               ha="center", va="center", color="#ffffff",
                               fontsize=26, max_w=0.84, zorder=2.5,
                               alpha=0.78 * ad)
        # ---- 3段目: 伏せている側を**絵で名指す**(2026-08-30 thumbnail/medium)。
        # 旧カバーは支払う額・期間・対象がすべて開示済みで、「まだ見ていない何か」が
        # 存在しなかった。赤=出ていく / 緑=まだ伏せている、の2枚組にする。
        if teaser:
            pt_ = _back((t - 0.34) / 0.22)
            if pt_ > 0.01:
                at_ = _ease((t - 0.34) / 0.16)
                tw = 0.46
                fig.add_artist(FancyBboxPatch(
                    (CHIP_X, TEASE_Y), tw, TEASE_H,
                    boxstyle=f"round,pad=0,rounding_size={R_MD}",
                    transform=fig.transFigure, facecolor=GREEN_SOFT,
                    edgecolor=GREEN, linewidth=3.0, zorder=2.3, alpha=at_,
                    mutation_aspect=_ma()))
                S.text_fit(fig, CHIP_X + tw / 2, TEASE_Y + TEASE_H / 2,
                           F.fmt_disp(teaser), ha="center", va="center",
                           color=GREEN_DARK, fontsize=44, max_w=tw - 0.05,
                           zorder=2.35, alpha=at_,
                           fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)
        # ---- キャラ。**右アクションレール(x 940〜1060)に目を置かない**
        # (2026-08-30 thumbnail/high)。実測した目の位置(画像幅の 0.488 / 0.610)と
        # 左シルエット(チップ帯の行で 0.19〜0.27)から、cx=0.74 / height=0.46 が
        # 「目 787〜912px(レールの外)」かつ「チップの右端 0.428 より左に人物が来ない」
        # を同時に満たす唯一の帯だった。両方の assert を末尾に置く。
        pc = _ease((t - 0.25) / 0.35)
        pose_top = POSE_TOP - 0.05 * (1 - pc)
        F.draw_pose(fig, name, cx=POSE_CX, top=pose_top, height=POSE_H,
                    fade=False, bob=True, flip=flip, crop="bust")
        # ---- 4段目: サービス名チップ(本編1カット目と同じ部品・同じ並び順)
        fs_c = chip_fs(fig, services)
        for i, svc in enumerate(services):
            pc_ = _back((t - 0.30 - i * 0.10) / 0.22)
            if pc_ <= 0.01:
                continue
            a_c = _ease((t - 0.30 - i * 0.10) / 0.14)
            yy = CHIP_BOT + (len(services) - 1 - i) * CHIP_STEP
            service_chip(fig, CHIP_X, yy, svc, alpha=a_c,
                         sc_=min(1.0, pc_), z=2.3, fs=fs_c)
        # ---- 寸法検査。**全 t で走らせる**(pose_top はアニメ中 0.470 まで
        # 上がるので、途中フレームのほうが上の要素に近づく)
        head_top = pose_top - _head_top_frac(name, flip) * POSE_H
        gap_px = (BADGE_Y - head_top) * S.H
        assert gap_px >= 24, (
            f"カバー: バッジ下端と頭頂の空きが {gap_px:.0f}px。24px以上とること")
        if t >= 0.99:
            # (a) チップ帯が実機の下部スクリム(下端15%)に沈まないこと
            assert CHIP_BOT * S.H >= 346, "カバー: 最下段チップが下部UI帯に沈む"
            assert (CHIP_Y_TOP := CHIP_BOT + (len(services) - 1) * CHIP_STEP
                    + CHIP_H) <= 1 - F.UI_TOP_FRAC, "カバー: チップが上部UI帯に掛かる"
            # (b) 目が右アクションレール(x>=0.87)に入らないこと
            eye_x = POSE_CX + (0.610 - 0.5) * POSE_H * _pose_aspect(name, flip) \
                * (S.H / S.W)
            assert eye_x < 0.87, f"カバー: 目が右レールに入る(x={eye_x:.3f})"
            # (c) チップの文字が立ち絵に食われないこと
            left = _pose_left_frac(name, flip, CHIP_BOT - pose_top,
                                   CHIP_Y_TOP - pose_top, POSE_H)
            pose_left = POSE_CX + (left - 0.5) * POSE_H \
                * _pose_aspect(name, flip) * (S.H / S.W)
            txt_right = CHIP_X + (CHIP_W + (CHIP_W - 0.05)) / 2
            assert pose_left > txt_right, (
                f"カバー: 立ち絵({pose_left:.3f})がチップの文字"
                f"({txt_right:.3f})に掛かる")
            # (d) フックが72pxタイルで判読できる字高を持つこと
            ink_px = fs2 * (S.DPI / 72.0) * 0.88
            assert ink_px * 72 / S.W >= 8.0, (
                f"カバー: フックの字高が72pxタイルで {ink_px * 72 / S.W:.1f}px。"
                "1行6字以下に割れる文言にすること")
    return painter


HOOK_LINE_H = 0.081        # フックの行送り
HOOK_FS_MAX = 104          # ink ≈127px → 72pxタイルで8.5px
HOOK_INK_MIN_PX = 8.0      # 72pxタイルでのフックの最小字高


def _hook_lines(fig, text: str) -> list:
    """フックを**72pxタイルで判読できる字高**になるまで行に割る。

    1080px幅では CJK 1行6字を超えると ink 120px(=タイル8px)に届かない。
    改行が明示されていればそれに従い、無ければ自動で2行に割る
    (読点があればそこで、無ければ中央で)。2行でも足りなければ3行まで。
    """
    if "\n" in text:
        return [ln for ln in text.split("\n") if ln]

    def ink(lines):
        fs = min(S.fit_fontsize(fig, F.fmt_disp(ln), HOOK_FS_MAX, max_w=0.86)
                 for ln in lines)
        return fs * (S.DPI / 72.0) * 0.88 * 72 / S.W

    def split(t, n):
        if n <= 1:
            return [t]
        for sep in ("、", "。", " "):
            i = t.find(sep, max(1, len(t) // n - 2))
            if 0 < i < len(t) - 1:
                return [t[:i + 1]] + split(t[i + 1:], n - 1)
        k = max(1, round(len(t) / n))
        return [t[:k]] + split(t[k:], n - 1)

    for n in (1, 2, 3):
        lines = split(text, n)
        if ink(lines) >= HOOK_INK_MIN_PX or n == 3:
            return lines
    return [text]


def _pose_aspect(name: str, flip: bool) -> float:
    key = ("aspect", name, flip)
    if key not in F._POSE_CACHE:
        im = F.pose(name, fade=False, flip=flip, crop="bust")
        F._POSE_CACHE[key] = im.width / im.height
    return F._POSE_CACHE[key]


def _pose_left_frac(name: str, flip: bool, dy0: float, dy1: float,
                    height: float) -> float:
    """立ち絵の左シルエット(画像幅に対する割合)を、指定の縦帯で最小値として返す。

    dy0/dy1 は pose の上端からの相対距離(figure座標。負の値)。
    カバーのチップ文字が人物に食われていないかを機械で見るために使う。
    """
    im = F.pose(name, fade=False, flip=flip, crop="bust")
    a = np.asarray(im.getchannel("A"))
    h, w = a.shape
    r0 = int(np.clip(-dy1 / height, 0, 1) * (h - 1))
    r1 = int(np.clip(-dy0 / height, 0, 1) * (h - 1))
    band = a[min(r0, r1):max(r0, r1) + 1] > 8
    cols = np.where(band.any(axis=0))[0]
    return float(cols[0]) / w if len(cols) else 1.0


def _head_top_frac(name: str, flip: bool) -> float:
    """立ち絵(bustクロップ)の頭頂の位置(画像高に対する割合)。

    2026-08-30 consistency/high: 判定が「不透明幅が画像幅の25%を超える最初の行」
    だったため、頭頂の細い部分(髪の山)を頭と認識せず、**実際に見える最上端より
    下**を頭頂として返していた。その結果、24px以上を要求する assert がすり抜け、
    プレート下端と髪の墨が1pxで接触したまま3回連続で出荷物に残った。
    判定を「アルファ>64 の画素が1行に8px以上ある最初の行」に緩める。
    """
    key = ("headtop", name, flip)
    if key not in F._POSE_CACHE:
        im = F.pose(name, fade=False, flip=flip, crop="bust")
        a = np.asarray(im.getchannel("A"))
        solid = (a > 64).sum(axis=1) >= 8
        idx = int(np.argmax(solid)) if solid.any() else 0
        F._POSE_CACHE[key] = idx / a.shape[0]
    return F._POSE_CACHE[key]


def table(headers, rows, highlight=None, title="", build=False, from_row=None,
          total_mode="red", wave_role="warn", focus=None, hl_role="warn",
          build_at=None, hl_at=None, total_ink=None):
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

    2026-08-29 批評6周目:
    - focus のズームは**往復**(t=0.85から0.15で正準グリッドへ戻る)。
      戻り区間が無く、カット境界で表全体が6%縮んで57px跳んでいた
    - hband に x0/w を渡せるようにし、行ハイライトの帯は枠の**内側**に収める
      (帯が枠線の左右外側に約3pxはみ出していた)
    - frame() の縦インセットを 0.005 / hh=rh-0.010 に広げ、合計行上の黒罫と
      赤枠が融合しないようにする(黒罫側も 0.003 上げる)
    - hl_role="neutral": 単なる読み上げ位置は墨色リング+ベージュ地
      (赤=損・警告の色文法を列挙に流用しない)
    - build_at / hl_at: 行の出現と枠の着地を**ナレーション進行度**(0〜1)に
      割り付ける(hyo_a で声より先に第3行が強調されていた)
    - sweep / wave の位相もナレーション進行度で刻む(anim窓で完了して
      ユニット後半が静止していた)
    - ?,???円 のティーズセルは文字色が明滅する(次への引きを絶やさない)
    """
    n = len(rows)
    # total_ink: 合計行の値の色。**「やめた」文脈のカットでは赤を外す**
    # (2026-08-30 consistency/low: 15『3つ全部やめた場合』でも合計が RED の
    #  3,162円のままで、「やめた」のに「出ていく赤」が残っていた)
    total_ink = total_ink or RED
    def painter(fig, t):
        tn = _prog(t)                     # ナレーション進行度(第2の拍用)
        top = CARD_TOP
        # **パネル矩形は全部品共通の1組に固定**(2026-08-30 consistency/high)。
        # 中身が少ないときにカードを縮めると、隣接カットで下辺が跳ぶ
        bot = CARD_BOT
        left, right = CARD_L, CARD_R
        rh = (top - bot) / (n + 1)

        def rowy_b(i):
            return top - rh * (i + 2)

        # focus: 対象行を中心とした等方スケール(パンチイン)。
        # 位置は zx/zy、寸法・級数は *zk を通す
        zk = 1.0
        fcx, fcy = 0.5, (top + bot) / 2
        if focus is not None:
            # **往復のパンチイン**(2026-08-29 批評6周目)。行きは0.60で1.12倍、
            # t=0.85から0.15で1.0へ戻す。各ユニットの最終フレームが必ず
            # 正準グリッドに戻り、カット境界で表がポップしない
            zk = 1.0 + 0.12 * (_ease(t / 0.60) - _ease((t - 0.85) / 0.15))
            fcy = rowy_b(focus) + rh / 2
            if zk > 1.001:
                # ズーム後のカード上辺が文脈見出し(TITLE_Y)に食い込まないよう、
                # 拡大の中心を必要なぶんだけ上へ寄せる(上辺 <= 0.806)
                fcy = max(fcy, (0.806 - top * zk) / (1.0 - zk))

        def zx(v):
            return fcx + (v - fcx) * zk

        dyt = float_dy()      # 表の塊ごとゆっくり流す(完全静止フレームを作らない)

        def zy(v):
            return fcy + (v - fcy) * zk + dyt

        x_lab = zx(left + 0.045)      # ラベル列の共通の行頭
        x_val = zx(right - 0.06)      # 数値列の共通の右端
        r_card = 0.028
        card_border = card(fig, zx(left), zy(bot), (right - left) * zk,
                           (top - bot) * zk, lw=2.0 * zk, r=r_card * zk, z=2.0)
        # ---- 帯の矩形系統は**1本だけ**(2026-08-30 craft/high・consistency/high)。
        # 旧実装は「広い既定矩形(bx0_b/bw_bd)」と「枠の内側の矩形(fx0_b/fw_b)」の
        # 2系統を持ち、前回の修正は band() 側にしか入っていなかった。合計行を描く
        # hband(y0, rh, ap) は広い矩形のままだったので、**強調が合計行に乗るカットで
        # 必ず、赤枠の外側に地の帯が3.5〜4px露出していた**(実測 y=1060: 左 band
        # 83-86 → 赤枠 87-91、右 赤枠 971-976 → band 977-980。角では8px)。
        # 以後、帯・罫・枠はすべて (fx0_b, fw_b) を基準にし、縦も frame() の
        # インセット(+0.005 / rh-0.010)より内側に入る (+0.004 / rh-0.008) に揃える。
        pad_in = 0.010                 # カード内側の共通パディング(≒10.8px)
        INS_V = 0.005                  # 帯・枠の共通の縦インセット(frame と同値。
                                       # 帯の外縁が枠線(±2px)の内側に必ず入る)
        fx0_b = left + pad_in
        fw_b = (right - pad_in) - fx0_b
        r_band = r_card * 0.5          # 帯の角丸はカードの角丸からの派生値

        def hband(y_b, h_b, a_b, color=HEAD_BG, z_b=2.05, x0_b=None, w_b=None):
            if x0_b is None:
                x0_b, w_b = fx0_b, fw_b
            p_b = FancyBboxPatch(
                (zx(x0_b), zy(y_b)), w_b * zk, h_b * zk,
                boxstyle=f"round,pad=0,rounding_size={r_band * zk:.4f}",
                transform=fig.transFigure, facecolor=color, edgecolor="none",
                zorder=z_b, alpha=a_b, mutation_aspect=_ma())
            # 帯がカードの角丸から絶対にはみ出さないようにクリップする
            p_b.set_clip_path(card_border.get_path(), card_border.get_transform())
            fig.add_artist(p_b)

        def hrule(y_r, color, lw_r, z_r=2.4, alpha_r=1.0):
            """帯と同じ左右範囲の罫。**ピクセルグリッドにスナップする**。"""
            yy_r = F.snap_y(zy(y_r), lw_r)
            fig.add_artist(plt.Line2D([zx(fx0_b), zx(fx0_b + fw_b)], [yy_r] * 2,
                                      transform=fig.transFigure, color=color,
                                      linewidth=lw_r, zorder=z_r, alpha=alpha_r))

        # 見出し行
        hy = zy(top - rh / 2)
        hband(top - rh + INS_V, rh - 2 * INS_V, 1.0, z_b=2.1)
        hrule(top - rh, "#cfc4ae", 2.5 * zk)
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

        def band(y_hl, a_hl, color=RED_SOFT, ring=None):
            # 帯は枠(fx0_b/fw_b)と**同一の矩形**(craft/high の露出はここが原因)
            hband(y_hl + INS_V, rh - 2 * INS_V, a_hl, color=color, z_b=2.06)
            if ring is not None:
                # **行頭の役割色ガター**(2026-08-30 retention/medium)。
                # RED_SOFT(#f9e6dc)は白カード(#fffdf7)に対し輝度比1.16:1・
                # 最大チャンネル差27で、背景ドットのドリフト振幅(20)と同水準。
                # 表カットは動画の27%を占め、そのあいだこれが唯一の「指し棒」
                # だった。幅9pxの縦バーを行頭に置けば最大差分が200以上になる。
                g = plt.Rectangle((zx(fx0_b + 0.002), zy(y_hl + 0.006)),
                                  0.008 * zk, (rh - 0.012) * zk,
                                  transform=fig.transFigure, facecolor=ring,
                                  edgecolor="none", zorder=2.07, alpha=a_hl)
                g.set_clip_path(card_border.get_path(), card_border.get_transform())
                fig.add_artist(g)

        def frame(y_hl, a_hl, lw, squash=1.0, color=RED):
            # 縦インセット 0.005 / hh=rh-0.010(2026-08-29 批評6周目:
            # 旧 0.002 では枠の下辺が合計行上の黒罫と1px差で密着し、
            # 赤+黒の8px帯に融合していた)
            hh = (rh - 2 * INS_V) * squash
            yy = y_hl + INS_V + (rh - 2 * INS_V - hh) / 2
            fr = FancyBboxPatch(
                (zx(fx0_b), zy(yy)), fw_b * zk, hh * zk,
                boxstyle=f"round,pad=0,rounding_size={r_band * zk:.4f}",
                transform=fig.transFigure, facecolor="none",
                edgecolor=color, linewidth=lw,
                zorder=2.6, alpha=a_hl, mutation_aspect=_ma())
            fr.set_clip_path(card_border.get_path(), card_border.get_transform())
            fig.add_artist(fr)

        # 役割別のハイライト色(2026-08-29 批評6周目)。
        # warn=赤(損・警告) / neutral=墨リング+ベージュ地(単なる読み上げ位置)
        # keep=緑(止めて積む側に立った行)
        ring_col = {"neutral": NEUTRAL_RING, "keep": GREEN}.get(hl_role, RED)
        # 中立ハイライトの地は **NEUTRAL_SOFT**(HEAD_BG は見出し行・合計行と
        # 同色で、ハイライトとして見えていなかった。2026-08-30 artdirection/medium)
        band_col = {"neutral": NEUTRAL_SOFT, "keep": GREEN_SOFT}.get(hl_role, RED_SOFT)
        hb = max(0.0, math.sin(2 * math.pi * F.LAST_T / 1.8)) ** 3  # 鼓動位相
        # 第2の拍(2026-08-30 retention/high): ナレーション進行度72%で強調行の
        # 値が+8%ポップする。線幅・下線を足さずに、いま指している行を再宣言する
        pop2 = (1.0 + 0.08 * max(0.0, 1.0 - (tn - 0.72) / 0.10)
                if tn >= 0.72 else 1.0)
        hl_row = highlight if isinstance(highlight, int) else None
        if hl_row is not None:
            # build 中は、枠の出現を当該行テキストの出現(0.05+i*0.10)+0.06 に
            # 遅らせる(空の赤枠が先に立たない)
            gate_st = (0.05 + hl_row * 0.10 + 0.06) if build else 0.0
            if from_row is not None:
                u = _ease(t / 0.60)
                y_hl = rowy(from_row) * (1 - u) + rowy(hl_row) * u
                # 移動中は枠を少し透かす(2026-08-29 批評6周目: 滑走中の枠が
                # 行テキストの上を横切り、静止フレームで文字への線被りに写る)
                a_hl = 0.85 + 0.15 * _ease((u - 0.92) / 0.08)
                squash = 0.94 + 0.06 * u        # 移動中はつぶして、動きを読ませる
                # 地色は両行のクロスフェード(枠だけがすべる。移動中の中間位置に
                # 「どの行でもない場所の単独強調」を作らない)
                band(rowy(from_row), 1.0 - u, color=band_col)
                band(rowy(hl_row), u, color=band_col)
            elif hl_at is not None:
                # 着地をナレーション進行度に割り付ける(声より先に強調しない)
                y_hl = rowy(hl_row)
                a_hl = _ease((tn - hl_at) / 0.10)
                squash = 1.0
                band(y_hl, a_hl, color=band_col)
            else:
                y_hl = rowy(hl_row)
                a_hl = _ease((t - gate_st) / 0.30)
                squash = 1.0
                band(y_hl, a_hl, color=band_col)
            # **線幅は着地後に動かさない**(2026-08-30 consistency/medium)。
            # 同じ「ここを見ろ」の枠が、カットによって・また時刻によって
            # 4系統(5/5/6/6px、最大8px)の太さを取っていた。
            # 到着の1拍だけ EMPH_LW_PULSE を足し、以後は EMPH_LW に固定する。
            if t > 0.60:
                lw = EMPH_LW
            else:
                lw = EMPH_LW + EMPH_LW_PULSE * math.sin(
                    math.pi * min(1.0, max(0.0, (t - 0.30) / 0.30)))
            if a_hl > 0.01:
                # **第2の拍**(2026-08-30 retention/high)。16_hyo_1 は
                # 「使っていない1つだけでいい。」という転回の頂点で t0.80→t1.00 の
                # 全画面差分が17/255=完全静止だった。太さは動かさず(consistency)、
                # 枠の明度を一瞬持ち上げ、行の下に下線を左→右へスイープさせる。
                col2 = ring_col
                if tn >= 0.72:
                    u2 = max(0.0, 1.0 - (tn - 0.72) / 0.10)
                    col2 = _mix(ring_col, "#ffffff", 0.32 * u2)
                frame(y_hl, a_hl, lw * zk, squash, color=col2)
        elif highlight == "sweep" and detail_idx:
            # 問いのカット: 枠が明細行を**往復し続ける**(答えの行を指さない・
            # 最終行に停めない)。位相はナレーション進行度で刻む
            # (anim窓で止まると、ユニット後半に静止した「指し棒」が残る)
            span = max(1, len(detail_idx) - 1)
            ph = (tn / 0.42) * span
            k = ph % (2 * span)
            seg = 2 * span - k if k > span else k
            i0 = min(int(seg), span - 1) if span > 0 else 0
            # **各行で止まる**(2026-08-30)。等速で往復すると、どの静止フレームも
            # 「行と行のあいだで枠が文字を横切っている」絵になる。
            # 区間の前45%で移動し、残り55%はその行に停める。
            frac_s = min(1.0, max(0.0, seg - i0))
            u = _ease(min(1.0, frac_s / 0.45))
            i1 = min(i0 + 1, len(detail_idx) - 1)
            y_hl = rowy(detail_idx[i0]) * (1 - u) + rowy(detail_idx[i1]) * u
            # 移動中は枠を透かす(行テキストへの線被りを静止フレームに残さない)
            moving = 0.02 < frac_s < 0.45
            a_hl = _ease(t / 0.20) * (0.45 if moving else 1.0)
            band(y_hl, a_hl, color=band_col)
            frame(y_hl, a_hl, EMPH_LW * zk, color=ring_col)
        # wave の点灯はナレーション進行度で配分。**最終行の着地を tn≈0.92 まで
        # 引き延ばす**(2026-08-30 retention/high: 03_hyo_n は「1590円、1080円、
        # 492円。」を読み上げている最中に3行とも点灯済みで、t0.80→t1.00 の
        # 全画面最大差分が19/255=背景ドットのドリフト振幅以下だった)
        wave_step = (0.86 / max(1, len(detail_idx))) if detail_idx else 0.22
        wave_col = GREEN_SOFT if wave_role == "keep" else RED_SOFT
        for i, (a, b) in enumerate(rows):
            y0 = rowy(i)
            yc = y0 + rh / 2
            ap, dy = 1.0, 0.0
            if build:
                if build_at is not None and i < len(build_at):
                    # 行の出現をナレーション内の語位置に割り付ける
                    ap = _ease((tn - build_at[i]) / 0.10)
                else:
                    ap = _ease((t - 0.05 - i * 0.10) / 0.28)
                if ap <= 0.01:
                    continue
                dy = -(1 - ap) * 0.022
            if is_total[i]:
                # 合計帯もハイライト帯と**同一の矩形**(craft/high・consistency/high)
                hband(y0 + INS_V, rh - 2 * INS_V, ap)
                # 黒罫は行境界に置く。**赤リングが立つカットでは描かない**
                # (2026-08-30 consistency/high: 黒罫5px → ベージュ4px →
                #  赤リング6px の15px縞で、動画で最初の大リビール(3,162円)が
                #  囲まれていた。罫とリングを二重に見せない)
                if hl_row != i:
                    hrule(y0 + rh, INK, 3.5 * zk, alpha_r=ap)
            wave_lit = False
            wave_dim, nxt = False, 0.0
            if highlight == "wave" and not is_total[i]:
                # 明細行が順に点灯していく(点いたら消さない。点灯済みの行も
                # 地色がごく薄く呼吸して、表全体が生きて見える)。
                # keep は赤側と同じ band+frame の文法で、色だけ緑。
                # 枠は squash=0.90 で行間に最低10pxの地を確保する
                # (3本の枠が2〜3px間隔で繋がって見えていた)
                di = detail_idx.index(i)
                aw = _ease((tn - 0.06 - di * wave_step) / wave_step)
                wave_lit = aw > 0.5
                # **読み終わった行は沈める**(2026-08-30 retention/high)。
                # 点灯済みの行を地色のアルファで呼吸させるだけだと、いま読んでいる
                # 行がどれか分からなくなる。次の行が点き始めたら前の行を落とす。
                nxt = _ease((tn - 0.06 - (di + 1) * wave_step) / 0.25)
                wave_dim = nxt > 0.01 and di < len(detail_idx) - 1
                if aw > 0.01:
                    band(y0, min(1.0, aw) * (1.0 - 0.55 * nxt), color=wave_col,
                         ring=(GREEN if wave_role == "keep" else RED))
                    if wave_role == "keep":
                        frame(y0, min(1.0, aw) * (1.0 - 0.55 * nxt),
                              EMPH_LW * zk, squash=0.90, color=GREEN)
            hl = (hl_row == i)
            # dim は highlight が合計行でもマスクを保つ(問いのカットで枠を
            # 合計行へ滑らせても、開示は total_mode="red" のカットまで起きない)
            dim_total = (is_total[i] and total_mode == "dim")
            emph_ink = {"neutral": INK, "keep": GREEN_DARK}.get(hl_role, RED)
            lab_color = emph_ink if hl else INK
            if dim_total:
                # **ティーズセル(?,???円)の色は固定**(2026-08-30 consistency/medium)。
                # 旧 _mix(SUB, RED, 0.35*(0.5+0.5*idle)) は同じセルが (107,100,89) と
                # (131,77,70) のあいだを2.4秒周期で往復し、01・02・03 のカット末で
                # 位相が違うため、値も文字も変わっていないセルが境界で色だけポップ
                # していた。予告は色ではなく形(11_tsumu の「?」)で示す。
                val_color = SUB
            else:
                val_color = emph_ink if hl else (total_ink if is_total[i] else INK)
            if highlight == "wave":
                if wave_role == "keep" and wave_lit:
                    lab_color = GREEN_DARK   # 「残してよい」行は緑で点灯
                    val_color = GREEN_DARK   # 値も同じ文法
                if not is_total[i] and not wave_lit:
                    # まだ読んでいない行は明度でも落とす(帯の1.16:1を補う)
                    lab_color = _mix(lab_color, SUB, 0.35)
                    val_color = _mix(val_color, SUB, 0.35)
                elif wave_dim:
                    # 読み終わった行は沈める(いまの行だけが明るい状態を作る)
                    lab_color = _mix(lab_color, SUB, 0.45 * nxt)
                    val_color = _mix(val_color, SUB, 0.45 * nxt)
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
            # 金額は big_number 経由(単位は CJK52%/ラテン62%・数字のインク下端
            # に揃える)。表・棒・明細で単位の組み方が2系統に分裂していた
            # (2026-08-30 consistency/medium)
            if re.search(r"\d", shown_v):
                big_number(fig, x_val, zy(yc + dy), shown_v,
                           fs_v * zk * (pop2 if hl else 1.0), color=val_color,
                           t=1.0, count=False, z=2.3, max_w=0.44 * zk,
                           alpha=ap, ha="right")
            else:
                # マスクしたティーズセル(?,???円)は数字を含まないので直描き
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
        # **枠色は既定の CARD_EDGE**(2026-08-30 consistency/medium: timeline だけが
        # CARD_EDGE_STRONG を渡していて、23カット中このカットでだけ白パネルの
        # 輪郭がはっきり見え、カット境界で「枠が現れる/消える」に見えていた。
        # CARD_EDGE_STRONG は**カード内に置く小箱・チップ・吹き出し専用**)
        card(fig, CARD_L, CARD_BOT, CARD_R - CARD_L, CARD_TOP - CARD_BOT,
             r=0.028, z=2.1)
        tn = _prog(t)
        x0, x1 = 0.12, 0.88
        # 帯+目盛+キャレットの塊をカードの中央に置く(固定パネルの余白を上下対称に)
        y, h = 0.535 + float_dy(), 0.135
        def px(age):
            return x0 + (x1 - x0) * (age - start) / (end - start)
        xm = px(empty)
        # **帯の伸長はナレーション進行度で刻む**(2026-08-30 retention/high)。
        # 旧 `_ease(t/0.6)` は painter t=0.24 で最終幅の94%に達し、以後は先端が
        # ±4px呼吸するだけだった。約2.0秒のナレーションに対し、絵は最初の
        # 0.25秒で終わっていた(t0.50→t0.80 の変化画素 0.080%)。
        p = _ease(tn / 0.88)
        xm_t = x0 + (xm - x0) * p
        if p >= 1.0:
            # 着地後も先端が動きつづける(振幅±6px・三角波=速度一定)
            xm_t = xm + 0.006 * tri(period=1.2)
        fig.add_artist(FancyBboxPatch((x0, y), xm_t - x0, h,
                                      boxstyle="round,pad=0,rounding_size=0.018",
                                      transform=fig.transFigure, facecolor=fill_color,
                                      edgecolor="none", zorder=2.2,
                                      mutation_aspect=_ma()))
        S.text_fit(fig, (x0 + xm) / 2, y + h / 2, fill_label, ha="center", va="center",
                   color=fill_ink, fontsize=34, max_w=(xm - x0) * 0.92, zorder=2.4,
                   alpha=_ease((t - 0.25) / 0.25))
        # **年齢キャレット**: 帯の先端の上に「いまどこまで来たか」を数で出す。
        # 2秒かけて 35 から 65 へ転がるので、尻まで情報が前進する
        # (2026-08-30 retention/high。カード内の49%が空白だった件も埋まる)
        age_now = int(round(start + (empty - start) * p))
        a_car = _ease((t - 0.10) / 0.16)
        cx_car = min(max(xm_t, x0 + 0.06), x1 - 0.06)
        S.text_fit(fig, cx_car, y + h + 0.048, f"{age_now}歳", ha="center",
                   va="center", color=INK, fontsize=44 * beat(period=1.6, amp=0.06),
                   max_w=0.20, zorder=2.45, alpha=a_car,
                   fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)
        fig.add_artist(plt.Line2D([xm_t, xm_t], [y + h, y + h + 0.020],
                                  transform=fig.transFigure, color=INK,
                                  linewidth=3.0, zorder=2.45, alpha=a_car))
        # 帯の先端の明るいキャップ。**着地後もここだけは呼吸する**
        # (2026-08-30 retention/high: 塗り終わったあとの尻が完全静止だった)
        fig.add_artist(FancyBboxPatch(
            (xm_t - 0.016, y + 0.012), 0.014, h - 0.024,
            boxstyle="round,pad=0,rounding_size=0.007",
            transform=fig.transFigure,
            facecolor=_mix(fill_color, "#ffffff", 0.45), edgecolor="none",
            zorder=2.23, alpha=a_car * (0.45 + 0.55 * (0.5 + 0.5 * idle(period=1.1))),
            mutation_aspect=_ma()))
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
        # 基線: ティック上端の高さに INK 2px の水平線(2026-08-29 批評6周目:
        # 両端のティックの間が地色のままで、ティックが宙に浮いて見えた)
        fig.add_artist(plt.Line2D([x0, x1], [F.snap_y(y, 2.0)] * 2,
                                  transform=fig.transFigure,
                                  color=INK, linewidth=2.0, zorder=2.25))
        for lab, x, ha in ticks:
            tick_x = xm if lab == mid_lab else x
            fig.add_artist(plt.Line2D([F.snap_x(tick_x, 3.0)] * 2, [y - 0.030, y],
                                      transform=fig.transFigure,
                                      color=INK, linewidth=3.0, zorder=2.3))
            S.text_fit(fig, x, y - 0.058, lab, ha=ha, va="center",
                       color=AXIS_INK, fontsize=AXIS_FS, max_w=0.26, zorder=2.4)
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
            title: str = "", emph_color: str = None):
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
    # 答え・強調語の色。既定は損の赤。**得の側の式では緑を渡す**
    # (2026-08-30 kousei/medium: 「出さずに済む額」は止めて得る側の額)
    emph = emph_color or RED

    def painter(fig, t):
        fam = [F.NUM_FAMILY]
        fam_w = [F.FONT_FAMILY, F.FONT_FALLBACK_FAMILY]
        if name:
            # 立ち絵つきの旧レイアウト(1行組)。S033では未使用だが互換で残す
            F.draw_pose(fig, name, cx=0.5, top=0.845, height=0.315)
            top, bot = 0.495, 0.320
            fs_num = 60
            sc = 0.88 + 0.12 * _back(t / 0.30)
            card(fig, CARD_L, bot, CARD_R - CARD_L, top - bot, edge=RED,
                 lw=EMPH_LW, r=0.028, z=2.2, sc=sc)
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
        # **パネル矩形は固定**(2026-08-30 consistency/high)。旧実装は
        # `bot = 0.45 if answer else 0.475` で下辺を中身から逆算していたため、
        # 05/09(y1056)と19(y1008)と表(y1152)でパネル下端が3種類に割れ、
        # 04→05→06→07→08→09 の連続6カットすべてで下辺が跳んでいた。
        # 中身が余るぶんは上下対称の余白として残す。
        top, bot = CARD_TOP, CARD_BOT
        cyf = (top + bot) / 2
        y1, y2 = (cyf + 0.062, cyf - 0.052) if answer else (cyf + 0.048, cyf - 0.047)
        sc = 0.88 + 0.12 * _back(t / 0.30)
        card(fig, CARD_L, bot, CARD_R - CARD_L, top - bot, edge=emph,
             lw=EMPH_LW, r=0.028, z=2.2, sc=sc)
        fs1 = 64.0
        fs_op = fs1 * 0.60
        toks = [x for x in re.split(r"\s*([÷×+−=])\s*", line.strip()) if x]
        starts = [0.02, 0.16, 0.28, 0.38, 0.46]
        r = _renderer(fig)
        widths = []
        for tok in toks:
            if tok in "÷×+−=":
                w = F.measure_w(fig, r, tok, fs_op, fam, F.NUM_WEIGHT) + 0.034
            elif _is_num_token(tok):
                w = _num_w(fig, r, tok, fs1)
            else:
                w = F.measure_w(fig, r, tok, fs1 * 0.82, fam, F.NUM_WEIGHT)
            widths.append(w)
        total = sum(widths)
        k = min(1.0, 0.80 / total) if total else 1.0
        x = 0.5 - total * k / 2
        x_l1 = x          # 1行目の左端。**2行目の演算子をここに揃える**
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
                elif _is_num_token(tok):
                    big_number(fig, cx_t, y1, tok, fs1 * k, color=INK,
                               t=1.0, count=False, z=2.4,
                               max_w=w * k + 0.02, alpha=a)
                else:
                    fig.text(cx_t, y1, tok, ha="center", va="center", color=INK,
                             fontsize=fs1 * 0.82 * k, fontfamily=fam,
                             fontweight=F.NUM_WEIGHT, zorder=2.4, alpha=a)
            x += w * k
        # 下段: 答え(または note)。式の1.6倍・赤。カードの下半分を埋める
        st2 = FORMULA_ANS_ST
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
            # **演算子アンカー揃え**(2026-08-30 artdirection/medium)。
            # 両行を独立に中央揃えすると「=」が1行目の左端より外側に出て、
            # 導出ではなく「無関係な2行の並び」に読める(19 は実測で175pxはみ出し)。
            # 2行目は「=」の左辺を1行目の左端 x_l1 に合わせて左寄せで置く。
            k2a = (0.94 - x_l1) / (w_eq + w_ans)
            if k2a >= k2 * 0.80:
                k2 = min(k2, k2a)
                eq_w = w_eq * k2
                eq_cx = x_l1 + eq_w / 2
                ans_cx = x_l1 + eq_w + w_ans * k2 / 2
            else:                       # 20%詰めても入らないときだけ中央揃え
                eq_w = w_eq * k2
                ans_cx = 0.5
                eq_cx = ans_cx - w_ans * k2 / 2 - eq_w / 2
            fig.text(eq_cx, y2, "=", ha="center", va="center",
                     color=INK, fontsize=fs2 * 0.55 * k2, fontfamily=fam,
                     fontweight=F.NUM_WEIGHT, zorder=2.4, alpha=a2)
            big_number(fig, ans_cx, y2, answer,
                       fs2 * k2 * pop * b, color=emph,
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
            sw = sum(wsn)
            kn = min(1.0, 0.80 / sw) if sw else 1.0
            # 演算子アンカー揃え(2026-08-30 artdirection/medium)。
            # 幅を最大20%まで詰めてでも1行目の左端に合わせる。20%で足りない
            # ときだけ従来の中央揃えへ退避する
            avail = 0.94 - x_l1
            kn_a = (avail / sw) if sw else kn
            if kn_a >= kn * 0.80:
                kn = min(kn, kn_a)
                xn = x_l1
            else:
                xn = 0.5 - sw * kn / 2
            pop_n = 1.15 - 0.15 * _back((t - st2) / 0.22)
            # **第2の拍**(2026-08-29 批評6周目): ナレーション進行度75%で
            # 強調語(【】)がもう一度ポップし、下線がスイープする。
            # anim窓に全モーションを詰めると、2.5秒超のユニットは後半が止まる
            tn2 = _prog(t)
            pop2 = 1.0
            if tn2 >= 0.72:
                pop2 = 1.0 + 0.15 * max(0.0, 1.0 - (tn2 - 0.72) / 0.10)
            for (s2, em), fz, wn in zip(segs, sizes, wsn):
                fig.text(xn + wn * kn / 2, y2, s2, ha="center", va="center",
                         color=(emph if em else INK),
                         fontsize=fz * kn * ((pop_n * pop2) if em else 1.0),
                         fontfamily=fam, fontweight=F.NUM_WEIGHT,
                         zorder=2.4, alpha=a2)
                if em and tn2 >= 0.72:
                    usw = _ease((tn2 - 0.72) / 0.12)
                    fig.add_artist(plt.Line2D(
                        [xn, xn + wn * kn * usw], [y2 - 0.036] * 2,
                        transform=fig.transFigure, color=emph, linewidth=5.0,
                        solid_capstyle="round", zorder=2.4, alpha=a2))
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
    - tease=添字: その棒を**予告扱い**にする(丸ドット輪郭のみ+値は「?」)。
      「積んだらどうなるか」と問うカットで答えの263万円が満尺で立っていた。
      高さは本物のまま=形は見えるが数字は伏せる(むしろ引きが強い)
    - gain=添字: その棒が強調されたとき**緑(増える側の色)**にする。
      出ていく114万も増える263万も同じ赤で、売り物に固有の色が無かった
    - 伸長・カウントの窓 0.55→0.72(着地が早すぎて伸びる棒を見られる時間が
      1/3しか無かった)。着地後は値ラベル+棒の頭が同位相で鼓動

    2026-08-29 批評6周目:
    - items の第4要素(省略可)に opts dict: {"count": False} で
      **既知の数字の棒を数え直さない**(t=0.15までにポップで即置き)。
      114万円が4ユニット連続でフルカウントされ、情報前進が止まっていた。
      空いたアニメ予算は tease 棒のドローオン(0.15→0.45)に回す
    - ゴースト/予告棒の輪郭は**丸ドット**(capstyle=round + (0,(0.1,5.5)))。
      バットキャップの破線は角で位相が切れてノッチが出ていた
    - ゴーストの水平参照線は、ゴースト箱の上辺と一致する高さでは描かない
      (同一yの二重点線がモアレになっていた)
    - 着地後の値ラベルは big_number と同じ**1.8秒周期の鼓動**(±3.2%)
    - 色対応表(同一フレーム内で赤を2トーンにしない):
        強調中の損側   = 面 RED    / ラベル RED
        強調中の増側   = 面 GREEN  / ラベル GREEN_DARK
        非強調の損側   = 面 RED_FADE / ラベル LOSS_INK(褪せ赤の親子)
        役割なしの棒   = 面 WARM_GRAY / ラベル SUB
    """
    vals = [it[1] for it in items]
    topval = ymax or max(vals) * 1.22
    n = len(items)
    # **着地を t=0.90 まで引き延ばす**(2026-08-30 retention/high)。
    # 旧 WIN=0.72 + 三次イーズアウトでは、実測で棒高が t0.20 で最終比90%、
    # カウンタが t≈0.29 で値の90%に達し、基準の「t0.8で9割」の約2.8倍前倒し
    # だった。残り40%は255万→263万の3%しか動かず、t0.75〜1.00 の5サンプル
    # 連続で変化画素0.000%。
    WIN = BARS_WIN
    DOTTED = dict(linestyle=(0, (0.1, 5.5)), capstyle="round")
    def painter(fig, t):
        card(fig, CARD_L, CARD_BOT, CARD_R - CARD_L, CARD_TOP - CARD_BOT,
             r=0.028, z=2.0)
        # 棒の並びは**スロット中心に厳密に**置く(2026-08-30 consistency/low:
        # 棒の中心が 356.5/723.5 に対しスロット中心は 345.25/735.75 で±11〜12px
        # ずれ、基線の外側余白97px・内側148pxで棒が過大な横罫の上に浮いていた)。
        # 基線は「最外の棒の外縁 ± 棒幅の1/2」に切り詰める。
        x0i, x1i = 0.16, 0.84
        # 棒の領域はカードの高さを使い切る(固定パネルの死んだ余白を減らす)
        y0, y1 = 0.455, 0.720
        slot = (x1i - x0i) / n
        bw = slot * 0.60
        # **外側余白 = 内側余白 / 2** を規約にする(2026-08-30 consistency/low)。
        # 棒はスロット中心に置いてあるので、基線を x0i..x1i に取ると
        # 外側 (slot-bw)/2 ・内側 (slot-bw) でこの比が自動的に出る
        base_l, base_r = x0i, x1i
        # **棒の伸長は緩いバック**(2026-08-30 retention/medium)。
        # ease_out_back(1.70158)は t≈0.40〜0.45 に最終比+8.1%の頂点を作り、
        # そこから窓の30%かけて縮んでいた。「増える」を見せるカットの最後の
        # 可視モーションが下方向になっていた。
        p = _back_soft(t / WIN)
        hb = max(0.0, math.sin(2 * math.pi * F.LAST_T / 1.8)) ** 3   # 鼓動位相
        fam = [F.NUM_FAMILY]
        # ゴースト棒(前カットの値)。丸ドットの輪郭+薄いラベル
        if ghost:
            ag = _ease((t - 0.10) / 0.25)
            if ag > 0.01:
                g_tops = []
                for gi, gv in enumerate(ghost):
                    if not gv or gi >= n:
                        continue
                    gval, glab = gv
                    gh_ = (gval / topval) * (y1 - y0)
                    g_tops.append(y0 + gh_)
                    cxg = x0i + slot * (gi + 0.5)
                    grs = min(0.012, gh_ * 0.45)
                    # **点線ではなく面**(2026-08-30 artdirection/medium)。
                    # 点線だと角でダッシュ位相がリセットされず4隅が開き、
                    # 横29px/縦36pxで格子も揃わず、色 #ded4c2 は白カードの上で
                    # ほぼ汚れに見えていた。「前の値の影」という意味は面のほうが素直。
                    fig.add_artist(FancyBboxPatch(
                        (cxg - bw / 2, y0), bw, gh_,
                        boxstyle=f"round,pad=0,rounding_size={grs:.4f}",
                        transform=fig.transFigure, facecolor=WARM_GRAY,
                        edgecolor="none", zorder=2.04, alpha=0.18 * ag,
                        mutation_aspect=_ma()))
                    if glab:
                        # ラベルは枠から浮かせず、ゴースト面の上端に接して置く
                        fig.text(cxg, y0 + gh_ - 0.008, F.fmt_disp(glab),
                                 ha="center", va="top", color=SUB,
                                 fontsize=30, fontfamily=fam,
                                 fontweight=F.NUM_WEIGHT, zorder=2.06,
                                 alpha=0.85 * ag)
                gmax = max(gv[0] for gv in ghost if gv)
                ygl = y0 + (gmax / topval) * (y1 - y0)
                # ゴースト箱の上辺と同じ高さなら参照線は引かない(二重点線防止)
                if all(abs(ygl - gt) > 0.004 for gt in g_tops):
                    fig.add_artist(plt.Line2D([base_l, base_r], [ygl] * 2,
                                              transform=fig.transFigure,
                                              color=WARM_GRAY, linewidth=2.0,
                                              linestyle=(0, (0.1, 5.5)),
                                              solid_capstyle="round",
                                              dash_capstyle="round",
                                              zorder=2.05, alpha=0.5 * ag))

        def mix(c1, c2, u):
            from matplotlib.colors import to_rgba
            a, b = to_rgba(c1), to_rgba(c2)
            return tuple(a[i] * (1 - u) + b[i] * u for i in range(4))

        def bar_color(idx, hl_idx):
            # 役割ベース(2026-08-29 批評4周目): gain の文法があるカットでは、
            # 損側の棒は非強調でも褪せた赤(RED_FADE)を返す。同じ114万円が
            # カットごとに赤→灰と色を変え、同一性が切れて見えていた。
            # gain 未指定の図(役割の文法が無い比較)は従来どおり WARM_GRAY。
            # 強調中の損側は**ラベルと同じ RED**(面だけ一段明るい RED_FILL だと
            # 同一フレームに赤が2トーン並ぶ。2026-08-29 批評6周目)
            if hl_idx == idx:
                return GREEN if gain == idx else RED
            if gain is not None and gain != idx:
                return RED_FADE
            return WARM_GRAY

        for i, item in enumerate(items):
            lab, v, note = item[0], item[1], item[2]
            opts = item[3] if len(item) > 3 else {}
            cnt = opts.get("count", True)
            cx = x0i + slot * (i + 0.5)
            hl_now = (highlight == i)
            teased = (tease == i)
            col = bar_color(i, highlight)
            if prev_highlight is not None and prev_highlight != highlight:
                u = _ease(t / 0.35)
                col = mix(bar_color(i, prev_highlight), col, u)
            if teased:
                # 予告棒はドローオンで立ち上がる(既知棒の即置きの後)
                p_i = _ease((t - 0.15) / 0.30)
            elif not cnt:
                # 既知の数字の棒は即置き(数え直さない)
                p_i = _back(t / 0.15)
            else:
                p_i = p
            # 着地インパルス(棒・ラベル・SEを**同一フレーム**で揃える)
            land_i = WIN if cnt else 0.20
            pop_i = max(0.0, 1.0 - (t - land_i) / 0.10) if t > land_i else 0.0
            h = (v / topval) * (y1 - y0) * p_i
            if hl_now:
                # 着地の瞬間に20px級で跳ね、以後は1〜2pxの呼吸
                h *= 1.0 + 0.020 * pop_i + (0.004 * hb if t >= land_i else 0.0)
            if teased and h > 0.004:
                # 予告棒: 丸ドットの輪郭のみ(面は塗らない)。数字は下で「?」になる
                # **空欄であることを色と太さで予告する**(2026-08-30 retention/medium)。
                # 旧: WARM_GRAY 3.5px の点線 + 64pt の灰色「?」で、出現時の変化画素は
                # 0.05%。カード内の79%が空白のまま、画面の1/2000の要素が引きを
                # 担っていた。輪郭を 6.0px・緑寄りにし、「ここに緑の答えが入る」を
                # 色で予告する(この棒は fueru で GREEN になる=増える側)。
                # **ドットは4隅を固定点にして辺ごとに等分する**(2026-08-30
                # craft/medium)。matplotlib の linestyle 破線は、矩形の周長が
                # ピッチの整数倍でないかぎり角で位相が合わず、片方の角に
                # 80pxのL字の欠け、反対の角にほぼ接触した2点が同時に出る。
                # 下辺は基線(墨の太線)と重なるので描かない
                F.dotted_rect(fig, cx - bw / 2, y0, bw, h, pitch=0.011,
                              r=0.0035, color=_mix(GREEN, "#ffffff", 0.45),
                              zorder=2.1, skip_bottom=True)
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
            elif m and cnt:
                pre, digits, suf = m.groups()
                # **big_number と同じ緩い指数**(t=0.8 で9割・t=1.0 で満)。
                # 三次イーズアウトは前倒しが強すぎて、残り時間が判別不能だった
                u_c = min(1.0, max(0.0, t / WIN))
                val = int(round(int(digits) * (1.0 - (1.0 - u_c) ** 1.7)))
                if t >= WIN:
                    val = int(digits)
                shown = pre + (f"{val:,}" if len(digits) >= 4 else str(val)) + suf
            else:
                shown = note      # count=False は最終値を即置き
            # 値ラベルは棒トップに詰める(0.012≈23pxの空隙で帰属が一瞬迷う。
            # 2026-08-29 批評4周目: 棒トップ+約10pxに固定。追従は現行のまま)
            y_v = y0 + h + 0.005
            land = WIN if cnt else 0.20
            if teased:
                # 予告の「?」: 出現を前倒し(0.55→0.42)・級数 64→110、
                # 出現後は**ナレーション進行度**で 1.1秒周期・±6% の脈動+明滅。
                # 旧 hb はグローバル時計で位相がユニットに揃わなかった。
                aq = _back((t - 0.42) / 0.16)
                if aq > 0.01:
                    tnq = _prog(t)
                    puls = math.sin(2 * math.pi * tnq * (S.SUB_TIME[1] / 1.1
                                                         if getattr(S, "SUB_TIME", None)
                                                         and S.SUB_TIME[1] else 2.0))
                    fs_q = 110.0 * min(1.0, aq) * (1.0 + 0.06 * puls)
                    fig.text(cx, y_v, "?", ha="center", va="bottom",
                             color=GREEN_DARK, fontsize=fs_q, fontfamily=fam,
                             fontweight=F.NUM_WEIGHT, zorder=2.4,
                             alpha=_ease((t - 0.42) / 0.10)
                             * (0.875 + 0.125 * puls))
            elif hl_now:
                # **着地ポップ**(2026-08-30 retention/high)。旧実装は
                # `fs_v *= 1.0 + 0.032*hb` だけで、hb はユニットに同期しない
                # 1.8秒周期のグローバル時計。着地の瞬間にインパルスが立たず、
                # 動画の最大リビール(263万円)が「桁の更新が止まる」だけで
                # 着地していた(t0.80→t1.00 のカード内変化画素 0.00%)。
                # hero(big_number)には +22%+白振りの着地ポップがあり、
                # 実測で変化画素11.75%のスパイクが立っているのに、bars だけが
                # 取り残されていた。棒・ラベル・SEを同一フレームで揃える。
                v_col = GREEN_DARK if gain == i else RED
                fs_v = 60.0
                if pop_i > 0.0:
                    fs_v *= 1.0 + 0.22 * pop_i
                    v_col = _mix(v_col, "#ffffff", 0.35 * pop_i)
                if t > land:
                    fs_v *= 1.0 + 0.012 * math.sin(2 * math.pi * F.LAST_T / 0.9)
                big_number(fig, cx, y_v + 0.020, shown, fs_v, color=v_col,
                           t=1.0, count=False, z=2.4, max_w=slot * 1.02,
                           path_effects=_halo(60))
            else:
                # 非強調の級数 36→44(最大値の棒に最小の文字、の逆転を緩和)。
                # gain の文法があるカットの損側は褪せ赤の文字(色の同一性)
                c_lab = LOSS_INK if (gain is not None and gain != i) else SUB
                big_number(fig, cx, y_v + 0.015, shown, 44.0, color=c_lab,
                           t=1.0, count=False, z=2.4, max_w=slot * 1.02)
            S.text_fit(fig, cx, y0 - 0.020, lab, ha="center", va="top",
                       color=AXIS_INK, fontsize=AXIS_FS, max_w=slot * 0.96,
                       zorder=2.4)
        # 基線(地面)。左右端は最外の棒の外縁±棒幅の1/2に切り詰め、
        # y はピクセルグリッドへスナップする(craft/low)
        fig.add_artist(plt.Line2D([base_l, base_r], [F.snap_y(y0, 3.5)] * 2,
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
            # **パネル矩形は固定**(2026-08-30 consistency/high)。
            # 旧実装は数字の高さから下辺を逆算していたため、17_hitotsu が y906、
            # 08_kikan が y1105 と、同じ役割のパネルの下端が5種類に割れていた。
            # 数字が小さく見えるのが問題なら**級数の上限を上げてパネルを埋める**。
            top, bot = CARD_TOP, CARD_BOT
            fs = _fit_num_fs(fig, main, 340.0, 0.86)
            fs = min(fs, (top - bot) * 0.62 * S.H * 72 / S.DPI)
            head = 0.0
            # 文脈見出しはカードの外(上の帯を埋め、視線アンカーを揃える)。
            # count=False のヒーローは見出しを遅延ポップさせて第2拍を作る
            # (2026-08-29 批評6周目: 行動提案の核が静止カード1枚だった)
            if count:
                head_title(fig, sub, t)
            else:
                head_title(fig, sub, max(0.0, (_prog(t) - 0.50) * 3.0))
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
                # 打消し表示は**注記帯と同一トークン**(2026-08-30 consistency/low)。
                # 旧 INK 34pt はカード内で本文並みの濃さ・大きさになり、
                # 同じ役割の注記帯(DISCLAIM 26pt)より目立っていた。
                S.text_fit(fig, 0.5, bot + 0.052, F.fmt_disp(caption), ha="center",
                           va="center", color=F.DISCLAIM, fontsize=26, max_w=0.78,
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
        elif count:
            big_number(fig, 0.5, cy, main, fs * b, color=hero_col,
                       t=t, count=True, z=2.4, max_w=0.84 * b)
        else:
            # count=False でも無演出にしない(2026-08-29 批評6周目):
            # 前カットの表の強調行の位置(y≈0.598)から数字がスライドインし
            # (マッチカット)、t=0.25で+22%の着地ポップ、以後は鼓動
            a_n = _ease((t - 0.08) / 0.12)
            if a_n > 0.01:
                ps = _back((t - 0.08) / 0.20)
                yy = 0.598 + (cy - 0.598) * ps
                pop = 1.0
                if t >= 0.25:
                    pop += 0.22 * max(0.0, 1.0 - (t - 0.25) / 0.12)
                big_number(fig, 0.5, yy, main, fs * b * pop, color=hero_col,
                           t=1.0, count=False, z=2.4, max_w=0.84 * b * pop,
                           alpha=a_n)
    return painter


def arrow(left_val: str, right_val: str, left_lab: str = "", right_lab: str = "",
          title: str = "", scale_right: float = 1.0, role: str = "loss",
          accent: str = "right", arrow_color: str = None):
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
    # **矢印が主役でないカットでは矢印を背景側へ落とす**(2026-08-30
    # artdirection/medium)。支払いの答えを見せるカットで、最も視覚重量の
    # ある要素が #2c2c2c の中実ポリゴン(152×90px)になっていて、
    # 263万円(#4d7a33)よりコントラストが高く、最初に目が行くのが方向記号だった。
    a_col = arrow_color or (INK if accent == "arrow" else WARM_GRAY)

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
        card(fig, xl, cy - hb / 2, wl, hb, edge=l_edge, lw=EMPH_LW,
             r=0.022, z=2.2, alpha=a_l)
        big_number(fig, xl + wl / 2, cy + 0.008, left_val, fs_l, color=l_ink,
                   t=1.0, count=False, z=2.4, max_w=wl * 0.80 if is_word
                   else wl - 0.05, alpha=a_l)
        # 矢印: 左箱の着地後、左→右へドローオン(先端の比率は崩れない)。
        # **左右のクリアランスを実描画端で揃える**(2026-08-30 craft/high:
        # 実測で左14px・右24pxの非対称になっていた)
        gap_a = 0.014
        x0, x1 = xl + wl + gap_a, xr - gap_a
        u = _ease((t - 0.16) / 0.28)
        # 右箱: 矢先の到達(見た目上 t≈0.33)と同時にポップを始め、
        # **0.10以内に数字**が入る(2026-08-29 批評4周目: 矢印が完成済みなのに
        # 右箱不在=矢印が空白を指す静止フレームが約14%の窓で出ていた)
        pr = _back((t - 0.34) / 0.20)
        pulse = math.sin(math.pi * min(1.0, max(0.0, (t - 0.34) / 0.28)))
        if pr > 0.01:
            # **着地後は線幅を固定**(2026-08-30 craft/high・consistency/medium)。
            # 旧 `EMPH_LW + 1.5*(0.5+0.5*idle(0.8))` は t>0.80 以降も 4.75〜6.25pt を
            # 往復し続け、左の赤箱5.60px に対し右の緑箱6.84px という食い違いを
            # 静止フレームに残していた。1080p では線幅が毎フレーム再サンプリング
            # され、AAエッジがクロールして「強調」ではなく破綻に見える。
            lw_r = EMPH_LW + EMPH_LW_PULSE * pulse if t <= 0.80 else EMPH_LW
            # 矢先が右箱に当たる瞬間のスカッシュ(縦-6%・0.1秒。
            # 2026-08-29 批評6周目: ユニット後半の静止を消す第2拍)
            hsq = 1.0 - 0.06 * math.sin(
                math.pi * min(1.0, max(0.0, (t - 0.34) / 0.10)))
            hr_d = hr * hsq
            if emph:
                card(fig, xr, cy - hr_d / 2, wr, hr_d, edge=hi_edge, lw=lw_r,
                     r=0.022, z=2.2, sc=min(1.0, pr) + 0.04 * pulse)
            else:
                card(fig, xr, cy - hr_d / 2, wr, hr_d, edge=CARD_EDGE_STRONG,
                     lw=EMPH_LW, r=0.022, z=2.2, sc=min(1.0, pr))
            a_r = _ease((t - 0.44) / 0.12)
            if a_r > 0.01:
                pop = 1.18 - 0.18 * _back((t - 0.44) / 0.18)
                b = beat() if t > 0.85 else 1.0
                big_number(fig, xr + wr / 2, cy + 0.008, right_val,
                           fs_r * pop * b, color=(hi_ink if emph else INK),
                           t=1.0, count=False, z=2.4,
                           max_w=(wr * 0.80 * 1.10) if is_word
                           else (wr - 0.05) * 1.10, alpha=a_r)
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
                           va="center", color=AXIS_INK, fontsize=AXIS_FS,
                           max_w=wb + 0.04, zorder=2.4, alpha=al)
        # 矢印本体(常に cy に乗る)。**矢先の位置は着地後に動かさない**
        # (2026-08-30 craft/high: `xe += 0.004*idle(0.7)` で矢先が±4.3px
        #  滑り続け、頂点が毎フレーム再サンプリングされていた)
        if u > 0.02:
            xe = x0 + (x1 - x0) * u
            hl_, hw, sh = 0.045, 0.042, 0.014
            if accent == "arrow":
                # 矢印が主役のカットの強調は太さで(色は変えない)
                hl_, hw, sh = hl_ * 1.3, hw * 1.3, sh * 1.3
            xs = max(x0, xe - hl_)
            _arrow_patch(fig, x0, xs, xe, cy, sh, hw, a_col, z=2.5)
        # **左の値が矢印に乗って右へ飛ぶ**(2026-08-30 retention/medium)。
        # 「同じ3162円が、積む側に変わる。」という変換を語るカットで、絵は
        # 静止した2箱+静止した矢印だった(t0.50→t0.80 の変化画素0.396%、
        # 変化は数字の鼓動のみ)。左から右への移動を1つ入れる。
        if 0.30 <= t <= 0.58:
            uf = _back((t - 0.30) / 0.25)
            af = 1.0 - _ease((t - 0.45) / 0.13)
            if af > 0.01:
                xf = (xl + wl / 2) + ((xr + wr / 2) - (xl + wl / 2)) * uf
                big_number(fig, xf, cy + 0.008, left_val,
                           fs_l * (1 - 0.35 * min(1.0, uf)), color=l_ink,
                           t=1.0, count=False, z=2.45,
                           max_w=(wl - 0.05) * 1.2, alpha=af * 0.85)
    return painter


def _arrow_patch(fig, x0, xs, xe, cy, sh, hw, color, z=2.5):
    """角丸+落ち影つきの矢印。**joinstyle と capstyle を必ず指定する。**

    2026-08-30 craft/high: 旧実装は plt.Polygon(角丸ゼロ・影ゼロ・joinstyle未指定)
    で、カード・箱だけが影を持ち矢印だけが無影という様式の割れが出ていた。
    """
    from matplotlib.path import Path
    r = 0.008
    ry = r * (S.W / S.H)
    verts = [(x0 + r, cy - sh)]
    codes = [Path.MOVETO]

    def line(p):
        verts.append(p); codes.append(Path.LINETO)

    def curve(c, p):
        verts.extend([c, p]); codes.extend([Path.CURVE3, Path.CURVE3])

    line((xs, cy - sh))
    line((xs, cy - hw))
    line((xe, cy))
    line((xs, cy + hw))
    line((xs, cy + sh))
    line((x0 + r, cy + sh))
    curve((x0, cy + sh), (x0, cy + sh - ry))
    line((x0, cy - sh + ry))
    curve((x0, cy - sh), (x0 + r, cy - sh))
    codes.append(Path.CLOSEPOLY); verts.append((x0 + r, cy - sh))
    drop_shadow(fig, x0, cy - hw, max(0.01, xe - x0), 2 * hw, r=r, z=z - 0.02,
                alpha=0.55)
    fig.add_artist(PathPatch(Path(verts, codes), transform=fig.transFigure,
                             facecolor=color, edgecolor="none", zorder=z,
                             joinstyle="round", capstyle="round"))


def _relation_glyph(fig, cx, cy, kind: str, size: float, color, z=2.45):
    """左右を関係づける記号(arrow / lt / gt)を**同じ線幅・角丸・影**で描く。

    size は箱の高さに対する固定比で渡す(compare は 0.42*hb)。
    """
    lw = 9.0
    dy = size / 2
    dx = dy * (S.H / S.W) * 0.72
    sgn = 1.0 if kind == "lt" else -1.0
    pts = [(cx + sgn * dx, cy + dy), (cx - sgn * dx, cy), (cx + sgn * dx, cy - dy)]
    drop_shadow(fig, cx - dx * 1.2, cy - dy, dx * 2.4, dy * 2, r=0.008,
                z=z - 0.02, alpha=0.40)
    fig.add_artist(plt.Line2D([p[0] for p in pts], [p[1] for p in pts],
                              transform=fig.transFigure, color=color,
                              linewidth=lw, solid_joinstyle="round",
                              solid_capstyle="round", zorder=z))


def compare(left_val: str, right_word: str, left_lab: str = "",
            right_lab: str = "", title: str = "", role: str = "neutral"):
    """左=数字、右=比較対象(語)の並置比較。あいだに「<」を置く。

    role="loss": 左の数字を褪せ赤(LOSS_INK)にする(2026-08-29 批評6周目:
    05・06で赤=出ていく側だった105円が、直後の比較で無彩の墨になり
    色の同一性追跡が切れていた。「非強調だが出ていく側」は RED_FADE 文法)。

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
        # 内箱の左右マージンを広げる(2026-08-30 artdirection/high:
        # 箱がカード壁から23pxしか離れておらず、箱間157pxとの比が1:3.7だった)
        wl, hb = 0.31, 0.16
        xl, xr = 0.105, 0.895 - wl
        # 左(数字)は即置き。開示済みの数字なのでカウントしない
        a_l = _ease(t / 0.16)
        fs_l = _fit_num_fs(fig, left_val, 96.0, wl - 0.06)
        l_ink = LOSS_INK if role == "loss" else INK
        l_edge = LOSS_EDGE if role == "loss" else CARD_EDGE_STRONG
        card(fig, xl, cy - hb / 2, wl, hb, edge=l_edge, lw=EMPH_LW,
             r=0.022, z=2.2, alpha=a_l)
        big_number(fig, xl + wl / 2, cy + 0.006, left_val, fs_l, color=l_ink,
                   t=1.0, count=False, z=2.4, max_w=wl - 0.06, alpha=a_l)
        # 関係記号。**arrow() と同じ図形ヘルパーから描く**(2026-08-30
        # consistency/low: 06 は活字の「<」(高さ約60px・影なし)、14 は161px幅の
        # 黒ベタ矢印(角丸ゼロ・影なし)で、同じ「左箱→記号→右箱」の系列なのに
        # 一方が文字・一方が図形だった)
        a_m = _ease((t - 0.30) / 0.14)
        if a_m > 0.01:
            stamp = 1.0 + 0.4 * (1 - _ease((t - 0.30) / 0.20))
            _relation_glyph(fig, 0.5, cy, "lt", hb * 0.42 * stamp, WARM_GRAY)
        # 右(比較対象の語)がポップイン=このカットの主役の動き
        pr = _back((t - 0.40) / 0.22)
        if pr > 0.01:
            a_r = _ease((t - 0.40) / 0.14)
            b = beat() if t > 0.85 else 1.0
            card(fig, xr, cy - hb / 2, wl, hb, edge=CARD_EDGE_STRONG, lw=EMPH_LW,
                 r=0.022, z=2.2, sc=min(1.0, pr))
            fs_r = _fit_num_fs(fig, right_word, 96.0, wl - 0.08)
            big_number(fig, xr + wl / 2, cy + 0.006, right_word, fs_r * b,
                       color=INK, t=1.0, count=False, z=2.4,
                       max_w=(wl - 0.08) * 1.05, alpha=a_r)
        # ラベルは各箱の直下
        for x0b, lab, al in ((xl, left_lab, a_l),
                             (xr, right_lab, _ease((t - 0.46) / 0.14))):
            if lab and al > 0.01:
                S.text_fit(fig, x0b + wl / 2, cy - hb / 2 - 0.042, lab,
                           ha="center", va="center", color=AXIS_INK,
                           fontsize=AXIS_FS, max_w=wl + 0.04, zorder=2.4,
                           alpha=al)
    return painter


def cta(line: str, name: str = "02_point", show_button: bool = False,
        show_comment: bool = False, bubble: str = "月いくら?", title: str = "",
        button_label: str = "チャンネル登録"):
    """締めの定型カット。競合は結論のあと**4カット**使っていた。

    2026-08-29: ボタン・吹き出しは ease_out_back で着地したあと呼吸パルス。
    「コメント」の吹き出しはキャラの頭の横に置き、しっぽを画面右下
    (コメント欄アイコンの方向)へ向ける。字幕の真上には置かない。
    2026-08-29 批評3周目: 呼吸を動画内時刻(idle)で回す(tだと尺の後半で
    止まる)。「コメント」バッジは0.9秒周期のスケールパルスでタップ対象と示す。
    """
    def painter(fig, t):
        # **裾を字幕の直上まで通す**(2026-08-30 artdirection/medium):
        # 旧 height=0.40 では裾が y1005 で終わり、字幕上端 y1362 まで319pxが
        # 空洞だった。person_bubble / person_cards と top を共有し、height だけで
        # 大きさを変えて、ユニット間で裾の終端 y を揃える。
        F.draw_pose(fig, name, cx=0.40 if show_comment else 0.5,
                    top=POSE_TOP_STD, height=0.45 if show_comment else 0.47)
        head_title(fig, title, t)
        breath = 1.0 + 0.020 * idle(period=1.3)
        if show_button:
            # 行動ボタンは**吹き出しの外・カード幅の中央に置く独立したピル**
            # (2026-08-30 artdirection/medium: 唯一の行動語が画面最小・最低
            #  コントラストで、しかも吹き出しの枠線に食い込んでいた)
            p = _back((t - 0.15) / 0.25)
            if p > 0.01:
                s = p * breath
                bw, bh = 0.46 * s, 0.055 * s
                by_ = clamp_above_subtitle(0.40)
                drop_shadow(fig, 0.5 - bw / 2, by_, bw, bh, r=R_MD, z=2.48)
                fig.add_artist(FancyBboxPatch(
                    (0.5 - bw / 2, by_), bw, bh,
                    boxstyle=f"round,pad=0,rounding_size={R_MD}",
                    transform=fig.transFigure, facecolor=GREEN_DARK,
                    edgecolor="none", zorder=2.5, mutation_aspect=_ma()))
                S.text_fit(fig, 0.5, by_ + bh / 2, F.fmt_disp(button_label),
                           ha="center", va="center", color="#ffffff",
                           fontsize=40 * s, max_w=bw - 0.05, zorder=2.6)
        if show_comment:
            # 吹き出しの中身は画面の問いと呼応する「月いくら?」。
            # 「コメント」は機能表示なのでバッジ状の小ラベルに格下げ(2026-08-29
            # 批評2周目)。しっぽは**話者(左の立ち絵の顔)へ向ける**。右下の
            # 何もない空間を指していて、話者から切り離れて見えていた
            p = _back((t - 0.15) / 0.25)
            if p > 0.01:
                s = p * breath
                # **ループの手渡し**(2026-08-29 批評6周目): ナレーション進行度
                # 80%で吹き出しが+8%ポップ+2度チルト。最終フレームが動いている
                # 状態でループ先頭(カバー)へ返す
                tnc = _prog(t)
                pop2 = max(0.0, 1.0 - (tnc - 0.80) / 0.14) if tnc >= 0.80 else 0.0
                s *= 1.0 + 0.08 * pop2
                rot2 = 2.0 * pop2
                # 寸法は person_bubble と**同じモジュール定数**を使う
                # (2026-08-30 consistency/medium: 同じ吹き出し部品なのに
                #  幅-8%・高さ-25%ちがっていた)
                bw, bh = BUBBLE_W, BUBBLE_H
                # 右端は 0.95 まで(実機の右レール x>0.888 にUI要素を置かない
                # 規約は守りつつ、吹き出しは話者の隣に置く)
                bx, by = 0.95 - bw, 0.615
                cxb = bx + bw / 2
                cyb = by + bh / 2 + 0.002 * idle(period=1.1)
                bw2, bh2 = bw * s, bh * s
                x_b, y_b = cxb - bw2 / 2, cyb - bh2 / 2
                # **しっぽ込みで1本の閉じた輪郭**(craft/high)。上辺に差し込む
                # ので、bubble_path を上下反転した座標で作る
                from matplotlib.transforms import Affine2D
                # しっぽは**短く**して話者の側へ向ける(長い槍だと
                # 「旗」に見えて吹き出しの語彙から外れる)
                tail = [(cxb - bw2 * 0.36, y_b), (cxb - bw2 * 0.42,
                                                  y_b - 0.026 * s),
                        (cxb - bw2 * 0.14, y_b)]
                path = F.bubble_path(x_b, y_b, bw2, bh2, 0.030 * s, tail)
                path = path.transformed(
                    Affine2D().translate(0, -cyb).scale(1, -1).translate(0, cyb))
                drop_shadow(fig, x_b, y_b, bw2, bh2, r=0.030, z=2.49)
                fig.add_artist(PathPatch(
                    path, transform=fig.transFigure, facecolor=CARD,
                    edgecolor=CARD_EDGE_STRONG, linewidth=4.0,
                    joinstyle="round", capstyle="round", zorder=2.5))
                S.text_fit(fig, cxb, cyb, F.fmt_disp(bubble), ha="center",
                           va="center", color=F.BAND_INK, fontsize=BUBBLE_FS * s,
                           max_w=0.32, zorder=2.6, rotation=rot2)
                # 機能ラベル「コメント」: 吹き出し**左下**の小さいバッジ。
                # 右下アンカーだと右端が x≈0.93 に達し、Shorts実機の右レール
                # UI(いいね/コメント/共有)に食われる(2026-08-29 批評4周目)。
                # **x>0.888(右120px)にはインタラクティブ要素を置かない。**
                # タップ対象であることは 1.6秒周期のスケール鼓動で示す
                # ピルの色はブランドの帯文字色(BAND_INK)+クリーム文字に接続
                # (2026-08-29 批評5周目: 黒充填チップはシステム内唯一の一点物
                # だった)。角丸もカード系の 0.022 に揃える
                # **UIチップは不透明**(2026-08-30 craft/high)。旧
                # `a_ch = 0.78 + 0.22*(0.5+0.5*idle(0.9))` は面と文字の両方に掛かり、
                # 拡大すると吹き出しの枠線がチップを横断して見え、髪の束が
                # チップ内に透けていた。タップ対象の合図はスケール拍(sb)に任せ、
                # 輝度で示したいぶんは**不透明度ではなく面の色**で取る。
                sb = s * beat(period=1.6, amp=0.05)
                mixv = 0.12 * (0.5 + 0.5 * idle(period=0.9))
                chw, chh = 0.155 * sb, 0.042 * sb
                # チップは吹き出しの**外**(下)に置く。枠線に食い込ませない
                chx, chy = cxb - bw2 / 2, cyb - bh2 / 2 - chh - 0.012
                chx = min(chx, 0.82 - chw)
                fig.add_artist(FancyBboxPatch(
                    (chx, chy), chw, chh,
                    boxstyle=f"round,pad=0,rounding_size={R_MD}",
                    transform=fig.transFigure,
                    facecolor=_mix(F.BAND_INK, CARD, mixv),
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
