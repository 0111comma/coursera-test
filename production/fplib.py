#!/usr/bin/env python3
"""新デザイン(自前キャラ・明るい背景)のテーマ。

competitor-shorts-teardown-2026-08-23.md の実測にもとづく:

| | 競合(@bankacademy) | 旧デザイン |
|---|---|---|
| 画面の明るさ | 0.771 | 0.141 |
| 字幕1行の高さ | 5.7%(2行常用) | 3.8% |
| 上部 | タイトル帯を固定 | なし |

**既存30本を壊さないため、shortlib は直さずに、ここから差し替える。**
`use_fp_theme()` を render.py の先頭で1回呼ぶ。
"""
import math
import re
from pathlib import Path

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
from PIL import Image

import shortlib as S

ROOT = Path(__file__).resolve().parent.parent
POSE_DIR = ROOT / "assets" / "character"
FONT_DIR = ROOT / "assets" / "fonts"

# **RocknRoll One**(2026-08-24、ユーザーが6書体を見比べて選定)。
# 前は M PLUS Rounded 1c Black だったが「すごいダサい。デフォルトっぽくてダサい」
# との指摘で差し替えた。日本語の無料フォントで最も使われている書体だったので、
# 見飽きられていた。OFL 1.1・商用可。assets/fonts/README.md に出典と確認日。
#
# **ウェイトは400の1つだけ。**900やboldを指定すると findfont が警告を出す。
FONT_FAMILY = "RocknRoll One"
FONT_WEIGHT = 400
FONT_GLOB = "RocknRollOne.ttf"

# **記号のフォールバック**(2026-08-24)。
# RocknRoll One は日本語の本文はそろっているが、記号が9字足りない:
#     ※ ← → ① ② ③ ▼ ◯ ㊹
# → は10本、▼ は9本の動画で使っていて、別の字に置き換えると意味が変わる。
# matplotlib 3.6 以降は font.family にリストを渡すと**字ごとに**後ろへ落ちるので、
# 日本語は RocknRoll One、足りない記号だけ IPAGothic で埋める。
# (置換ではなく埋めるので、台本を書くときに記号を避けなくてよい)
FONT_FALLBACK = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
FONT_FALLBACK_FAMILY = "IPAGothic"

# **ヒーロー数字・強調語の第2書体**(2026-08-29 批評ループ)。
# RocknRoll One はウェイトが400の1つだけで、大きい数字に「重さ」が出ない。
# 金額・強調語だけ Noto Sans CJK JP Black(OFL/システム同梱)で極太に打ち、
# 本文は RocknRoll One のままにしてウェイト差で階層を作る。
NUM_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
NUM_FAMILY = "RocknRoll One"       # _setup_font が実在を確認して差し替える
NUM_WEIGHT = 900

# ---- 配色(競合の実測値に寄せた)
CREAM = "#f3e7d3"          # 背景。明るさ 0.75 前後
DOT = "#f9f1e3"            # 背景のドット。地との差を2倍に(2026-08-29 批評5周目。
                           # #f6ecdb は差が小さすぎ、ドリフトが知覚不能で
                           # 「完全静止フレームを作らない」の設計意図を満たせなかった)
BAND = "#f8cf5a"           # 上部のタイトル帯(下側)。2026-08-29 批評5周目:
                           # 帯が全フレームで最高彩度・最大面積となり、各カットの
                           # 結論(赤・緑の数字)より先に目を引いていた → 15%減彩
BAND_LO = "#eeaf3b"        # 帯の上側。**縦のグラデーション**にする(同・15%減彩)
BAND_INK = "#3b2c10"       # 帯の文字
TELOP = "#ffffff"          # テロップの本文
TELOP_EMPH = "#ffb020"     # テロップの強調(数字)。#ffd93d は帯(#f9cb45)と同色相で
                           # クリーム地に沈んでいた → 一段濃いアンバー(2026-08-29)
TELOP_EDGE = "#7b2d00"     # テロップの縁
TELOP_EDGE_EMPH = "#5a3d0e"  # 強調語の縁。地から切り離すため本文より濃く太く
TELOP_SHADOW = (4.5, -6.0, "#4a2a05", 0.60)   # 下に落ちる影。背景から浮かせる
                           # (3,-4,0.42 では実質1層に見えた → 強化。2026-08-29)
INK_DARK = "#2b2b28"
CARD = "#fffdf7"           # カード面の白。**白はこの1色に統一**(純白は文字専用)
DISCLAIM = "#4a4234"       # 免責行。#8a7f6c はコントラスト不足で読めなかった

TITLE = ""                 # 上部の帯に出す文字(use_fp_theme で設定)
BADGE = ""                 # 仮定の明示(戦略§6-2「利回りは仮定と明示」)
_POSE_CACHE: dict[str, Image.Image] = {}


def use_fp_theme(title: str, speaker: int = 108, badge: str = ""):
    """明るい背景・大きい字幕・上部のタイトル帯に切り替える。

    speaker=108 は**東北きりたん**(2026-08-24、ユーザーが10種を聴き比べて選定)。
    前は冥鳴ひまり(14)だったが「ボソボソ喋っていて、この女性に合ってない」
    との指摘で変更した。商用可・クレジット「VOICEVOX:東北きりたん」が必要
    (zunko.jp の音源利用規約。エンジンの speaker_info で確認・2026-08-24)。
    """
    global TITLE, BADGE
    TITLE = title
    BADGE = badge
    S.SURFACE = CREAM
    S.INK = INK_DARK
    S.DEFAULT_SPEAKER = speaker
    # 字幕: 3.8% → 5.7%(競合の実測)。2行を常用するので折り返しも広げる
    S.SUB_FS = 84
    S.SUB_WRAP = 11
    S.SUB_BLOCK_FIT = 0.86
    S.SUB_LINE_H = 0.052
    S.SUBTITLE_Y = 0.235
    S.STROKE_EDGE = TELOP_EDGE
    S.STROKE_SHADOW = TELOP_SHADOW
    S.new_canvas = _canvas
    S.draw_subtitle = _subtitle
    S.SUB_WORDPOP = WORD_POP    # 語ごとポップ(ユニット全体をfpsで割る)
    S.save_frame = _save_frame
    # **setup_fonts も差し替える。**(2026-08-29 批評ループで発覚)
    # render_video / preview_fp は途中で S.setup_fonts() を呼ぶ。テーマの後に
    # 呼ばれると rcParams が Noto に戻り、**RocknRoll One が一度も使われないまま**
    # 全フレームが焼かれていた。テーマ有効時は setup_fonts もテーマの書体を張る。
    S.setup_fonts = _setup_font
    _setup_font()


def _setup_font():
    """この動画のあいだだけ既定の書体にする。
    **shortlib.setup_fonts() は触らない**(既存30本の見た目を変えないため)。"""
    from matplotlib import font_manager
    files = sorted(FONT_DIR.glob(FONT_GLOB))
    if not files:
        raise SystemExit(f"書体が無い: {FONT_DIR}/{FONT_GLOB}")
    for f in files:
        font_manager.fontManager.addfont(str(f))
    fams = [FONT_FAMILY]
    fb = Path(FONT_FALLBACK)
    if fb.exists():
        font_manager.fontManager.addfont(str(fb))
        fams.append(FONT_FALLBACK_FAMILY)     # 足りない記号だけここへ落ちる
    # 第2書体(数字の極太)。Black の .ttc だけを登録するので、
    # この家族名+weight指定はかならず Black 面に解決される
    global NUM_FAMILY
    nf = Path(NUM_FONT_PATH)
    if nf.exists():
        try:
            font_manager.fontManager.addfont(str(nf))
            NUM_FAMILY = font_manager.FontProperties(fname=str(nf)).get_name()
        except Exception:
            NUM_FAMILY = FONT_FAMILY
    plt.rcParams["font.family"] = fams
    plt.rcParams["font.weight"] = FONT_WEIGHT


# ---------------------------------------------------------------- 表示用の整形
# **画面に出る数字は桁区切りを打つ**(2026-08-29 批評ループ)。
# 台本・verify.py・ナレーションは生の数字のまま(読み上げと検証を変えない)。
# 描画の直前でだけ「3162円 → 3,162円」に整形する。
_KETA_RE = re.compile(r"\d{4,}")
_ZEN = str.maketrans({"?": "?", "!": "!"})   # 和文の並びでは全角のほうが字間が締まる


def fmt_disp(s: str) -> str:
    """画面表示用の整形。4桁以上の数字に桁区切り、?!を全角へ。"""
    return _KETA_RE.sub(lambda m: f"{int(m.group()):,}", s).translate(_ZEN)


# ---------------------------------------------------------------- 縁取り(4層)
def fx(color: str, fs: float, emph: bool = False):
    """テロップ・数字の縁取り。影 → 白外縁 → 濃縁 → 同色 の4層で紙面から浮かせる。
    (旧: 影+縁の実質1層で、拡大すると平板だった。2026-08-29 批評ループ)"""
    o = fs * (0.14 if emph else 0.12)
    dx, dy, sc, sa = TELOP_SHADOW
    edge = TELOP_EDGE_EMPH if emph else TELOP_EDGE
    return [
        path_effects.Stroke(offset=(dx, dy), linewidth=o * 1.30, foreground=sc, alpha=sa),
        path_effects.Stroke(linewidth=o * 1.55, foreground="#fffaf0"),
        path_effects.Stroke(linewidth=o, foreground=edge),
        path_effects.Stroke(linewidth=2.0, foreground=color),
        path_effects.Normal(),
    ]


# ---------------------------------------------------------------- 実測幅(書体つき)
# shortlib._measure_widths は書体をキーに持たない。第2書体を混ぜると幅がずれるので、
# テーマ側は (文字列, サイズ, 書体, 太さ) で測る。
_MEASURE_CACHE: dict = {}


def measure_w(fig, renderer, s: str, fs: float, family, weight) -> float:
    key = (s, round(fs, 2), str(family), weight, S.W)
    w = _MEASURE_CACHE.get(key)
    if w is None:
        tmp = fig.text(0, -1, s, fontsize=fs, fontfamily=family, fontweight=weight)
        w = tmp.get_window_extent(renderer=renderer).width / S.W
        tmp.remove()
        _MEASURE_CACHE[key] = w
    return w


# ---------------------------------------------------------------- イージング
# 部品は min(1.0, t*1.6) の純線形を使っていた(等速で動いて等速で止まる=安物の動き)。
# 以後の部品はこの2つを経由すること。実体は shortlib のもの。
def ease_out(t: float) -> float:
    return S.ease_out(min(1.0, max(0.0, t)))


def ease_back(t: float) -> float:
    return S.ease_out_back(min(1.0, max(0.0, t)))


CHROME_GID = "fp_chrome"   # 帯・バッジ。ゲートの集計から外す印
BADGE_GID = "fp_chrome_badge"
DOT_GID = "fp_dot"         # 背景の水玉。カバーが dim_dots() で減光できるように
LAST_T = 0.0               # 直近フレームの動画内時刻。立ち絵のボブ等が読む


def _canvas(t_global: float = 0.0):
    global LAST_T
    LAST_T = t_global
    fig = plt.figure(figsize=S.FIGSIZE, dpi=S.DPI)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1], zorder=-10)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    # ドット(競合と同じ質感)。2026-08-29: 径70%・ピッチ80%に詰めて地紋に格下げ。
    # さらに低速の**対角**ドリフト(上0.020/秒+横0.012/秒)。どのユニットでも
    # 背景が微速で流れ、着地後の完全静止フレームを作らない
    # (批評5周目: 0.006/秒+旧DOT色は知覚閾値未満だった → 速度・コントラストを
    #  引き上げ。ドットには gid を付け、カバーだけ dim_dots() で減光できるようにする)
    step = 0.042
    r = 0.0068
    ystep = step * (S.W / S.H)
    xoff = (t_global * 0.012) % step
    j = 0
    y = -ystep + (t_global * 0.020) % ystep
    while y < 1.0 + ystep:
        x = (j % 2) * step / 2 - step + xoff
        while x < 1.0:
            # **円で描くと縦に伸びる**(軸は0〜1だが画面は1080×1920)。
            # 楕円で縦横比を打ち消して、競合と同じ真円にする
            e = Ellipse((x, y), 2 * r, 2 * r * S.W / S.H, color=DOT, zorder=-9)
            e.set_gid(DOT_GID)
            ax.add_patch(e)
            x += step
        y += ystep
        j += 1
    # 上部のタイトル帯。**単色の板ではなく縦のグラデーション**にする。
    # 帯とバッジは全フレーム共通の装飾なので gid で印を付けて、
    # 図のゲート(figure/align/overlap)の集計から外す。印が無いと
    # 「15字以上の文字列が2個」が全ユニットで鳴り、本当の指摘が埋もれる
    from matplotlib.colors import LinearSegmentedColormap
    # 帯は 0.098→0.075 に詰め、彩度も15%落とした(BAND/BAND_LO)。
    # 常設のチャンネル名がヒエラルキーの頂点になっていた(2026-08-29 批評5周目)
    h = 0.075
    bax = fig.add_axes([0, 1 - h, 1, h], zorder=3.0)
    bax.imshow(np.linspace(1, 0, 64).reshape(-1, 1), aspect="auto", extent=(0, 1, 0, 1),
               cmap=LinearSegmentedColormap.from_list("fpband", [BAND_LO, BAND]))
    bax.axis("off")
    bax.set_gid(CHROME_GID)
    if TITLE:
        # 白抜き + 濃い縁 + 影(競合と同じ)。濃い字を黄色に乗せるより遠くで読める
        S.text_fit(fig, 0.5, 1 - h / 2, fmt_disp(TITLE), ha="center", va="center",
                   color="#ffffff", fontsize=38, max_w=0.92, zorder=3.1,
                   path_effects=S.stroke_fx("#ffffff", outline=6.0)).set_gid(CHROME_GID)
    if BADGE:
        # 仮定の明示。**画面のどこかに常に出しておく**(戦略§6-2)。
        # max_w はカード幅(0.06〜0.94)に合わせる(2026-08-29 批評4周目:
        # 注記だけ左右マージン約0.03でカードより外に走り、揃え辺が1本ずれていた)
        S.text_fit(fig, 0.5, 1 - h - 0.026, BADGE, ha="center", va="center",
                   color=DISCLAIM, fontsize=26,
                   max_w=0.88, zorder=3.1).set_gid(BADGE_GID)
    return fig


def badge_head(fig):
    """免責行を先頭の一文だけにする(表示だけ。文言は BADGE の部分列)。

    2026-08-29 批評ループ: 「運用は年5%と仮定」を0秒目から出すと、後半で明かす
    ひねりを自分でネタバレする。運用の話が始まるユニットまでは料金の時点だけ出す。
    打消し表示の要件は保つ: 年5%の数字が画面に出る場面では必ず全文が出ている。"""
    for art in list(fig.texts):
        if art.get_gid() == BADGE_GID and "。" in art.get_text():
            art.set_text(art.get_text().split("。")[0] + "。")


def hide_chrome(fig):
    """帯・バッジを消す。カバーとサムネは全面を使うので、上から重ねない。
    帯は zorder 3.0 でカバーの黄色(1.5)より上にいるため、消さないと
    カバーの1行目に文字が重なる(check_overlap がループ72で検出)。"""
    for art in list(fig.artists) + list(fig.texts) + list(fig.axes):
        if str(art.get_gid() or "").startswith(CHROME_GID):
            art.remove()


def dim_dots(fig, factor: float = 0.5):
    """背景の水玉を減光する(カバー用。2026-08-29 批評5周目)。
    72px縮小のフィード寸ではドットがスペックルノイズになり、
    文字縁のギザつきと混ざって安っぽく見えていた。"""
    for ax in fig.axes:
        for p in ax.patches:
            if str(p.get_gid() or "") == DOT_GID:
                p.set_alpha((p.get_alpha() or 1.0) * factor)


# ---------------------------------------------------------------- 語ごとのポップ
# (2026-08-24。ユーザー指示「ポップさせてみて」)
#
# 競合のショートは、字幕が一度に全部出ない。**語がひとつずつ着地する。**
# 見る側は「次が出る」ので目を離しづらく、これが速度感の正体のひとつ。
#
# **既存32本には影響させない。**この関数は fp テーマのときだけ使われる。
# 描画は draw_rich_text を使わず自前でやる。理由は、語ごとに
# 透明度と拡大率を変える必要があり、既存の共通描画に手を入れると
# 32本すべての見た目が変わりうるため。

WORD_POP = True            # テーマの既定。False にすると従来どおり一度に出る
POP_PEAK = 1.34            # 着地の瞬間の拡大率
POP_SEC = 0.10             # 拡大が1.0に戻るまでの秒数
MAX_LINES = 2              # 字幕の最大行数(2026-08-29 批評5周目: 3行ブロックは
                           # 下端が Shorts 下部UI帯(y<0.10)に沈み、行数によって
                           # ブロックのアンカーが±100px級で漂っていた)
SUB_BOTTOM_MIN = 0.095     # 字幕ブロックの下端はここより下げない(機械ゲート)
SUB_FS_LOCK = None         # lock_sub_fs() が決める動画内共通の字幕級数

_TOKENIZER = None
# 数字のあとに来る「万・億・円・歳…」を前にくっつけるための判定
_NUM_TAIL = re.compile(r"[0-9０-９万億兆]$")
# 語が数字を含むか(2026-08-29 批評ループ2周目)。
# 強調(【】)の数字だけ極太にしていたが、テロップ内の裸の数字
# (「たった105円」の105円)が本文ウェイト400のままだった。
# **数字を含む語は強調でなくても第2書体の極太で打つ。**
_HAS_DIGIT = re.compile(r"\d")
# 単独で立たせない字(前の語にくっつける)
_PUNCT = "。、!?…・「」『』()()!?.,:;〜ー"


def _words(text: str) -> list[tuple[str, bool]]:
    """字幕を「語」に割る。返り値は(語, 強調か)の並び。

    【】で囲んだ語は**割らない**(「3万3000円」を分けたら意味が壊れる)。
    それ以外は janome で形態素に割り、助詞・助動詞・記号は前の語にくっつける
    (「貯金」「は、」ではなく「貯金は、」で1語にする)。
    """
    global _TOKENIZER
    out = []
    for seg, emph in S.parse_rich(text):
        if emph:
            out.append((seg, True, False))
            continue
        try:
            if _TOKENIZER is None:
                from janome.tokenizer import Tokenizer
                _TOKENIZER = Tokenizer()
            toks = list(_TOKENIZER.tokenize(seg))
        except Exception:
            out.append((seg, False, False))   # janome が無ければ割らない
            continue
        prev = ("", "", "")          # 直前の(品詞, 細分類, 表層)
        for tk in toks:
            pos = tk.part_of_speech.split(",")
            head, sub = pos[0], (pos[1] if len(pos) > 1 else "")
            prev_num = bool(out) and not out[-1][1] and _NUM_TAIL.search(out[-1][0])
            glue = (
                head in ("助詞", "助動詞")           # 「貯金」+「は」→「貯金は」
                or head == "記号"                     # 読点・句点は前にくっつける
                # **品詞ではなく文字で見る。**(2026-08-24)
                # janome は ASCII の「?」を 名詞,サ変接続 と判定するので、
                # 記号の規則をすり抜けて「開いてみませんか / ?」で行が折れていた
                or (tk.surface and not tk.surface.strip(_PUNCT))
                or sub in ("接尾", "非自立")          # 「3万」+「円」→「3万円」
                or (head == "名詞" and sub == "数" and prev_num)   # 「3」+「万」
                # --- ここから下は**実際に焼いて見つけた割れ方**(2026-08-24)
                # サ変動詞。janome は「仮定します」を
                #   仮定(名詞,サ変接続) + し(動詞) + ます(助動詞)
                # に割るので、動詞を繋げないと「仮定し / ます。」で行が折れる
                or (head == "動詞" and prev[:2] == ("名詞", "サ変接続"))
                # 「缶」+「コーヒー」のような接頭の一字。
                # 前が1字の名詞で、いまも名詞なら繋げる
                or (head == "名詞" and prev[0] == "名詞" and len(prev[2]) == 1
                    and sub != "数")
                # 数のあとの「年」「%」など(「年」+「5」+「%」→「年5%」)
                or (head == "名詞" and sub == "サ変接続" and prev[:2] == ("名詞", "数"))
                or (head == "名詞" and sub == "数" and prev[0] == "名詞"
                    and len(prev[2]) == 1)
            )
            if out and not out[-1][1] and glue:
                out[-1] = (out[-1][0] + tk.surface, False)
            else:
                # **くっつけたいのに、前が【】の強調でくっつけられなかった語**は
                # 別の語として置くが、「行頭に立たせない」印をつける(2026-08-24)。
                # 「263万円 / に / なります。」のように助詞が1字で行頭に立つのを防ぐ。
                # 実際に焼いて見つけた(強調の直後の助詞は色が変わるので繋げられない)
                out.append((tk.surface, False, glue))
            prev = (head, sub, tk.surface)
    # 2つ組で足した箇所を3つ組にそろえ、**1字の語は前後と離さない**
    fixed = []
    for w in out:
        s, e = w[0], w[1]
        nb = w[2] if len(w) > 2 else False
        if not s:
            continue
        if len(s) <= 1:
            nb = True                      # 1字の語を行頭に立たせない
        # 表示だけの整形(桁区切り・全角?!)。読み上げ・台本は変えない
        fixed.append([fmt_disp(s), e, nb])
    for i in range(len(fixed) - 1):
        # 1字の語の直後も切らない(「月 / 3162円」防止)。
        # ただし**ひらがな1字(=助詞)の直後は切ってよい**(2026-08-29 批評5周目:
        # 「【明細】を開いてみませんか?」で を→開いて… が全部連結され、
        # 1行が折れずに級数が半分まで縮んでいた。「…を / 開いて」は自然な改行)
        if len(fixed[i][0]) <= 1 and not re.match(r"[ぁ-ん]", fixed[i][0]):
            fixed[i + 1][2] = True
    return [tuple(x) for x in fixed]


def word_schedule(text: str, dur: float) -> list[float]:
    """各語が着地する時刻(ユニット頭からの秒)。字数で按分する。

    読み上げの実測に合わせるのが理想だが、VOICEVOX の音素長を語に対応づける
    のは別の作業になるので、まずは字数按分にする。**尺は必ず dur に収まる。**
    """
    ws = _words(text)
    n = sum(len(s) for s, *_ in ws) or 1
    # **全語をユニット前半で着地させる**(2026-08-29 批評ループ)。
    # dur-0.25 いっぱいに按分すると、行が左に垂れて中央揃えに見えない時間が
    # ユニットの大半を占めていた。前半55%で出し切り、残りは完成形を見せる
    span = max(0.0, min(dur - 0.25, dur * 0.55))
    out, acc = [], 0
    for s, *_ in ws:
        t0 = span * acc / n
        # 「。」「、」だけの語は前の語と**同時**に出す(1文字が単独で跳ねると変)
        if out and not s.strip("。、!?…・"):
            t0 = out[-1]
        out.append(t0)
        acc += len(s)
    # **答えの数字(強調語)は図の着地より先に出さない**(2026-08-29 批評2周目)。
    # 14_fueru で棒がまだカウント中なのに字幕に263万円が先に出て、
    # 「図→答え」の視線順が逆転していた。強調語は尺の38%以降に遅らせる
    # (図のアニメは anim(≈1〜1.2s)×0.55 で完了する。dur≈2s なので 0.38×dur が上回る)。
    hold = dur * 0.38
    for i, (s, emph, *_x) in enumerate(ws):
        if emph and out[i] < hold:
            out[i] = hold
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1])   # 出る順序は入れ替えない
    return out


def _fam_of(word, emph):
    # 強調語と**数字を含む語**は第2書体の極太で打つ(ウェイト差で階層を作る)。
    # 強調(【】)だけ太らせていた前版は、テロップのペイオフ数字
    # (「たった105円」)が本文400のままだった(2026-08-29 批評2周目)
    if emph or _HAS_DIGIT.search(word):
        return ([NUM_FAMILY], NUM_WEIGHT)
    return ([FONT_FAMILY, FONT_FALLBACK_FAMILY], FONT_WEIGHT)


def _fit_rows(fig, r, ws, fs0):
    """字幕の級数と行分割を決める(実測幅・行頭禁則つき)。

    _subtitle_wordpop と lock_sub_fs が**同じ計算**を使うためにここへ分離。
    返り値: (fs, rows)。rows は [[(語, 強調, 語番号), ...], ...]
    """
    def pack(size):
        rows, row, w = [], [], 0.0
        for i, (s, emph, nobreak) in enumerate(ws):
            ww = measure_w(fig, r, s, size, *_fam_of(s, emph))
            # nobreak の語は、はみ出しても前の語と同じ行に置く(行頭禁則)
            if row and w + ww > S.SUB_BLOCK_FIT and not nobreak:
                rows.append(row); row, w = [], 0.0
            row.append((s, emph, i)); w += ww
        if row:
            rows.append(row)
        return rows

    def widest(rows, size):
        return max((sum(measure_w(fig, r, s, size, *_fam_of(s, e))
                        for s, e, _ in row) for row in rows), default=0.0)

    def orphan(rows):
        # 最終行が2字以下の1語(「1つ」等)だと間延びして見える(2026-08-29)
        return (len(rows) > 1 and len(rows[-1]) == 1
                and len(rows[-1][0][0].strip(_PUNCT)) <= 2)

    fs = fs0
    rows = pack(fs)
    # 2行に収まるまで、**かつ どの行も画面幅に収まるまで**小さくする。
    for _ in range(12):
        if len(rows) <= MAX_LINES and widest(rows, fs) <= S.SUB_BLOCK_FIT:
            break
        fs *= 0.94
        rows = pack(fs)
    for _ in range(3):
        if not orphan(rows):
            break
        fs *= 0.94
        rows = pack(fs)
    return fs, rows


def lock_sub_fs(texts) -> float:
    """全ユニットの字幕を事前に採寸し、**最小の適合級数に動画内で固定**する。

    2026-08-29 批評5周目: 縮小がユニットごとに独立していたため、同じ役割の
    ナレーション字幕がカットまたぎで約4割サイズ揺れしていた(22 vs 23)。
    級数はユニット内でなく**動画内**で揃える。render.py が UNITS 定義の直後に
    1回呼ぶ(preview_fp も render.py を import するので同じ級数で下見できる)。
    """
    global SUB_FS_LOCK
    SUB_FS_LOCK = None
    fig = plt.figure(figsize=S.FIGSIZE, dpi=S.DPI)
    try:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        best = float(S.SUB_FS)
        for tx in texts:
            tx = re.sub(r"。\s*$", "", str(tx).rstrip())
            fs, _rows = _fit_rows(fig, r, _words(tx), float(S.SUB_FS))
            best = min(best, fs)
        SUB_FS_LOCK = best
    finally:
        plt.close(fig)
    return SUB_FS_LOCK


# 半角だけの語(Netflix 等)は1文字ずつに割ると字間が壊れるので語ごと出す
_ASCII_WORD = re.compile(r"[\x20-\x7e]+$")


def _subtitle_wordpop(fig, text: str, t_unit: float, dur: float, tag=None):
    """語がひとつずつ着地する字幕。**折り返しの位置は最初から固定**で、
    まだ出ていない語はその場所を空けたまま(レイアウトが跳ねない)。

    2026-08-29 批評5周目:
    - 級数は lock_sub_fs() の動画内共通値から始める(カット間のサイズ揺れ禁止)
    - **先頭行のyを固定し、下方向にのみ伸長**(行数でブロックが漂わない)。
      最大2行。下端が SUB_BOTTOM_MIN を割る組みは例外で落とす(機械ゲート)
    - 語の中は1〜2文字ずつのリビール(塊ポップの粗い粒度を細かくする。
      各文字 0.12秒の ease_out で 2px 浮き上がりながら着地する)
    """
    ws = _words(text)
    starts = word_schedule(text, dur)

    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    fs, rows = _fit_rows(fig, r, ws, float(SUB_FS_LOCK or S.SUB_FS))

    n = len(rows)
    step = S.SUB_LINE_H * (fs / 40)
    # **先頭行固定・下方向にのみ伸長**(2026-08-29 批評5周目)。
    # 中心固定だと行数が変わるたびに先頭行が±100px級で漂い、3行ブロックは
    # 下端が Shorts 下部UI帯まで沈んでいた
    y0 = S.SUBTITLE_Y
    if n > MAX_LINES or (y0 - (n - 1) * step) < SUB_BOTTOM_MIN:
        raise AssertionError(
            f"字幕が{n}行/下端{y0 - (n - 1) * step:.3f}。"
            f"2行以内・下端>={SUB_BOTTOM_MIN} に収まる文へ割り直すこと: {text!r}")
    for i, row in enumerate(rows):
        ws_row = [measure_w(fig, r, s, fs, *_fam_of(s, e)) for s, e, _ in row]
        x = 0.5 - sum(ws_row) / 2
        y = y0 - i * step
        for (s, emph, idx), w in zip(row, ws_row):
            st = starts[idx] if idx < len(starts) else 0.0
            if t_unit < st:
                x += w
                continue                    # まだ着地していない語は描かない
            color = TELOP_EMPH if emph else TELOP
            fam, wt = _fam_of(s, emph)
            if _ASCII_WORD.match(s):
                chars = [s]                 # 欧文はカーニングを守って語ごと
            else:
                chars = list(s)
            cw = ([w] if len(chars) == 1 else
                  [measure_w(fig, r, ch, fs, fam, wt) for ch in chars])
            cx = x
            for ci, (ch, cwi) in enumerate(zip(chars, cw)):
                cst = st + ci * 0.025       # 語内は1文字ずつ25msずらす
                age = t_unit - cst
                if age < 0:
                    cx += cwi
                    continue
                scale = 1.0 + (POP_PEAK - 1.0) * max(0.0, 1.0 - age / POP_SEC)
                rise = 0.0011 * (1.0 - ease_out(min(1.0, age / 0.12)))
                fig.text(cx + cwi / 2, y - rise, ch, ha="center", va="center",
                         color=color, fontsize=fs * scale, fontfamily=fam,
                         fontweight=wt,
                         path_effects=fx(color, fs * scale, emph=emph),
                         zorder=3.0)
                cx += cwi
            x += w


def _subtitle(fig, text: str, pop: float = 1.0, tag: str | None = None):
    """テーマの字幕。**WORD_POP なら語ごとに着地する描画へ回す。**(2026-08-24)

    ここで振り分けていなかったので、語ごとポップを実装したのに
    **動画には一度も入っていなかった**(下見でしか動いていなかった)。

    **行末の句点は落とす**(2026-08-29 批評2周目)。84pxの級数では「。」が
    1文字分の空白として目立つ。トップチャンネルのテロップの通例に合わせる。
    表示だけの整形で、ナレーション・台本・読点・文中の句点は変えない。
    """
    text = re.sub(r"。\s*$", "", text.rstrip())
    if WORD_POP and getattr(S, "SUB_TIME", None):
        t_unit, dur = S.SUB_TIME
        return _subtitle_wordpop(fig, text, t_unit, dur, tag)
    return _subtitle_plain(fig, text, pop, tag)


def _subtitle_plain(fig, text: str, pop: float = 1.0, tag: str | None = None):
    """大きい縁取りテロップ。**帯は敷かない**(競合は背景の上に直接置いている)。

    3行以上になったら**上に伸ばす**。下に伸ばすと Shorts のUI(下12〜15%)に入る。
    2行目・3行目の位置は2行のときと同じになるので、行数が変わってもブレない。
    (2026-08-23。ユーザー指示「文字制限かけて何言ってるかよくわからない文章に
     なるなら文字制限かけない方がいい」を受け、長い文も描けるようにした)
    """
    n = len(S.wrap_plain(text.replace("【", "").replace("】", ""), S.SUB_WRAP))
    step = S.SUB_LINE_H * (S.SUB_FS * pop / 40)
    y = S.SUBTITLE_Y + max(0, n - 2) * step
    S.draw_rich_text(fig, 0.5, y, text, S.SUB_FS * pop,
                     base_color=TELOP, emph_color=TELOP_EMPH,
                     wrap=S.SUB_WRAP, line_h=S.SUB_LINE_H, block_fit=S.SUB_BLOCK_FIT,
                     outline=13.0)


def _save_frame(fig, path: Path, facecolor: str = None):
    fig.savefig(path, dpi=S.DPI, facecolor=facecolor or CREAM)
    plt.close(fig)


# ---------------------------------------------------------------- キャラ

def pose(name: str, fade: bool = True, flip: bool = False) -> Image.Image:
    key = (name, fade, flip)
    if key not in _POSE_CACHE:
        p = POSE_DIR / f"{name}.png"
        if not p.exists():
            raise SystemExit(f"立ち絵がない: {p}")
        im = Image.open(p).convert("RGBA")
        if flip:
            # 左右反転(2026-08-29 批評5周目: カバーで指先・視線を
            # バッジへ向ける構図用)
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        # **透明の余白を切り落とす。** 切り抜きPNGは1024×1024の中に人物が
        # 浮いているので、そのまま置くと軸の枠だけが画面外にはみ出し、
        # check_overlap が「画面外」を毎シーン鳴らす(絵は見えていないのに)。
        box = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if box:
            im = im.crop(box)
        _POSE_CACHE[key] = _fade_bottom(im) if fade else im
    return _POSE_CACHE[key]


def _fade_bottom(im: Image.Image, frac: float = 0.07) -> Image.Image:
    """絵の下端を透明へ落とす。

    素材は腰のあたりで真横に切れているので、そのまま置くと
    ドットの背景の上に**硬い水平の切り口**が出る(2026-08-23の見比べ)。
    """
    a = np.asarray(im.getchannel("A"), dtype=np.float32)
    h = a.shape[0]
    n = max(1, int(h * frac))
    ramp = np.linspace(1.0, 0.0, n, dtype=np.float32)[:, None]
    a[h - n:] *= ramp
    out = im.copy()
    out.putalpha(Image.fromarray(a.astype("uint8"), mode="L"))
    return out


def draw_pose(fig, name: str, cx: float = 0.5, top: float = 0.78, height: float = 0.46,
              scale: float = 1.0, fade: bool = True, bob: bool = True,
              flip: bool = False):
    """キャラを図の上に置く。**画面中央に大きく**(競合の型)。

    top は絵の上端(figure座標)、height は絵の高さ(figure座標)。
    bob: 動画内時刻(LAST_T)でごく小さく上下にゆらす(2026-08-29 批評ループ。
    完全静止の立ち絵は画面の6割を「死んだ時間」にする)。振幅は0.004以下。
    flip: 左右反転(視線・指先の向きを構図に合わせる)。
    """
    im = pose(name, fade=fade, flip=flip)
    h = height * scale
    w = h * (im.width / im.height) * (S.H / S.W)
    dy = dx = 0.0
    if bob:
        dy = 0.0035 * math.sin(2 * math.pi * 1.2 * LAST_T)
        dx = 0.0015 * math.sin(2 * math.pi * 0.7 * LAST_T + 1.1)
    y0 = top - h + dy
    if y0 < 0:
        # 画面下端より下は**軸を伸ばさず絵を刈る**(2026-08-29 批評5周目)。
        # カバーの立ち絵は腰下が画面外で、軸の矩形が下へはみ出して
        # check_overlap の「画面外(上下)」に掛かっていた
        keep = max(0.05, (top + dy) / h)
        im = im.crop((0, 0, im.width, max(1, int(im.height * keep))))
        h = h * keep
        y0 = 0.0
    ax = fig.add_axes([cx - w / 2 + dx, y0, w, h], zorder=2.0)
    ax.imshow(np.asarray(im))
    ax.axis("off")
    return ax
