"""ずんだもん立ち絵エンジン(VOICEVOX公式立ち絵+口パクパッチ合成)。

立ち絵はVOICEVOX公式リソース(github.com/VOICEVOX/voicevox_resource)の公式イラスト
(坂本アヒル様)。assets/zunda/README.md参照。

権利: 東北ずん子・ずんだもんプロジェクトの二次創作ガイドライン準拠
(個人チャンネルの広告収益は非商用の例外として許容。zunko.jp/guideline.html)。
概要欄に「VOICEVOX:ずんだもん」(音声・必須)+キャラクターガイドライン準拠の一文を記載する。
禁止: 政治・宗教への関与、特定個人・団体の非難、キャラのイメージ毀損(ずん虐)。

演出の根拠(deep-loops ㉙): 口パク=音声RMS連動で口3枚(YMM4/PSDToolKit方式)、
切替は最大10Hz相当。目パチ=平均3.5秒±1.5秒・閉じ1フレーム。表情は1本で2〜4種。
呼吸=高さ1%弱のsin揺れ。Z順は グラフ → 立ち絵 → 字幕(テロップ最前面)。
"""
import struct
import wave
from pathlib import Path

import numpy as np
import matplotlib.transforms as mtrans
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Arc

# ずんだもんの配色(公式イメージに寄せた二次創作)
SKIN = "#ffe9d6"
SKIN_EDGE = "#d9a583"
HAIR = "#cdeaa5"
HAIR_SHADE = "#a8d375"
EDAMAME = "#6fae4b"
EDAMAME_DARK = "#4f8a33"
EYE = "#3f9b3f"
OUTFIT = "#e8f4dc"
LINE = "#4a3b30"

EXPRESSIONS = ("normal", "surprised", "troubled", "happy", "smug")
CHARA_FPS = 8  # 口パクの実効切替 ≤8Hz(アニメ3コマ@24fps相場と同等)


# 公式立ち絵(VOICEVOX公式=坂本アヒル様。assets/zunda/README.md参照)
ASSET_DIR = Path(__file__).resolve().parent / "assets" / "zunda"
EXPR_FILES = {
    "normal": "1.png",      # ノーマル
    "surprised": "1.png",   # 驚きは通常顔+開口+驚き線+ジャンプで表現
    "troubled": "76.png",   # ヘロヘロ(困り顔)
    "happy": "22.png",      # セクシー(微笑)
    "smug": "7.png",        # ツンツン(ジト目=ドヤ)
}
# 顔パーツのアンカー(portrait 255x500のピクセル座標。グリッド計測 2026-08-13)
MOUTH = (118.5, 138.0)
EYES = ((102.0, 127.5), (136.0, 126.5))
SKIN = "#fdf4f0"
MOUTH_DARK = "#8c3b30"
MOUTH_TONGUE = "#e06a5a"
LINE = "#7a4a42"
# バストアップの表示範囲(portrait座標)
VIEW = (40, 215, 55, 280)  # x0, x1, y0, y1

_IMG_CACHE: dict[str, "np.ndarray"] = {}


_SKIN_CACHE: dict[str, str] = {}


def _img(expr: str):
    fn = EXPR_FILES.get(expr, "1.png")
    if fn not in _IMG_CACHE:
        from PIL import Image
        im = Image.open(ASSET_DIR / fn).convert("RGBA")
        im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)  # 表示スケール向けに先行拡大
        arr = np.asarray(im)
        _IMG_CACHE[fn] = arr
        # 口の直上(あご上部)の肌色をサンプリング → パッチが陰影に馴染む
        mx, my = MOUTH
        region = arr[int((my - 7) * 3):int((my - 4) * 3), int((mx - 5) * 3):int((mx + 5) * 3), :3]
        med = np.median(region.reshape(-1, 3), axis=0).astype(int)
        _SKIN_CACHE[fn] = "#{:02x}{:02x}{:02x}".format(*med)
    return _IMG_CACHE[fn]


def _skin(expr: str) -> str:
    fn = EXPR_FILES.get(expr, "1.png")
    _img(expr)
    return _SKIN_CACHE[fn]


def draw_zunda(ax, mouth=0, eyes="open", expr="normal", dy_px: float = 0.0):
    """公式立ち絵のバストアップ+口パッチ合成。ax=専用オーバーレイaxes。
    mouth: 0閉/1半/2開(口元のみ描き替え) / eyes: open/closed(まぶたパッチ)
    dy_px: 呼吸・ジャンプの上下(portrait px)
    """
    arr = _img(expr)
    x0, x1, y0, y1 = VIEW
    ax.imshow(arr, extent=[0, arr.shape[1] / 3, arr.shape[0] / 3, 0],
              interpolation="bilinear", aspect="auto")
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1 - dy_px, y0 - dy_px)  # yは下向き(origin upper相当)
    ax.autoscale(False)
    mx, my = MOUTH
    # surprisedは常時開口を最低ラインに(驚き顔の代替)
    if expr == "surprised" and mouth < 1:
        mouth = 1
    # 口パッチ: 元の口を肌色で覆ってから状態別の口を描く
    ax.add_patch(Ellipse((mx, my - 0.5), 15, 11, facecolor=_skin(expr), edgecolor="none"))
    if mouth == 0:
        # y軸反転座標系: theta25〜155が「にっこり(∪)」、200〜340が「への字」
        if expr == "troubled":
            ax.add_patch(Arc((mx, my), 7.5, 4.5, theta1=200, theta2=340, color=LINE, linewidth=1.6))
        else:
            ax.add_patch(Arc((mx, my - 1.0), 7.5, 4.5, theta1=25, theta2=155, color=LINE, linewidth=1.6))
    elif mouth == 1:
        ax.add_patch(Ellipse((mx, my), 5.5, 4.0, facecolor=MOUTH_DARK, edgecolor=LINE, linewidth=0.7))
    else:
        ax.add_patch(Ellipse((mx, my), 8.0, 7.5, facecolor=MOUTH_DARK, edgecolor=LINE, linewidth=0.8))
        ax.add_patch(Ellipse((mx, my + 1.8), 4.6, 2.6, facecolor=MOUTH_TONGUE, edgecolor="none"))
    # まばたきは公式立ち絵モードでは行わない(まぶたパッチは絵の完全性を損なうため。㉙改)
    # 驚き線
    if expr == "surprised":
        for ddx, ddy in ((-30, -26), (-34, -18), (-26, -21)):
            ax.plot([mx + ddx, mx + ddx - 5], [my + ddy, my + ddy - 6], color="#4a3b30", linewidth=1.6)


def mouth_track(wav_path: Path, fps: int = CHARA_FPS) -> list[int]:
    """音声RMS連動の口パク列(PSDToolKit方式)。フレームごとに 0閉/1半/2開。"""
    with wave.open(str(wav_path), "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
        ch = w.getnchannels()
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    data /= 32768.0
    dur = len(data) / sr
    frames = max(1, int(np.ceil(dur * fps)))
    rms = np.zeros(frames)
    for k in range(frames):
        s = int(k / fps * sr)
        e = min(len(data), int((k + 1) / fps * sr))
        if e > s:
            rms[k] = float(np.sqrt(np.mean(data[s:e] ** 2)))
    peak = rms.max() or 1.0
    track = []
    for v in rms:
        r = v / peak
        track.append(2 if r > 0.42 else (1 if r > 0.10 else 0))
    # 終了マージン: 発話の切れ目を1フレーム延ばして口パクを滑らかに
    for k in range(len(track) - 1, 0, -1):
        if track[k] == 0 and track[k - 1] > 0:
            track[k] = 1 if track[k - 1] == 2 else 0
    return track


class BlinkSchedule:
    """平均3.5秒±1.5秒間隔・閉じ約0.13秒の目パチ(YMM4相場)。"""

    def __init__(self, seed: int):
        rng = np.random.default_rng(seed)
        self.times = []
        t = float(rng.uniform(0.5, 2.5))
        while t < 120:
            self.times.append(t)
            t += float(rng.uniform(2.0, 5.0))

    def eyes(self, t: float) -> str:
        for bt in self.times:
            if bt <= t < bt + 0.13:
                return "closed"
            if bt > t:
                break
        return "open"


def breath_offset(t: float, h: float, phase: float = 0.0) -> float:
    """呼吸の上下(高さ0.8%・周期4.6秒)。"""
    return 0.008 * h * float(np.sin(2 * np.pi * (t / 4.6) + phase))
