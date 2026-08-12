"""ショート動画(1080x1920)制作の共通ライブラリ。

使い方は videos/S001-*/render.py を参照。流れ:
  1. 各ユニット(字幕+ナレーションの1チャンク)をTTSで音声化して長さを測る
  2. ユニットごとに1枚のフレームPNG(シーン背景+字幕)を描く
  3. ffmpegで 静止画列+ナレーション → mp4 に結合する

TTSはローカルのVOICEVOXエンジン(http://127.0.0.1:50021)を使い、
起動していなければOpen JTalkにフォールバックする。
"""

import json
import subprocess
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- キャンバス(1080x1920) ----
W, H = 1080, 1920
DPI = 100
FIGSIZE = (W / DPI, H / DPI)

# ---- デザイントークン(datavizスキルの参照パレット・ダークモード。検証済み) ----
SURFACE = "#1a1a19"      # 背景
INK = "#ffffff"          # 主テキスト
INK_2 = "#c3c2b7"        # 副テキスト
MUTED = "#898781"        # 軸ラベル等
GRID = "#2c2c2a"         # グリッド線
BASELINE = "#383835"     # 軸線
SERIES_1 = "#3987e5"     # 青(スロット1)
SERIES_2 = "#d95926"     # 橙(スロット2)

# Shortsのセーフエリア(右端のボタン列・下部のUIを避ける)
SAFE_L, SAFE_R = 0.08, 0.92
SUBTITLE_Y = 0.24        # 字幕の中心(下から)

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


@dataclass
class Unit:
    """字幕1枚+ナレーション1チャンク。scene名で背景を選ぶ。"""
    scene: str
    subtitle: str            # 画面に出す字幕(記号OK)
    narration: str = ""      # 読み上げテキスト(読み間違い防止の表記。空なら subtitle を読む)
    pad: float = 0.35        # ナレーション後の間(秒)

    def tts_text(self) -> str:
        return self.narration or self.subtitle


# ---- TTS ----

VOICEVOX_URL = "http://127.0.0.1:50021"


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


def tts_voicevox(text: str, out_wav: Path, speaker: int = 2, speed: float = 1.1):
    """VOICEVOXで合成。speaker=2は四国めたん(ノーマル)。動画の概要欄にクレジット必須。"""
    q = urllib.parse.quote(text)
    query = _http(f"{VOICEVOX_URL}/audio_query?text={q}&speaker={speaker}", data=b"")
    qj = json.loads(query)
    qj["speedScale"] = speed
    qj["postPhonemeLength"] = 0.15
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
            "-r", "1.05",
            "-ow", str(out_wav),
        ],
        input=text.encode(),
        check=True,
    )


def synthesize(units: list[Unit], workdir: Path, speaker: int = 2) -> tuple[list[Path], str]:
    """全ユニットを音声化。(wavパスのリスト, 使用エンジン名) を返す。"""
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


def assemble(frames: list[Path], durations: list[float], padded_wavs: list[Path], out_mp4: Path, workdir: Path):
    """静止画列+ナレーション音声をmp4(1080x1920, 30fps)に結合する。"""
    # 音声の連結
    alist = workdir / "audio.txt"
    alist.write_text("".join(f"file '{w.resolve()}'\n" for w in padded_wavs))
    narration = workdir / "narration.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(alist),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", str(narration)],
        check=True,
    )
    # 映像の連結(concatデマルチプレクサ。最後のフレームは繰り返しが必要)
    vlist = workdir / "frames.txt"
    lines = []
    for f, d in zip(frames, durations):
        lines.append(f"file '{f.resolve()}'\nduration {d:.3f}\n")
    lines.append(f"file '{frames[-1].resolve()}'\n")
    vlist.write_text("".join(lines))
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error",
         "-f", "concat", "-safe", "0", "-i", str(vlist),
         "-i", str(narration),
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


def wrap_jp(text: str, width: int) -> list[str]:
    """日本語向け折り返し。句読点で句に分けて行に詰める(句読点の行頭孤立や
    数字+助数詞の分断を避ける)。長すぎる句だけ文字数で強制分割する。"""
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
            # 数字・助数詞の途中では切らない
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


def draw_subtitle(fig, text: str):
    lines = wrap_jp(text, 15)
    fig.text(
        0.5, SUBTITLE_Y, "\n".join(lines),
        ha="center", va="center", color=INK, fontsize=34, linespacing=1.5,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#000000", alpha=0.35, edgecolor="none"),
    )


def draw_badge(fig, text: str):
    """右上の注記バッジ(例:「年利5%と仮定」)。"""
    fig.text(
        0.90, 0.935, text, ha="right", va="center", color=INK_2, fontsize=22,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=SURFACE, edgecolor=BASELINE, linewidth=1.5),
    )


def draw_footer_brand(fig, text: str):
    fig.text(0.5, 0.045, text, ha="center", va="center", color=MUTED, fontsize=20)


def style_axes(ax):
    """チャート用の recessive な軸スタイル。"""
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


def render_video(units: list[Unit], scene_painters: dict, outdir: Path, out_name: str, speaker: int = 2) -> dict:
    """ユニット列とシーン描画関数からmp4を作る。

    scene_painters: {scene名: fig を受け取り背景を描く関数}
    戻り値: {"mp4": Path, "engine": str, "total_sec": float}
    """
    setup_fonts()
    workdir = outdir / "work"
    workdir.mkdir(parents=True, exist_ok=True)

    wavs, engine = synthesize(units, workdir, speaker=speaker)

    frames, durations, padded = [], [], []
    for i, (u, w) in enumerate(zip(units, wavs)):
        pw = workdir / f"seg_{i:02d}_pad.wav"
        pad_wav(w, pw, u.pad)
        d = duration_of(pw)
        padded.append(pw)
        durations.append(d)

        fig = new_canvas()
        scene_painters[u.scene](fig)
        draw_subtitle(fig, u.subtitle)
        f = workdir / f"frame_{i:02d}.png"
        save_frame(fig, f)
        frames.append(f)

    out_mp4 = outdir / out_name
    assemble(frames, durations, padded, out_mp4, workdir)
    return {"mp4": out_mp4, "engine": engine, "total_sec": sum(durations)}
