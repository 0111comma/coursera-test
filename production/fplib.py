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
import re
from pathlib import Path

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

# ---- 配色(競合の実測値に寄せた)
CREAM = "#f3e7d3"          # 背景。明るさ 0.75 前後
DOT = "#faf1e2"            # 背景のドット
BAND = "#f9cb45"           # 上部のタイトル帯(下側)
BAND_LO = "#eda520"        # 帯の上側。**縦のグラデーション**にする
BAND_INK = "#3b2c10"       # 帯の文字
TELOP = "#ffffff"          # テロップの本文
TELOP_EMPH = "#ffd93d"     # テロップの強調(数字)
TELOP_EDGE = "#7b2d00"     # テロップの縁。**stroke_fx が黒を焼いていて、この色は
                           # 使われていなかった**(2026-08-23に接続)
TELOP_SHADOW = (3.0, -4.0, "#4a2a05", 0.42)   # 下に落ちる影。背景から浮かせる
INK_DARK = "#2b2b28"

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
    plt.rcParams["font.family"] = fams
    plt.rcParams["font.weight"] = FONT_WEIGHT


CHROME_GID = "fp_chrome"   # 帯・バッジ。ゲートの集計から外す印


def _canvas(t_global: float = 0.0):
    fig = plt.figure(figsize=S.FIGSIZE, dpi=S.DPI)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1], zorder=-10)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    # ドット(競合と同じ質感)
    # **大きく・まばらに**(競合の実測: 間隔が幅の約5.3%、半径が約1.0%)。
    # 0.024/0.0065 は目が細かすぎて、網目の生地のように見えていた
    step = 0.053
    r = 0.0100
    j = 0
    y = 0.0
    while y < 1.0:
        x = (j % 2) * step / 2
        while x < 1.0:
            # **円で描くと縦に伸びる**(軸は0〜1だが画面は1080×1920)。
            # 楕円で縦横比を打ち消して、競合と同じ真円にする
            ax.add_patch(Ellipse((x, y), 2 * r, 2 * r * S.W / S.H,
                                 color=DOT, zorder=-9))
            x += step
        y += step * (S.W / S.H)
        j += 1
    # 上部のタイトル帯。**単色の板ではなく縦のグラデーション**にする。
    # 帯とバッジは全フレーム共通の装飾なので gid で印を付けて、
    # 図のゲート(figure/align/overlap)の集計から外す。印が無いと
    # 「15字以上の文字列が2個」が全ユニットで鳴り、本当の指摘が埋もれる
    from matplotlib.colors import LinearSegmentedColormap
    h = 0.098
    bax = fig.add_axes([0, 1 - h, 1, h], zorder=3.0)
    bax.imshow(np.linspace(1, 0, 64).reshape(-1, 1), aspect="auto", extent=(0, 1, 0, 1),
               cmap=LinearSegmentedColormap.from_list("fpband", [BAND_LO, BAND]))
    bax.axis("off")
    bax.set_gid(CHROME_GID)
    if TITLE:
        # 白抜き + 濃い縁 + 影(競合と同じ)。濃い字を黄色に乗せるより遠くで読める
        S.text_fit(fig, 0.5, 1 - h / 2, TITLE, ha="center", va="center",
                   color="#ffffff", fontsize=44, max_w=0.92, zorder=3.1,
                   path_effects=S.stroke_fx("#ffffff", outline=7.0)).set_gid(CHROME_GID)
    if BADGE:
        # 仮定の明示。**画面のどこかに常に出しておく**(戦略§6-2)
        S.text_fit(fig, 0.5, 1 - h - 0.026, BADGE, ha="center", va="center",
                   color="#8a7f6c", fontsize=26,
                   max_w=0.92, zorder=3.1).set_gid(CHROME_GID)
    return fig


def hide_chrome(fig):
    """帯・バッジを消す。カバーとサムネは全面を使うので、上から重ねない。
    帯は zorder 3.0 でカバーの黄色(1.5)より上にいるため、消さないと
    カバーの1行目に文字が重なる(check_overlap がループ72で検出)。"""
    for art in list(fig.artists) + list(fig.texts) + list(fig.axes):
        if art.get_gid() == CHROME_GID:
            art.remove()


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
MAX_LINES = 3              # 字幕の最大行数。4行だと立ち絵に重なる(実測)

_TOKENIZER = None
# 数字のあとに来る「万・億・円・歳…」を前にくっつけるための判定
_NUM_TAIL = re.compile(r"[0-9０-９万億兆]$")
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
        fixed.append([s, e, nb])
    for i in range(len(fixed) - 1):
        if len(fixed[i][0]) <= 1:
            fixed[i + 1][2] = True         # 1字の語の直後も切らない(「月 / 3162円」防止)
    return [tuple(x) for x in fixed]


def word_schedule(text: str, dur: float) -> list[float]:
    """各語が着地する時刻(ユニット頭からの秒)。字数で按分する。

    読み上げの実測に合わせるのが理想だが、VOICEVOX の音素長を語に対応づける
    のは別の作業になるので、まずは字数按分にする。**尺は必ず dur に収まる。**
    """
    ws = _words(text)
    n = sum(len(s) for s, *_ in ws) or 1
    # 最後の語が出てから 0.25 秒は全部見えている時間を残す
    span = max(0.0, dur - 0.25)
    out, acc = [], 0
    for s, *_ in ws:
        t0 = span * acc / n
        # 「。」「、」だけの語は前の語と**同時**に出す(1文字が単独で跳ねると変)
        if out and not s.strip("。、!?…・"):
            t0 = out[-1]
        out.append(t0)
        acc += len(s)
    return out


def _subtitle_wordpop(fig, text: str, t_unit: float, dur: float, tag=None):
    """語がひとつずつ着地する字幕。**折り返しの位置は最初から固定**で、
    まだ出ていない語はその場所を空けたまま(レイアウトが跳ねない)。"""
    ws = _words(text)
    starts = word_schedule(text, dur)

    fig.canvas.draw()
    r = fig.canvas.get_renderer()

    def widths(row, size):
        return [S._measure_widths(fig, r, [(s, e)], size, FONT_WEIGHT)[0]
                for s, e, _ in row]

    # **語の途中では折らない。**(2026-08-24)
    # S.wrap_plain は句読点でしか折らないので、行に入らないと語の真ん中で切れて
    # 「つみたて / ると、」のようになっていた。
    # そのうえで**文字数ではなく実測の幅**で詰める。字数だと書体を変えるたびに
    # 折り返しが合わなくなるし、字幅の広い書体(Dela Gothic など)で画面から出る。
    def pack(size):
        rows, row, w = [], [], 0.0
        for i, (s, emph, nobreak) in enumerate(ws):
            ww = S._measure_widths(fig, r, [(s, emph)], size, FONT_WEIGHT)[0]
            # nobreak の語は、はみ出しても前の語と同じ行に置く(行頭禁則)
            if row and w + ww > S.SUB_BLOCK_FIT and not nobreak:
                rows.append(row); row, w = [], 0.0
            row.append((s, emph, i)); w += ww
        if row:
            rows.append(row)
        return rows

    def widest(rows, size):
        return max((sum(widths(row, size)) for row in rows), default=0.0)

    fs = S.SUB_FS
    rows = pack(fs)
    # 3行に収まるまで、**かつ どの行も画面幅に収まるまで**小さくする。
    # 行頭禁則(nobreak)で1行に押し込むと、折り返せないぶん行が長くなる。
    # 幅を見ずに行数だけ見ていたので、1行のまま画面から溢れていた(2026-08-24)。
    for _ in range(12):
        if len(rows) <= MAX_LINES and widest(rows, fs) <= S.SUB_BLOCK_FIT:
            break
        fs *= 0.94
        rows = pack(fs)

    n = len(rows)
    step = S.SUB_LINE_H * (fs / 40)
    y0 = S.SUBTITLE_Y + max(0, n - 2) * step
    for i, row in enumerate(rows):
        ws_row = widths(row, fs)
        x = 0.5 - sum(ws_row) / 2
        y = y0 - i * step
        for (s, emph, idx), w in zip(row, ws_row):
            st = starts[idx] if idx < len(starts) else 0.0
            if t_unit < st:
                x += w
                continue                    # まだ着地していない語は描かない
            age = t_unit - st
            scale = 1.0 + (POP_PEAK - 1.0) * max(0.0, 1.0 - age / POP_SEC)
            color = TELOP_EMPH if emph else TELOP
            fig.text(x + w / 2, y, s, ha="center", va="center", color=color,
                     fontsize=fs * scale, fontweight=FONT_WEIGHT,
                     path_effects=S.stroke_fx(color, outline=S.outline_for(fs * scale)),
                     zorder=3.0)
            x += w


def _subtitle(fig, text: str, pop: float = 1.0, tag: str | None = None):
    """テーマの字幕。**WORD_POP なら語ごとに着地する描画へ回す。**(2026-08-24)

    ここで振り分けていなかったので、語ごとポップを実装したのに
    **動画には一度も入っていなかった**(下見でしか動いていなかった)。
    """
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

def pose(name: str) -> Image.Image:
    if name not in _POSE_CACHE:
        p = POSE_DIR / f"{name}.png"
        if not p.exists():
            raise SystemExit(f"立ち絵がない: {p}")
        im = Image.open(p).convert("RGBA")
        # **透明の余白を切り落とす。** 切り抜きPNGは1024×1024の中に人物が
        # 浮いているので、そのまま置くと軸の枠だけが画面外にはみ出し、
        # check_overlap が「画面外」を毎シーン鳴らす(絵は見えていないのに)。
        box = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if box:
            im = im.crop(box)
        _POSE_CACHE[name] = _fade_bottom(im)
    return _POSE_CACHE[name]


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
              scale: float = 1.0):
    """キャラを図の上に置く。**画面中央に大きく**(競合の型)。

    top は絵の上端(figure座標)、height は絵の高さ(figure座標)。
    """
    im = pose(name)
    h = height * scale
    w = h * (im.width / im.height) * (S.H / S.W)
    ax = fig.add_axes([cx - w / 2, top - h, w, h], zorder=2.0)
    ax.imshow(np.asarray(im))
    ax.axis("off")
    return ax
