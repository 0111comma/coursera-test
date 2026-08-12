"""ショート動画(1080x1920)制作の共通ライブラリ。

制作ルールの根拠は docs/research/short-video-format.md(R1〜R14)。
このライブラリが実装しているルール:
  R2/R4: ユニット冒頭のアニメーション(painter(fig, t) の t で状態を描き分ける)
  R5:    1ユニット=1文。話速は既定1.2
  R6:    字幕=ナレーション文そのもの(【】強調マーカーだけ読み上げから除去)
  R7/R8: 太字風テロップ(黒縁取り+同色ストローク)、【】で囲んだ語だけ黄色
  R9:    セーフエリア定数
  R13:   既定話者ずんだもん(VOICEVOX speaker=3)
  R14:   小音量BGMの合成とミックス

使い方は videos/S001-*/render.py を参照。
"""

import json
import math
import re
import struct
import subprocess
import urllib.parse
import urllib.request
import wave
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- キャンバス(1080x1920) ----
W, H = 1080, 1920
DPI = 100
FIGSIZE = (W / DPI, H / DPI)

# ---- デザイントークン ----
# チャート配色は dataviz スキルの参照パレット(ダークモード、検証済み)
SURFACE = "#1a1a19"      # 背景
INK = "#ffffff"          # 主テキスト
INK_2 = "#c3c2b7"        # 副テキスト
MUTED = "#898781"        # 軸ラベル等
GRID = "#2c2c2a"         # グリッド線
BASELINE = "#383835"     # 軸線
SERIES_1 = "#3987e5"     # 青(スロット1)
SERIES_2 = "#d95926"     # 橙(スロット2)
# テロップ強調色(R8: 黄色+黒縁の定番)。チャートの系列色としては使わない
EMPH = "#fab219"

# Shortsのセーフエリア(R9: 右端のボタン列・下部のUIを避ける)
SAFE_L, SAFE_R = 0.08, 0.92
SUBTITLE_Y = 0.24        # 字幕ブロックの上端(下から)
SUB_FS = 40              # 字幕フォントサイズ
SUB_WRAP = 14            # 字幕の折り返し文字数

_JP_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
]


def setup_fonts():
    for p in _JP_FONT_CANDIDATES:
        if Path(p).exists():
            font_manager.fontManager.addfont(p)
            name = font_manager.FontProperties(fname=p).get_name()
            plt.rcParams["font.family"] = name
            return name
    raise RuntimeError("日本語フォントが見つからない")


def ease_out(t: float) -> float:
    """カウントアップ・バー成長用のイージング。"""
    return 1 - (1 - t) ** 3


@dataclass
class Unit:
    """1ユニット = 1文(R5)。scene名で背景を選び、animで冒頭に動きを入れる(R2/R4)。"""
    scene: str
    subtitle: str            # 字幕=読み上げ文(R6)。【】で囲んだ語は黄色強調(R8)
    narration: str = ""      # 読み上げ用の上書き(省略時はsubtitleから【】を除いた文)
    pad: float = 0.2         # ナレーション後の間(秒)
    anim: float = 0.0        # ユニット冒頭のアニメーション秒数(0=静止)
    fps: int = 20            # アニメーション部分のfps

    def tts_text(self) -> str:
        t = self.narration or self.subtitle
        return t.replace("【", "").replace("】", "")


# ---- TTS ----

VOICEVOX_URL = "http://127.0.0.1:50021"
DEFAULT_SPEAKER = 3      # ずんだもん(ノーマル)。概要欄に「VOICEVOX:ずんだもん」必須(R13)
DEFAULT_SPEED = 1.2      # R5: 速めのテンポ


def _http(url: str, data: bytes | None = None, headers: dict | None = None, timeout=120) -> bytes:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def voicevox_alive() -> bool:
    try:
        _http(f"{VOICEVOX_URL}/version", timeout=5)
        return True
    except Exception:
        return False


def tts_voicevox(text: str, out_wav: Path, speaker: int = DEFAULT_SPEAKER, speed: float = DEFAULT_SPEED):
    q = urllib.parse.quote(text)
    query = _http(f"{VOICEVOX_URL}/audio_query?text={q}&speaker={speaker}", data=b"")
    qj = json.loads(query)
    qj["speedScale"] = speed
    qj["prePhonemeLength"] = 0.05
    qj["postPhonemeLength"] = 0.08
    wav = _http(
        f"{VOICEVOX_URL}/synthesis?speaker={speaker}",
        data=json.dumps(qj).encode(),
        headers={"Content-Type": "application/json"},
    )
    out_wav.write_bytes(wav)


def tts_openjtalk(text: str, out_wav: Path):
    """フォールバック(音質は落ちる)。"""
    subprocess.run(
        [
            "open_jtalk",
            "-x", "/var/lib/mecab/dic/open-jtalk/naist-jdic",
            "-m", "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice",
            "-r", "1.15",
            "-ow", str(out_wav),
        ],
        input=text.encode(),
        check=True,
    )


def synthesize(units: list[Unit], workdir: Path, speaker: int = DEFAULT_SPEAKER) -> tuple[list[Path], str]:
    workdir.mkdir(parents=True, exist_ok=True)
    use_vv = voicevox_alive()
    engine = "voicevox" if use_vv else "open_jtalk"
    wavs = []
    for i, u in enumerate(units):
        w = workdir / f"seg_{i:02d}.wav"
        if use_vv:
            tts_voicevox(u.tts_text(), w, speaker=speaker)
        else:
            tts_openjtalk(u.tts_text(), w)
        wavs.append(w)
    return wavs, engine


# ---- BGM(R14: 小さく敷くだけの合成ループ。著作権フリー=自前生成) ----

def synth_bgm(duration: float, out_wav: Path, bpm: int = 86):
    """lo-fi風の控えめな4コードループ(Am7→Fmaj7→Cadd9→G)+キック/ハット。"""
    import numpy as np
    sr = 44100
    n = int(sr * duration)
    t = np.arange(n) / sr
    beat = 60.0 / bpm
    bar = beat * 4

    chords = [
        [110.00, 164.81, 196.00, 261.63],   # Am7
        [87.31, 130.81, 174.61, 220.00],    # Fmaj7
        [130.81, 196.00, 293.66, 329.63],   # Cadd9
        [98.00, 146.83, 196.00, 246.94],    # G
    ]
    audio = np.zeros(n)
    # パッド: 小節ごとにコードを切り替え、ゆっくり立ち上がる正弦波の重ね
    for bi in range(int(duration / bar) + 1):
        start = bi * bar
        seg = (t >= start) & (t < start + bar)
        if not seg.any():
            continue
        ts = t[seg] - start
        env = np.minimum(ts / 0.6, 1.0) * np.exp(-ts / (bar * 1.4))
        for f in chords[bi % 4]:
            audio[seg] += 0.05 * env * np.sin(2 * np.pi * f * ts)
            audio[seg] += 0.015 * env * np.sin(2 * np.pi * f * 2 * ts)
    # キック(各拍)とハット(8分)
    for k in range(int(duration / beat) + 1):
        start = k * beat
        seg = (t >= start) & (t < start + 0.12)
        ts = t[seg] - start
        audio[seg] += 0.16 * np.exp(-ts * 40) * np.sin(2 * np.pi * 52 * ts)
        for off in (0.0, beat / 2):
            s2 = (t >= start + off) & (t < start + off + 0.03)
            m = int(s2.sum())
            if m:
                noise = np.random.default_rng(k * 7 + int(off * 1000)).standard_normal(m)
                audio[s2] += 0.015 * np.diff(np.concatenate([[0], noise])) * np.exp(-np.arange(m) / (0.008 * sr))
    peak = np.abs(audio).max() or 1.0
    audio = audio / peak * 0.30  # 十分小さく
    pcm = (audio * 32767).astype("<i2")
    with wave.open(str(out_wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(pcm.tobytes())


# ---- 計測・結合(ffmpeg) ----

def duration_of(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def pad_wav(src: Path, dst: Path, pad_sec: float):
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", f"apad=pad_dur={pad_sec}", str(dst)],
        check=True,
    )


def assemble(frames: list[Path], durations: list[float], padded_wavs: list[Path],
             out_mp4: Path, workdir: Path, bgm: bool = True):
    """フレーム列+ナレーション(+BGM)をmp4(1080x1920, 30fps)に結合する。"""
    alist = workdir / "audio.txt"
    alist.write_text("".join(f"file '{w.resolve()}'\n" for w in padded_wavs))
    narration = workdir / "narration.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(alist),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", str(narration)],
        check=True,
    )
    total = sum(durations)
    audio_in = narration
    if bgm:
        bgm_wav = workdir / "bgm.wav"
        synth_bgm(total + 0.5, bgm_wav)
        mixed = workdir / "mixed.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(narration), "-i", str(bgm_wav),
             "-filter_complex", "[1:a]volume=0.5[bg];[0:a][bg]amix=inputs=2:duration=first:normalize=0",
             str(mixed)],
            check=True,
        )
        audio_in = mixed

    vlist = workdir / "frames.txt"
    lines = []
    for f, d in zip(frames, durations):
        lines.append(f"file '{f.resolve()}'\nduration {d:.4f}\n")
    lines.append(f"file '{frames[-1].resolve()}'\n")
    vlist.write_text("".join(lines))
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error",
         "-f", "concat", "-safe", "0", "-i", str(vlist),
         "-i", str(audio_in),
         "-vf", f"fps=30,scale={W}:{H}:flags=lanczos,format=yuv420p",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest",
         str(out_mp4)],
        check=True,
    )


# ---- 描画ヘルパ ----

def new_canvas():
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor(SURFACE)
    return fig


def stroke_fx(text_color: str, outline: float = 7.0, fatten: float = 2.0):
    """R7: 黒縁取り+同色ストロークで太字化(IPAゴシックにボールドがないため)。"""
    return [
        path_effects.Stroke(linewidth=outline, foreground="#000000"),
        path_effects.Stroke(linewidth=fatten, foreground=text_color),
        path_effects.Normal(),
    ]


_EMPH_RE = re.compile(r"【(.+?)】")


def parse_rich(text: str) -> list[tuple[str, bool]]:
    """【】マーカーを(文字列, 強調フラグ)のセグメント列に分解。"""
    segs, pos = [], 0
    for m in _EMPH_RE.finditer(text):
        if m.start() > pos:
            segs.append((text[pos:m.start()], False))
        segs.append((m.group(1), True))
        pos = m.end()
    if pos < len(text):
        segs.append((text[pos:], False))
    return [(s, e) for s, e in segs if s]


def wrap_plain(text: str, width: int) -> list[str]:
    """句読点で句に分けて行に詰める(句読点の行頭孤立や数字+助数詞の分断を避ける)。"""
    phrases, cur = [], ""
    for ch in text:
        cur += ch
        if ch in "、。!?":
            phrases.append(cur)
            cur = ""
    if cur:
        phrases.append(cur)

    def hard_split(p: str) -> list[str]:
        out, buf = [], ""
        for ch in p:
            buf += ch
            if len(buf) >= width + 2 and ch not in "0123456789万円%年.,":
                out.append(buf)
                buf = ""
        if buf:
            out.append(buf)
        return out

    lines, line = [], ""
    for p in phrases:
        parts = [p] if len(p) <= width + 4 else hard_split(p)
        for part in parts:
            if line and len(line) + len(part) > width:
                lines.append(line)
                line = part
            else:
                line += part
    if line:
        lines.append(line)
    return lines


def wrap_rich(text: str, width: int) -> list[list[tuple[str, bool]]]:
    """richテキストを折り返し、行ごとのセグメント列にする。"""
    chars = []
    for seg, emph in parse_rich(text):
        chars.extend((ch, emph) for ch in seg)
    plain = "".join(ch for ch, _ in chars)
    lines_plain = wrap_plain(plain, width)
    lines, idx = [], 0
    for lp in lines_plain:
        line_chars = chars[idx: idx + len(lp)]
        idx += len(lp)
        segs, buf, cur = [], "", None
        for ch, e in line_chars:
            if cur is None or e == cur:
                buf += ch
                cur = e
            else:
                segs.append((buf, cur))
                buf, cur = ch, e
        if buf:
            segs.append((buf, cur))
        lines.append(segs)
    return lines


def draw_rich_line(fig, y: float, segs: list[tuple[str, bool]], fontsize: float,
                   base_color: str = INK, emph_color: str = EMPH,
                   outline: float = 7.0, ha_center_x: float = 0.5):
    """強調色の混在する1行を中央揃えで描く(実測幅で並べる)。"""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    widths = []
    for s, _ in segs:
        tmp = fig.text(0, -1, s, fontsize=fontsize)
        ext = tmp.get_window_extent(renderer=renderer)
        widths.append(ext.width / W)
        tmp.remove()
    total = sum(widths)
    x = ha_center_x - total / 2
    for (s, emph), w in zip(segs, widths):
        color = emph_color if emph else base_color
        fig.text(x, y, s, ha="left", va="center", color=color, fontsize=fontsize,
                 path_effects=stroke_fx(color, outline=outline))
        x += w


def draw_rich_text(fig, x: float, y: float, text: str, fontsize: float,
                   base_color: str = INK, emph_color: str = EMPH,
                   outline: float = 7.0, wrap: int = 0, line_h: float = 0.034):
    """【】強調に対応したテキスト描画(中央揃え)。wrap>0で折り返し。"""
    lines = wrap_rich(text, wrap) if wrap else [parse_rich(text)]
    for i, segs in enumerate(lines):
        draw_rich_line(fig, y - i * line_h * (fontsize / 40), segs, fontsize,
                       base_color=base_color, emph_color=emph_color,
                       outline=outline, ha_center_x=x)


def draw_subtitle(fig, text: str):
    """R6/R7/R8: ナレーション文そのものを縁取りテロップで。【】は黄色。"""
    draw_rich_text(fig, 0.5, SUBTITLE_Y, text, SUB_FS, wrap=SUB_WRAP, line_h=0.036)


def draw_badge(fig, text: str):
    """右上の注記バッジ(例:「年利5%と仮定」)。コンプライアンス表示(戦略§6)。"""
    fig.text(
        0.90, 0.935, text, ha="right", va="center", color=INK_2, fontsize=22,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=SURFACE, edgecolor=BASELINE, linewidth=1.5),
    )


def draw_footer_brand(fig, text: str):
    fig.text(0.5, 0.045, text, ha="center", va="center", color=MUTED, fontsize=20)


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(BASELINE)
        ax.spines[s].set_linewidth(1.5)
    ax.tick_params(colors=MUTED, labelsize=20, length=0)
    ax.grid(axis="y", color=GRID, linewidth=1.2)
    ax.set_axisbelow(True)


def save_frame(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, facecolor=SURFACE)
    plt.close(fig)


def render_video(units: list[Unit], scene_painters: dict, outdir: Path, out_name: str,
                 speaker: int = DEFAULT_SPEAKER, bgm: bool = True) -> dict:
    """ユニット列とシーン描画関数からmp4を作る。

    scene_painters: {scene名: painter(fig, t)}。tはユニット内アニメーションの進行度
    (0→1、静止ユニットでは常に1.0)。
    """
    setup_fonts()
    workdir = outdir / "work"
    workdir.mkdir(parents=True, exist_ok=True)
    for old in workdir.glob("frame_*.png"):
        old.unlink()

    wavs, engine = synthesize(units, workdir, speaker=speaker)

    frames, durations, padded = [], [], []
    for i, (u, w) in enumerate(zip(units, wavs)):
        pw = workdir / f"seg_{i:02d}_pad.wav"
        pad_wav(w, pw, u.pad)
        d_total = duration_of(pw)
        padded.append(pw)

        def emit(t: float, sub_idx: int, dur: float):
            fig = new_canvas()
            scene_painters[u.scene](fig, t)
            draw_subtitle(fig, u.subtitle)
            f = workdir / f"frame_{i:02d}_{sub_idx:03d}.png"
            save_frame(fig, f)
            frames.append(f)
            durations.append(dur)

        anim = min(u.anim, d_total)
        if anim > 0:
            n = max(2, int(anim * u.fps))
            for k in range(n):
                t = (k + 1) / n
                emit(t, k, anim / n)
            hold = d_total - anim
            if hold > 0.01:
                emit(1.0, n, hold)
        else:
            emit(1.0, 0, d_total)

    out_mp4 = outdir / out_name
    assemble(frames, durations, padded, out_mp4, workdir, bgm=bgm)
    return {"mp4": out_mp4, "engine": engine, "total_sec": sum(durations)}
