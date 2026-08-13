"""ずんだもん立ち絵エンジン(二次創作・ベクター描画)。

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


def draw_zunda(ax, cx, cy, h, mouth=0, eyes="open", expr="normal"):
    """立ち絵を描く。ax=専用オーバーレイaxes(aspect equal)。
    cx,cy=頭の中心 / h=キャラ全体の高さ / mouth: 0閉・1半・2開 / eyes: open/closed
    expr: normal/surprised/troubled/happy/smug
    """
    u = h / 10.0
    head_r = 2.6 * u
    # 体(チビキャラのバストアップ)
    body_w, body_h = 3.4 * u, 3.0 * u
    ax.add_patch(FancyBboxPatch((cx - body_w / 2, cy - head_r - body_h * 0.92), body_w, body_h,
                                boxstyle="round,pad=0.02",
                                facecolor=OUTFIT, edgecolor=EDAMAME, linewidth=2))
    ax.add_patch(Polygon([(cx - 0.9 * u, cy - head_r - 0.1 * u), (cx + 0.9 * u, cy - head_r - 0.1 * u),
                          (cx, cy - head_r - 1.1 * u)], closed=True,
                         facecolor=EDAMAME, edgecolor=EDAMAME_DARK, linewidth=1.5))
    # 髪(後ろ)→顔→前髪
    ax.add_patch(Circle((cx, cy + 0.15 * u), head_r * 1.12, facecolor=HAIR_SHADE, edgecolor="none"))
    ax.add_patch(Circle((cx, cy), head_r, facecolor=SKIN, edgecolor=SKIN_EDGE, linewidth=1.5))
    n_bang = 7
    bang_pts = [(cx - head_r * 1.05, cy + 0.3 * u)]
    for i in range(n_bang + 1):
        x = cx - head_r * 1.05 + (2 * head_r * 1.05) * i / n_bang
        bang_pts.append((x, cy + (0.30 if i % 2 == 0 else 0.62) * head_r))
    bang_pts.append((cx + head_r * 1.05, cy + 0.3 * u))
    top = [(cx + head_r * 1.05, cy + 0.3 * u), (cx + head_r * 0.9, cy + head_r * 0.95),
           (cx, cy + head_r * 1.18), (cx - head_r * 0.9, cy + head_r * 0.95),
           (cx - head_r * 1.05, cy + 0.3 * u)]
    ax.add_patch(Polygon(bang_pts + top[::-1], closed=True, facecolor=HAIR,
                         edgecolor=HAIR_SHADE, linewidth=1.5))
    # 枝豆ヘッドピース(傾けた莢+豆3粒)
    pod_cx, pod_cy = cx + 0.3 * u, cy + head_r * 1.30
    tr = mtrans.Affine2D().rotate_deg_around(pod_cx, pod_cy, -14) + ax.transData
    ax.add_patch(Ellipse((pod_cx, pod_cy), 2.4 * u, 1.0 * u, facecolor=EDAMAME,
                         edgecolor=EDAMAME_DARK, linewidth=2, transform=tr))
    for dx in (-0.65, 0, 0.65):
        ax.add_patch(Circle((pod_cx + dx * u, pod_cy + (0.16 if dx == 0 else 0.06) * u), 0.34 * u,
                            facecolor="#8cc763", edgecolor=EDAMAME_DARK, linewidth=1.2, transform=tr))
    # もみあげ
    for sx in (-1, 1):
        ax.add_patch(Polygon([(cx + sx * head_r * 0.98, cy + 0.2 * u), (cx + sx * head_r * 1.25, cy - 1.4 * u),
                              (cx + sx * head_r * 0.72, cy - 0.4 * u)], closed=True,
                             facecolor=HAIR, edgecolor=HAIR_SHADE, linewidth=1.2))
    # 目
    ey = cy + 0.1 * u
    ex = head_r * 0.45
    if eyes == "open":
        we, he_ = 0.62 * u, (1.3 if expr == "surprised" else 1.05) * u
        for sx in (-1, 1):
            ax.add_patch(Ellipse((cx + sx * ex, ey), we, he_, facecolor=EYE, edgecolor=LINE, linewidth=1.2))
            ax.add_patch(Ellipse((cx + sx * ex - 0.1 * u, ey + he_ * 0.22), we * 0.32, he_ * 0.3,
                                 facecolor="#ffffff", edgecolor="none"))
    else:
        for sx in (-1, 1):
            ax.add_patch(Arc((cx + sx * ex, ey), 0.7 * u, 0.5 * u, theta1=200, theta2=340,
                             color=LINE, linewidth=2.2))
    # 眉
    for sx in (-1, 1):
        if expr == "troubled":
            ang = -18 * sx
        elif expr == "surprised":
            ang = 0
        elif expr == "smug":
            ang = 14 * sx
        else:
            ang = 6 * sx
        bx = cx + sx * ex
        dx = 0.3 * u * np.cos(np.radians(ang))
        dy = 0.3 * u * np.sin(np.radians(ang))
        yy = ey + 0.85 * u + (0.25 * u if expr == "surprised" else 0)
        ax.plot([bx - dx, bx + dx], [yy - dy * sx, yy + dy * sx],
                color=LINE, linewidth=2.2, solid_capstyle="round")
    # ほっぺ
    cheek_a = 0.85 if expr in ("happy", "smug") else 0.45
    for sx in (-1, 1):
        ax.add_patch(Ellipse((cx + sx * head_r * 0.62, cy - 0.5 * u), 0.7 * u, 0.42 * u,
                             facecolor="#ffb0a0", edgecolor="none", alpha=cheek_a))
    # 口(3枚: 閉/半/開)
    my = cy - 0.85 * u
    if mouth == 0:
        if expr == "troubled":
            ax.add_patch(Arc((cx, my - 0.1 * u), 0.8 * u, 0.5 * u, theta1=20, theta2=160,
                             color=LINE, linewidth=2.2))
        else:
            ax.add_patch(Arc((cx, my + 0.1 * u), 0.8 * u, 0.5 * u, theta1=200, theta2=340,
                             color=LINE, linewidth=2.2))
    elif mouth == 1:
        ax.add_patch(Ellipse((cx, my), 0.5 * u, 0.35 * u, facecolor="#8c3b30", edgecolor=LINE, linewidth=1.5))
    else:
        ax.add_patch(Ellipse((cx, my), 0.75 * u, 0.75 * u, facecolor="#8c3b30", edgecolor=LINE, linewidth=1.5))
        ax.add_patch(Ellipse((cx, my - 0.18 * u), 0.45 * u, 0.25 * u, facecolor="#e06a5a", edgecolor="none"))
    # 驚き線
    if expr == "surprised":
        for dx, dy in [(-1.4, 1.5), (-1.7, 0.9), (-1.15, 1.05)]:
            ax.plot([cx + dx * head_r * 0.8, cx + dx * head_r * 0.95],
                    [cy + dy * u * 1.9, cy + dy * u * 2.25], color=LINE, linewidth=2)


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
