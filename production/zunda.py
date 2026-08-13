"""ずんだもん立ち絵エンジン(坂本アヒル様「ずんだもん立ち絵素材2.3」+音声連動合成)。

素材: 坂本アヒル様のPSD立ち絵素材(assets/zunda/。readme=自由利用・公式規約準拠で商用可・改変可)。
gen_zunda_parts.py が表情×口×目の状態別PNG(assets/zunda/parts/)を事前合成し、
本モジュールが口パク(音声RMS連動)・目パチ・呼吸・強調ジャンプを付けて描画する。
概要欄クレジット: 「VOICEVOX:ずんだもん」(必須)+「立ち絵: 坂本アヒル 様」(慣行)。
禁止: 政治・宗教への関与、特定個人・団体の非難、キャラのイメージ毀損(ずん虐)。

演出の根拠(deep-loops ㉙): 口パク=RMS2閾値で口3枚(YMM4/PSDToolKit方式)・切替8Hz。
目パチ=平均3.5秒±1.5秒・閉じ0.13秒(normalのみ。専用目の表情は常時)。
表情は1本で2〜4種。呼吸=高さ1%弱のsin揺れ。Z順=グラフ→立ち絵→字幕(最前面)。
"""
from pathlib import Path

import numpy as np

EXPRESSIONS = ("normal", "surprised", "troubled", "happy", "smug")
CHARA_FPS = 8  # 口パクの実効切替 ≤8Hz(アニメ3コマ@24fps相場と同等)

PARTS_DIR = Path(__file__).resolve().parent / "assets" / "zunda" / "parts"
_IMG_CACHE: dict[str, "np.ndarray"] = {}


def _img(expr: str, mouth: int, eyes: str):
    """状態別PNG(uniform crop 800x915)。まばたき差分がない表情はopenにフォールバック。"""
    name = f"{expr}_{mouth}_{eyes}.png"
    if not (PARTS_DIR / name).exists():
        name = f"{expr}_{mouth}_open.png"
    if name not in _IMG_CACHE:
        from PIL import Image
        _IMG_CACHE[name] = np.asarray(Image.open(PARTS_DIR / name).convert("RGBA"))
    return _IMG_CACHE[name]


def draw_zunda(ax, mouth=0, eyes="open", expr="normal", dy_px: float = 0.0):
    """立ち絵を描く。ax=専用オーバーレイaxes(縦横比は呼び出し側のrectで合わせる)。
    mouth: 0閉/1半/2開 / eyes: open/closed(まばたき) / dy_px: 呼吸・ジャンプの上下(素材px)
    """
    arr = _img(expr, mouth, eyes)
    h, w = arr.shape[:2]
    ax.imshow(arr, extent=[0, w, h, 0], interpolation="bilinear", aspect="auto")
    ax.set_xlim(0, w)
    ax.set_ylim(h - dy_px, -dy_px)
    ax.autoscale(False)


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
