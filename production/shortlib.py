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

import hashlib
import json
import os
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
INK = "#f2f1e9"          # 主テキスト(オフホワイト。Material Designダークテーマの高強調=白87%に準拠。
                         # 「乱視ハレーション説」は裏取りの結果、査読なしの通説だった。字幕の放送標準は
                         # 純白だが、コントラスト17:1でAAA維持のため本件はどちらでも可 → Material寄せ。ループ㉟)
INK_2 = "#c3c2b7"        # 副テキスト
MUTED = "#898781"        # 軸ラベル等(テキスト用。背景と4:1を確保するため暗くしない)
MUTED_BAR = "#67655f"    # グレーアウトした文脈バー用(ループ⑮: 金とのΔE 通常21/P型17を確保)
GRID = "#2c2c2a"         # グリッド線
BASELINE = "#383835"     # 軸線
SERIES_1 = "#3987e5"     # 青(スロット1)
SERIES_2 = "#d95926"     # 橙(スロット2)
# テロップ強調色(R8: 黄色+黒縁の定番)。チャートの系列色としては使わない
EMPH = "#fab219"

# カテゴリ別のアクセント色(ループ71。ユーザー「画面構成飽きてきた」への対策1)。
# 全動画が同じ黄色だったので、テーマ系統で色を変える。
#   invest=NISA・投資(緑) / tax=税・取られる系(珊瑚) / save=貯金・預金(青) /
#   pension=年金・老後(紫) / default=時事・その他(従来の黄)
ACCENTS = {
    "invest":  ("#3ecf8e", "#1f9c63"),
    "tax":     ("#ff7a6b", "#d14b3c"),
    "save":    ("#5aa9ff", "#2f6fc0"),
    "pension": ("#c39bff", "#8f63e0"),
    "default": ("#fab219", "#c98500"),
}


def set_accent(name: str):
    """アクセント色をカテゴリで切り替える。render_video より前に呼ぶ。

    scenes_common / scenes_long は import 時に EMPH/GOLD を写し取るので、
    読み込み済みならそちらの束縛も貼り替える。
    """
    global EMPH, GOLD, SERIES_1
    EMPH, GOLD = ACCENTS[name]
    SERIES_1 = EMPH                    # 主役の棒もテーマ色に合わせる
    import sys as _sys
    for mod in ("scenes_common", "scenes_long"):
        m = _sys.modules.get(mod)
        if m is not None:
            m.EMPH, m.GOLD, m.SERIES_1 = EMPH, GOLD, SERIES_1
# お金・成功の系列色(ループ2: 金融は金がアクセント。青とのCVD/コントラスト検証済み)
GOLD = "#c98500"

# Shortsのセーフエリア(R9: 右端のボタン列・下部のUIを避ける)
SAFE_L, SAFE_R = 0.08, 0.92
SUBTITLE_Y = 0.24        # 字幕ブロックの上端(下から)
SUB_FS = 52              # 字幕フォントサイズ(ループ20: 画面高の約4%。スマホ最優先)
SUB_WRAP = 12            # 字幕の折り返し文字数
SUB_BLOCK_FIT = 0.70     # 字幕ブロックの最大幅(Shorts右ボタン列 x>0.85 を避ける)
SUB_LINE_H = 0.036       # 字幕の行間(図の高さに対する割合)
BADGE_XY = (0.90, 0.83)  # 注記バッジの位置
BADGE_FS = 28
BRAND_XY = (0.5, 0.045)  # フッターのチャンネル名
BRAND_FS = 20


def use_landscape():
    """出力を横型 1920×1080 に切り替える(長尺用。docs/research/longform-design.md)。

    ショートと長尺で違うのは**画面比とレイアウト定数だけ**で、
    TTS・BGM・SE・立ち絵・結合はまったく同じ処理でよい。
    だから 868行を複製せず、この関数でモジュール定数を差し替える。
    長尺の render.py は先頭で 1回だけ呼ぶこと(new_canvas より前)。

    値の決め方(縦型からの換算):
    - 字幕は「画面高の何%か」で決まる。縦型52ptは1920pxの3.8%。
      横型1080pxで同じ割合にすると29ptだが、長尺はテレビ・PCでも見られるので
      少し大きめの40pt(4.9%)を採る
    - 折り返しは横幅が1.78倍になるので12字→26字
    - バッジとフッターは Shorts のUIを避ける必要がないので、四隅に寄せる

    話速も下げる(ループ71 フェーズ5)。ショートの 1.3 のままだと
    L001 は **398字/分** で、押し付けられる側の速さを8分続けることになる。
    日本語の目安は 標準300〜350字/分・速め400字/分〜 なので、
    長尺は **標準の上限(約340字/分)** に置く。実測の対応は 05-tempo.md。
    """
    global W, H, FIGSIZE, SUBTITLE_Y, SUB_FS, SUB_WRAP, SUB_BLOCK_FIT, SUB_LINE_H
    global BADGE_XY, BADGE_FS, BRAND_XY, BRAND_FS, SAFE_L, SAFE_R, SPEED_SCALE
    W, H = 1920, 1080
    FIGSIZE = (W / DPI, H / DPI)
    SAFE_L, SAFE_R = 0.05, 0.95
    SUBTITLE_Y = 0.150
    SUB_FS = 40
    SUB_WRAP = 26
    SUB_BLOCK_FIT = 0.86
    SUB_LINE_H = 0.069       # 縦型と同じ行間(px)を、1080px基準の割合に直したもの
    BADGE_XY, BADGE_FS = (0.972, 0.940), 22
    BRAND_XY, BRAND_FS = (0.5, 0.036), 16
    # 立ち絵: 縦型と同じピクセル寸法(約369×422px)を右下に置き、字幕の上に載せる
    CHARA_RECTS["bl"] = [0.010, 0.200, 0.192, 0.391]
    CHARA_RECTS["br"] = [0.798, 0.200, 0.192, 0.391]
    # 環境変数で明示指定されているときは、それを尊重して上書きしない
    if "SHORTLIB_SPEED_SCALE" not in os.environ:
        SPEED_SCALE = LONG_SPEED_SCALE
    # 長尺はリッチ背景(背景+テロップ帯+素材枠+章チップ)を標準にする
    # (video-elements-2026-08.md。ショートは実測検証済みの現行ルックを維持)
    use_rich_bg()

# ループ3: テロップの定番は源ノ角ゴシック(=Noto Sans CJK JP)。太ウェイトを実際に使う
_JP_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
]


def setup_fonts():
    name = None
    for p in _JP_FONT_CANDIDATES:
        if Path(p).exists():
            try:
                font_manager.fontManager.addfont(p)
                if name is None:
                    name = font_manager.FontProperties(fname=p).get_name()
            except Exception:
                continue
    if name is None:
        raise RuntimeError("日本語フォントが見つからない")
    plt.rcParams["font.family"] = name
    plt.rcParams["font.weight"] = "bold"
    return name


def ease_out(t: float) -> float:
    """反応系(カウントアップの着地・ポップ)のイージング。"""
    return 1 - (1 - t) ** 3


def ease_in_out(t: float) -> float:
    """自動アニメーション(バー成長・線の描画)のイージング(ループ9)。"""
    return 3 * t * t - 2 * t * t * t


def ease_out_back(t: float) -> float:
    """オーバーシュート付き(深掘り④: 突発的な出現=abrupt onsetが注意を捕捉する)。"""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


@dataclass
class Unit:
    """1ユニット = 1文(R5)。scene名で背景を選び、animで冒頭に動きを入れる(R2/R4)。"""
    scene: str
    subtitle: str            # 字幕=読み上げ文(R6)。【】で囲んだ語は黄色強調(R8)
    narration: str = ""      # 読み上げ用の上書き(省略時はsubtitleから【】を除いた文)
    pad: float = 0.15        # ナレーション後の間(秒。深掘り⑦: 詰め気味が定石)
    anim: float = 0.0        # ユニット冒頭のアニメーション秒数(0=静止)
    fps: int = 20            # アニメーション部分のfps
    intonation: float = 1.1  # 抑揚(深掘り②: 一律1.0は単調。文脈で1.05〜1.3)
    speed: float = 0.0       # 話速の上書き(0=既定。深掘り②: 重要文は遅く・つなぎは速く)
    pitch: float = -0.03     # ピッチ(深掘り②: ナレーション基調は少し低め。ピークで持ち上げ)
    pause_scale: float = 1.1 # 句読点の間(深掘り②: AIの早口感を消す。タメは1.5〜1.7)
    se: str | None = None    # 効果音 "pop"/"don"/"puchun"(強調箇所のみ。ループ6)
    se_at: float = 0.0       # ユニット頭からのSEオフセット秒(深掘り④: 着地に同期させる用)
    cover: bool = False      # 冒頭0.07秒に完成形フレームを挟む(フィードの静止表示対策。ループ7)
    puchun: bool = False     # ユニット頭に「プチュン」を鳴らす(音だけのフリーズ演出。映像の暗転はしない)
    face: str = "normal"     # 立ち絵の表情 normal/surprised/troubled/happy/smug(deep-loops ㉙: 1本で2〜4種)
    chara: str = "bl"        # 立ち絵の位置 "bl"(左下)/"br"(右下)/"none"(そのユニットで非表示)
    speaker: int = 0         # 話者の上書き(0=render_videoの既定)。二人会話は 3=ずんだもん/2=めたん

    def tts_text(self) -> str:
        t = self.narration or self.subtitle
        for a, b in READING.items():
            t = t.replace(a, b)
        return t.replace("【", "").replace("】", "")


# 画面に出す綴りと、読ませたい音がちがう語(ループ66)。
#
# 「NISA を エヌアイエスエー と読んでいる」はループ⑳(S002)とループ64(S017)で
# **2回**指摘されている。1回目の対策は render.py に narration= を1つ書くことで、
# それは**その1本しか直らない対策**だった。2回目の対策として check_yomi.py を
# 作ったが、それは**書き忘れを見つける**だけで、書き忘れ自体は起こり続ける。
#
# ここで表にしておけば、字幕に NISA と書くだけで読みは常に「ニーサ」になる。
# つまり**書き忘れようがない**。check_yomi.py は最後の網として残す。
READING = {
    "NISA": "ニーサ",
    "iDeCo": "イデコ",
    "ATM": "エーティーエム",
    "GDP": "ジーディーピー",
    "ETF": "イーティーエフ",
}


# ---- TTS ----

VOICEVOX_URL = "http://127.0.0.1:50021"
DEFAULT_SPEAKER = 3      # ずんだもん(ノーマル)。概要欄に「VOICEVOX:ずんだもん」必須(R13)
METAN_SPEAKER = 2        # 四国めたん(ノーマル)。概要欄に「VOICEVOX:四国めたん」必須

# 二人会話(寸劇)モード。duo-skit-2026-08.md の調査に基づく:
#   ずんだもん=聞き手(左・反転して内側向き) / 四国めたん=解説役(右・公式ポートレート)。
#   話者は Unit.speaker で切り替え、字幕に名札(緑/ピンク)、非話者は減光。
DUO = False
ZUNDA_TAG_COLOR = "#3ecf8e"   # ずんだもんの名札(緑)
METAN_TAG_COLOR = "#f28bb4"   # めたんの名札(ピンク。髪色由来の慣行)


def use_duo():
    """二人会話(ずんだもん×四国めたん)に切り替える。render.py の先頭で
    use_landscape() と同じく new_canvas() より前に1回だけ呼ぶ。"""
    global DUO
    DUO = True
DEFAULT_SPEED = 1.2      # R5: 速めのテンポ
# 全体の話速の倍率(ループ58)。ユーザー指摘:
#   「もうちょっと早くできる? 周りのショート動画の速度感についていけてない」
# 各Unitの speed に、さらにこの倍率を掛ける。1本ずつ直さなくても全体を調整できる
SPEED_SCALE = float(os.environ.get("SHORTLIB_SPEED_SCALE", "1.3"))
# これ以上の pad は「止め」とみなし、その区間はBGMも切る(05/08-tempo/audio)
LONG_STOP_PAD = 0.5


def render_signature(units, scene_painters, speaker=None, bgm=True, chara=True,
                     out_name="", bands=None) -> str:
    """レンダリング結果を一意に決める署名。

    `render_video` の再開判定に使うほか、**`check_long.py` が
    `output/work/` の音声を信じてよいかの判断にも使う。**
    署名が合わないのに秒を読むと、台本を作り直したあとに
    **古い音声から計算した秒で判定してしまう**(フェーズ12で実際に踏んだ)。

    SPEED_SCALE と画面比も入れる(フェーズ5)。u.speed だけ見ていると、
    全体の話速だけ変えたときに古い音声を使い回してしまう。
    """
    return hashlib.sha256(repr([
        (u.scene, u.subtitle, u.narration, u.pad, u.anim, u.fps, u.intonation, u.speed,
         u.pitch, u.pause_scale, u.se, u.se_at, u.cover, u.puchun, u.face, u.chara,
         u.speaker)
        for u in units
    ] + [sorted(scene_painters), speaker if speaker is not None else DEFAULT_SPEAKER,
         bgm, chara, out_name, SPEED_SCALE, W, H, EMPH, DUO, RICH_BG,
         bands]).encode()).hexdigest()
# 長尺(横型)の倍率。use_landscape() が環境変数の指定が無いときに差し替える。
# 実測(05-tempo.md): 実効speed 1.25 = 約340字/分 = 日本語の「標準」の上限。
# ショートの 1.3 は L001 で 398字/分 = 「速め」になり、8分続けると疲れる。
LONG_SPEED_SCALE = 1.15


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


def tts_voicevox(text: str, out_wav: Path, speaker: int = DEFAULT_SPEAKER, speed: float = DEFAULT_SPEED,
                 intonation: float = 1.0, pitch: float = 0.0, pause_scale: float = 1.0):
    q = urllib.parse.quote(text)
    query = _http(f"{VOICEVOX_URL}/audio_query?text={q}&speaker={speaker}", data=b"")
    qj = json.loads(query)
    qj["speedScale"] = speed
    qj["intonationScale"] = intonation
    qj["pitchScale"] = pitch
    if "pauseLengthScale" in qj:
        qj["pauseLengthScale"] = pause_scale
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
        if w.exists() and w.stat().st_size > 0:
            wavs.append(w)          # 再開: すでに合成済み(署名が一致した回のみ残っている)
            continue
        if use_vv:
            tts_voicevox(u.tts_text(), w, speaker=(u.speaker or speaker),
                         intonation=u.intonation,
                         speed=(u.speed or DEFAULT_SPEED) * SPEED_SCALE, pitch=u.pitch,
                         pause_scale=u.pause_scale)
        else:
            tts_openjtalk(u.tts_text(), w)
        wavs.append(w)
    return wavs, engine


# ---- BGM(R14: 小さく敷くだけの合成ループ。著作権フリー=自前生成) ----

BGM_OVERRIDE = Path(__file__).resolve().parent / "assets" / "bgm.wav"


BGM_VARIANTS = [
    # (bpm, コード進行)。量産型対策(㉚): 動画ごとにローテーション
    (86, [
        [110.00, 164.81, 196.00, 261.63, 246.94],   # Am9
        [87.31, 130.81, 174.61, 220.00, 196.00],    # Fmaj9
        [130.81, 196.00, 293.66, 329.63, 246.94],   # Cadd9
        [98.00, 146.83, 196.00, 246.94, 220.00],    # G9
    ]),
    (92, [
        [146.83, 220.00, 261.63, 349.23, 329.63],   # Dm9 (D,A,C,F,E)
        [116.54, 174.61, 233.08, 293.66, 261.63],   # Bbmaj9
        [174.61, 261.63, 349.23, 440.00, 392.00],   # Fadd9
        [130.81, 196.00, 261.63, 329.63, 293.66],   # C9
    ]),
    (80, [
        [164.81, 246.94, 293.66, 392.00, 369.99],   # Em9 (E,B,D,G,F#)
        [130.81, 196.00, 246.94, 329.63, 293.66],   # Cmaj9
        [196.00, 293.66, 392.00, 493.88, 440.00],   # Gadd9
        [146.83, 220.00, 293.66, 369.99, 329.63],   # D9
    ]),
]


def synth_bgm(duration: float, out_wav: Path, variant: int = 0):
    """lo-fi風BGM(深掘り③で定石に準拠)。

    - 9th入りボイシング(Am9→Fmaj9→Cadd9→G9)
    - ハットは約66%スウィング(裏拍を遅らせて跳ねさせる)
    - ビニールノイズ(まばらなクラックル+微小ヒス)
    - パッドはローパス相当(高次倍音を絞る)でナレーション帯域を空ける
    production/assets/bgm.wav があればそちらを使う(ローカル工程で実BGMに差し替え可)。
    """
    import numpy as np
    if BGM_OVERRIDE.exists():
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1",
                        "-i", str(BGM_OVERRIDE), "-t", f"{duration:.2f}",
                        "-ar", "44100", "-ac", "1", str(out_wav)], check=True)
        return
    bpm, chords = BGM_VARIANTS[variant % len(BGM_VARIANTS)]
    sr = 44100
    n = int(sr * duration)
    t = np.arange(n) / sr
    beat = 60.0 / bpm
    bar = beat * 4
    rng = np.random.default_rng(20260812 + variant)
    audio = np.zeros(n)
    for bi in range(int(duration / bar) + 1):
        start = bi * bar
        seg = (t >= start) & (t < start + bar)
        if not seg.any():
            continue
        ts = t[seg] - start
        env = np.minimum(ts / 0.7, 1.0) * np.exp(-ts / (bar * 1.5))
        for j, f in enumerate(chords[bi % 4]):
            w = 0.045 if j < 4 else 0.028          # 9thは控えめ
            audio[seg] += w * env * np.sin(2 * np.pi * f * ts)
            audio[seg] += 0.008 * env * np.sin(2 * np.pi * f * 2 * ts)  # 倍音薄め=LPF相当
    swing = 0.66  # ハットのスウィング(60〜74%圏)
    for k in range(int(duration / beat) + 1):
        start = k * beat
        seg = (t >= start) & (t < start + 0.12)
        ts = t[seg] - start
        audio[seg] += 0.13 * np.exp(-ts * 42) * np.sin(2 * np.pi * 50 * ts)  # キック柔らかめ
        for off in (0.0, beat * swing):            # 裏拍を66%位置に(跳ね)
            s2 = (t >= start + off) & (t < start + off + 0.03)
            m = int(s2.sum())
            if m:
                noise = rng.standard_normal(m)
                amp = 0.012 if off else 0.016
                audio[s2] += amp * np.diff(np.concatenate([[0], noise])) * np.exp(-np.arange(m) / (0.008 * sr))
    # ビニールノイズ: 微小ヒス+まばらなクラックル
    audio += 0.0035 * np.diff(np.concatenate([[0], rng.standard_normal(n)]))
    n_crackle = int(duration * 9)
    for pos in rng.integers(0, max(n - 900, 1), n_crackle):
        ln = int(rng.integers(60, 700))
        audio[pos:pos + ln] += rng.uniform(0.01, 0.05) * np.exp(-np.arange(ln) / 90) * rng.choice([-1, 1])
    peak = np.abs(audio).max() or 1.0
    audio = audio / peak * 0.30
    pcm = (audio * 32767).astype("<i2")
    with wave.open(str(out_wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(pcm.tobytes())


SE_DIR = Path(__file__).resolve().parent / "assets" / "se"


def _load_se_file(path: Path, sr: int, max_sec: float = 2.2):
    """実ファイルSE(mp3/wav)をモノラルPCMに読み込む。末尾0.5秒はフェードアウト。"""
    import numpy as np
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-t", f"{max_sec}",
         "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"],
        capture_output=True, check=True,
    ).stdout
    sig = np.frombuffer(raw, dtype="<i2").astype(float) / 32767.0
    fade = min(int(0.5 * sr), len(sig))
    if fade > 0:
        sig[-fade:] *= np.linspace(1, 0, fade)
    peak = np.abs(sig).max() or 1.0
    return sig / peak


def synth_se_track(events: list[tuple[float, str]], duration: float, out_wav: Path):
    """効果音トラック(ループ6)。events=[(秒, 種類)]。強調箇所のみ・入れすぎ禁止。

    pop: テロップ・数字表示のポップ音(短い上昇ブリップ)
    don: オチ・ピーク用の低いドン
    puchun: 電源断音(暗転=スロットのフリーズ演出とセット)
    その他: production/assets/se/<種類>.mp3|wav があれば実ファイルを使う(例: impact)
    """
    import numpy as np
    sr = 44100
    n = int(sr * (duration + 0.5))
    track = np.zeros(n)
    file_cache: dict[str, object] = {}
    for t0, kind in events:
        i0 = int(t0 * sr)
        if kind == "pop":
            dur = 0.09
            ts = np.arange(int(dur * sr)) / sr
            f = 620 + 480 * (ts / dur)  # 上昇ブリップ
            sig = 0.5 * np.sin(2 * np.pi * f * ts) * np.exp(-ts * 34)
        elif kind == "don":
            dur = 0.28
            ts = np.arange(int(dur * sr)) / sr
            f = 130 * np.exp(-ts * 7) + 46
            sig = 0.9 * np.sin(2 * np.pi * f * ts) * np.exp(-ts * 11)
        elif kind == "puchun":
            # 電源断・ブラウン管OFF風「プチュン」(スロットのフリーズ演出)。
            # 高音から一気に落ちるスイープ+冒頭の断線ノイズ
            dur = 0.34
            ts = np.arange(int(dur * sr)) / sr
            f = 60 + 3400 * np.exp(-ts * 22)
            phase = 2 * np.pi * np.cumsum(f) / sr
            sig = 0.85 * np.sin(phase) * np.exp(-ts * 15)
            nz = np.random.default_rng(7).normal(0, 1, len(ts)) * np.exp(-ts * 90) * 0.22
            sig = sig + nz
        else:
            if kind not in file_cache:
                hit = next((SE_DIR / f"{kind}{ext}" for ext in (".wav", ".mp3")
                            if (SE_DIR / f"{kind}{ext}").exists()), None)
                file_cache[kind] = _load_se_file(hit, sr) * 0.9 if hit else None
            if file_cache[kind] is None:
                continue
            sig = file_cache[kind]
        i1 = min(i0 + len(sig), n)
        track[i0:i1] += sig[: i1 - i0]
    # 相対音量を保ったまま過大のみ抑える(1本の大きいSEで全体が痩せないように)
    peak = np.abs(track).max()
    if peak > 1.0:
        track = track / peak
    track = track * 0.5
    pcm = (track * 32767).astype("<i2")
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
             out_mp4: Path, workdir: Path, bgm: bool = True,
             se_events: list[tuple[float, str]] | None = None, bgm_variant: int = 0,
             bgm_mute: list[tuple[float, float]] | None = None):
    """フレーム列+ナレーション(+BGM+SE)をmp4(1080x1920, 30fps)に結合する。"""
    alist = workdir / "audio.txt"
    alist.write_text("".join(f"file '{w.resolve()}'\n" for w in padded_wavs))
    narration = workdir / "narration.wav"
    # ループ㉞: HPF80Hz(不要低域カット)+1.4kHz+2dB(スマホスピーカーは700Hz以下が
    # ほぼ出ないため声の芯を中域で確保)+軽いコンプ → loudnorm の宅録ナレーション定石チェーン
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(alist),
         "-af", "highpass=f=80,equalizer=f=1400:t=q:w=1.2:g=2,"
                "acompressor=threshold=-21dB:ratio=2.5:attack=8:release=120,"
                "loudnorm=I=-14:TP=-1.0:LRA=11", str(narration)],
        check=True,
    )
    total = sum(durations)
    audio_in = narration
    extra = []
    filters = []
    mix_labels = "[0:a]"
    n_in = 1
    if bgm:
        bgm_wav = workdir / "bgm.wav"
        synth_bgm(total + 0.5, bgm_wav, variant=bgm_variant)
        # 深掘り③: ダッキング(発話中はBGMが自動で下がる。動画ミックスの定石)
        filters.append("[0:a]asplit=2[nara][narb]")
        filters.append(
            # 0.6→0.15(video-elements-2026-08.md #12)。実測: 声RMS-27.4dB/BGM生-25.2dB。
            # 0.15でダッキング込みの発話中ギャップ約-22dB(定石: 声より-20dB、ゆっくり系は更に下)
            f"[{n_in}:a]volume=0.15[bgv];"
            "[bgv][narb]sidechaincompress=threshold=0.015:ratio=6:attack=8:release=300:makeup=1[bg]"
        )
        if bgm_mute:
            # 止めの区間はBGMを0にする。ダッキングだけでは release=300ms のせいで
            # 長い間にBGMが戻ってきてしまうので、明示的に切る
            windows = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in bgm_mute)
            filters.append(f"[bg]volume=0:enable='{windows}'[bgq]")
            mix_labels = "[nara][bgq]"
        else:
            mix_labels = "[nara][bg]"
        extra.append(bgm_wav)
        n_in += 1
    if se_events:
        se_wav = workdir / "se.wav"
        synth_se_track(se_events, total, se_wav)
        filters.append(f"[{n_in}:a]volume=0.55[se]")
        mix_labels += "[se]"
        extra.append(se_wav)
        n_in += 1
    if extra:
        mixed = workdir / "mixed.wav"
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(narration)]
        for e in extra:
            cmd += ["-i", str(e)]
        # ループ㉞: 最終ミックスにもloudnormを掛ける。ナレーション単体を-14に正規化しても
        # 間(無音)とBGM/SEの合成で統合ラウドネスが-15.5〜-16に沈み、他チャンネルより
        # 音が小さくなっていた(実測)。YouTubeは音量を上げる方向には正規化しない。
        cmd += ["-filter_complex",
                ";".join(filters) + f";{mix_labels}amix=inputs={n_in}:duration=first:normalize=0"
                # 2026-08-22 実測: TP=-1.0 と書いても、出来上がったmp4の真のピークは
                # -0.2〜-0.8 dBTP しかない(L001 -0.2 / S020 -0.6 / S030 -0.8)。
                # loudnorm の1パス動的モードは真のピークを保証せず、そのあとの
                # AACエンコードがサンプル間ピークを持ち上げるため。ヘッドルームが
                # 無いと、YouTube側の再エンコードで歪む。
                # リミッタを足して測り直した結果: -14.3 LUFS / -0.6 dBTP(0.4dBぶん改善)。
                # ※ 値は実測で決めた。0.841(≒-1.5dBFS)ではL002は-0.8まで下がったが、
                #   **L001は-0.3までしか下がらなかった**。L001はSEが18個(15.9%)と多く、
                #   立ち上がりが鋭いぶんAACのサンプル間ピークが立ちやすい。
                #   0.750 にすると真のピーク-0.9・統合-14.7(実測)。統合は0.3LU下がるが
                #   -14±1.0 の内側なので、ヘッドルームを取るほうを選ぶ
                ",loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.750:level=false",
                str(mixed)]
        subprocess.run(cmd, check=True)
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
         "-c:v", "libx264", "-preset", "medium", "-crf", "15",  # 細字の圧縮にじみ対策(文字潰れ指摘第2弾: 17→15)
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest",
         str(out_mp4)],
        check=True,
    )


# ---- 描画ヘルパ ----

_BG_CACHE = None


def _bg_image():
    """背景のグラデーション+ビネット(深掘りループ①: 純ベタ黒はダサい/四隅暗で中央集中)。

    中心やや上を「色を乗せた黒」で最も明るく、周辺へ沈める。平均は従来のSURFACE近傍を
    保つ(テロップ・チャート色のコントラスト検証を壊さないため)。
    """
    global _BG_CACHE
    if _BG_CACHE is None:
        import numpy as np
        h, w = 240, 135
        y, x = np.mgrid[0:h, 0:w]
        cx, cy = w / 2, h * 0.38
        r = np.sqrt(((x - cx) / (w * 0.85)) ** 2 + ((y - cy) / (h * 0.85)) ** 2)
        base = np.array([0x21, 0x20, 0x1d], float)   # 中心(わずかに暖色の黒)
        edge = np.array([0x12, 0x12, 0x11], float)   # 周辺
        t = np.clip(r, 0, 1)[..., None]
        img = base * (1 - t) + edge * t
        vin = 1 - 0.10 * np.clip((r - 0.72) / 0.38, 0, 1)   # ビネット
        img = img * vin[..., None]
        _BG_CACHE = (img / 255).clip(0, 1)
    return _BG_CACHE


# 長尺のリッチ背景(video-elements-2026-08.md)。定番の「背景+テロップ帯+素材枠」構成:
#   ベース=教科書モチーフ(罫線ノート+紙目+ビネット、明度一段上げ)
#   動き=薄い円貨(¥)モチーフが斜めにゆっくり流れる(「常にどこかが動く」の定石)
#   枠=中央コンテンツ領域の角丸パネル / 章チップ=左上に常時表示(章ごとに色替え)
RICH_BG = False
DRIFT_FPS = 4            # 静止ユニットでも背景を流すためのフレームレート
CURRENT_BAND = None      # (章ラベル, 色)。render_video が bands から units ごとに設定
_BG_CACHE_RICH = None


def use_rich_bg():
    global RICH_BG
    RICH_BG = True


def _bg_image_rich():
    global _BG_CACHE_RICH
    if _BG_CACHE_RICH is None:
        import numpy as np
        h, w = 240, 135
        y, x = np.mgrid[0:h, 0:w]
        cx, cy = w / 2, h * 0.38
        r = np.sqrt(((x - cx) / (w * 0.85)) ** 2 + ((y - cy) / (h * 0.85)) ** 2)
        base = np.array([0x2b, 0x2a, 0x25], float)   # 中心(明るめの紙色がかった黒)
        edge = np.array([0x17, 0x16, 0x14], float)
        t = np.clip(r, 0, 1)[..., None]
        img = base * (1 - t) + edge * t
        vin = 1 - 0.12 * np.clip((r - 0.70) / 0.40, 0, 1)
        img = img * vin[..., None]
        _BG_CACHE_RICH = (img / 255).clip(0, 1)
    return _BG_CACHE_RICH


def _draw_rich_layers(fig, bg_ax, t: float):
    import numpy as np
    # 罫線ノート(横罫+左の縦罫。ごく薄く)
    for k in range(1, 12):
        bg_ax.axhline(k / 12, color="#8a8578", linewidth=0.7, alpha=0.055)
    bg_ax.axvline(0.045, color="#b0846a", linewidth=1.0, alpha=0.10)
    # 流れる円貨モチーフ(疑似乱数は添字から決める。Date系は使わない)
    for i in range(7):
        sx = ((i * 0.161 + 0.07) + t * 0.010) % 1.16 - 0.08
        sy = ((i * 0.379 + 0.15) + t * 0.006) % 1.16 - 0.08
        rr = 0.025 + (i % 3) * 0.013
        c = plt.Circle((sx, sy), rr, fill=False, color="#c8bfa5",
                       linewidth=1.4, alpha=0.05)
        bg_ax.add_patch(c)
        bg_ax.text(sx, sy, "¥", ha="center", va="center", color="#c8bfa5",
                   fontsize=rr * 900, alpha=0.05)
    # 素材表示枠(中央コンテンツの角丸パネル)
    from matplotlib.patches import FancyBboxPatch
    panel = FancyBboxPatch((0.030, 0.225), 0.940, 0.680,
                           boxstyle="round,pad=0.008,rounding_size=0.015",
                           facecolor="#ffffff", alpha=0.030,
                           edgecolor="#8a8578", linewidth=1.2)
    panel.set_alpha(None)
    panel.set_facecolor((1, 1, 1, 0.030))
    panel.set_edgecolor((0.54, 0.52, 0.47, 0.28))
    bg_ax.add_patch(panel)
    # 章チップ(左上に常時表示。色は章ごと)
    if CURRENT_BAND:
        label, color = CURRENT_BAND
        fig.text(0.028, 0.945, label, ha="left", va="center", color="#17202a",
                 fontsize=BADGE_FS, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.45", facecolor=color, edgecolor="none"))


def new_canvas(t_global: float = 0.0):
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor(SURFACE)
    bg = fig.add_axes([0, 0, 1, 1], zorder=-10)
    if RICH_BG:
        bg.imshow(_bg_image_rich(), extent=[0, 1, 0, 1], aspect="auto",
                  interpolation="bicubic")
        bg.set_xlim(0, 1)
        bg.set_ylim(0, 1)
        _draw_rich_layers(fig, bg, t_global)
    else:
        bg.imshow(_bg_image(), extent=[0, 1, 0, 1], aspect="auto", interpolation="bicubic")
    bg.axis("off")
    return fig


def draw_glow_text(fig, x: float, y: float, text: str, fontsize: float, color: str = None):
    # 既定値を def 時に写すと set_accent が効かない。呼び出し時に解決する(ループ71)
    if color is None:
        color = EMPH
    """ヒーロー数字用: 影+グロー+縁取りの3層で立体感を出す(深掘りループ①)。"""
    fig.text(x, y - 0.007, text, ha="center", va="center", color="#000000",
             fontsize=fontsize, alpha=0.5,
             path_effects=[path_effects.Stroke(linewidth=12, foreground="#000000"),
                           path_effects.Normal()])
    fig.text(x, y, text, ha="center", va="center", color=color, fontsize=fontsize,
             alpha=0.28,
             path_effects=[path_effects.Stroke(linewidth=30, foreground=color),
                           path_effects.Normal()])
    fig.text(x, y, text, ha="center", va="center", color=color, fontsize=fontsize,
             path_effects=stroke_fx(color, outline=outline_for(fontsize) * 1.0, fatten=4))


# 縁取りの色と影。**テーマが差し替える**(既定は旧デザインの黒縁・影なし)。
# 競合のテロップは「太い色つきの縁 + 下に落ちる影」で、背景から浮いている。
# 黒縁だけだと明るい背景の上でべたっと沈む(2026-08-23の見比べ)
STROKE_EDGE = "#000000"
STROKE_SHADOW = None       # (dx_pt, dy_pt, 色, 濃さ) または None


def stroke_fx(text_color: str, outline: float = 7.0, fatten: float = 2.0):
    """R7: 縁取り+同色ストローク。縁取りは文字サイズの約10%が基準(深掘り⑥)。
    呼び出し側は outline_for(fontsize) を使うこと。"""
    fx = []
    if STROKE_SHADOW:
        dx, dy, col, al = STROKE_SHADOW
        fx.append(path_effects.Stroke(offset=(dx, dy), linewidth=outline * 1.10,
                                      foreground=col, alpha=al))
    fx += [
        path_effects.Stroke(linewidth=outline, foreground=STROKE_EDGE),
        path_effects.Stroke(linewidth=fatten, foreground=text_color),
        path_effects.Normal(),
    ]
    return fx


def outline_for(fontsize: float) -> float:
    """縁取り太さ=文字サイズの10%(定石5〜10%の上限。深掘り⑥)。"""
    return fontsize * 0.10


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
        if ch in "、。!?…":  # …も句境界(タメの後で折り返せるように。ループ⑫)
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


# (文字列, fontsize, weight, W) → 幅(図の割合)。フレームをまたいで使い回す。
# 同じ字幕を何十枚も描くので、ここのキャッシュが効く(実測 1312ms → 後述)
_WIDTH_CACHE: dict = {}


def _measure_widths(fig, renderer, segs, fs, weight):
    """セグメントごとの幅(図幅に対する割合)。測った値はキャッシュする。"""
    out = []
    for s, _ in segs:
        key = (s, round(fs, 3), weight, W)
        w = _WIDTH_CACHE.get(key)
        if w is None:
            tmp = fig.text(0, -1, s, fontsize=fs, fontweight=weight)
            w = tmp.get_window_extent(renderer=renderer).width / W
            tmp.remove()
            _WIDTH_CACHE[key] = w
        out.append(w)
    return out


def _needs_measure(segs, fs, weight):
    return any((s, round(fs, 3), weight, W) not in _WIDTH_CACHE for s, _ in segs)


def draw_rich_line(fig, y: float, segs: list[tuple[str, bool]], fontsize: float,
                   base_color: str = INK, emph_color: str = None,
                   outline: float | None = None, ha_center_x: float = 0.5,
                   weight: str = "black"):
    if emph_color is None:
        emph_color = EMPH
    """強調色の混在する1行を中央揃えで描く(実測幅で並べ、幅超過なら自動縮小)。"""
    # canvas.draw() は1フレーム描くのと同じ重さ。測る必要があるときだけ呼ぶ
    renderer = None
    if _needs_measure(segs, fontsize, weight):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()

    def measure(fs):
        nonlocal renderer
        if renderer is None and _needs_measure(segs, fs, weight):
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
        return _measure_widths(fig, renderer, segs, fs, weight)

    widths = measure(fontsize)
    total = sum(widths)
    if total > 0.86:  # 深掘り⑧: 見切れの根絶(画面幅86%に自動フィット)
        fontsize = fontsize * 0.86 / total
        widths = measure(fontsize)
        total = sum(widths)
    if outline is None:
        outline = outline_for(fontsize)
    x = ha_center_x - total / 2
    for (s, emph), w in zip(segs, widths):
        color = emph_color if emph else base_color
        fig.text(x, y, s, ha="left", va="center", color=color, fontsize=fontsize,
                 fontweight=weight, path_effects=stroke_fx(color, outline=outline))
        x += w


def fit_fontsize(fig, text: str, fontsize: float,
                 max_w: float = 0.92, min_scale: float = 0.55) -> float:
    """画面幅の max_w に収まる字の大きさを返す(ループ71)。

    S016 の締めの見出しが左右とも画面外に切れたまま、11本のゲートを全部通った。
    原因は**字の大きさが固定**で、長い文はそのまま枠の外に出ていたこと。
    ここで測って縮める。収まっているときは元の大きさをそのまま返すので、
    既存の画面は1ドットも変わらない。

    min_scale より小さくはしない。そこまで縮めないと入らない文は、
    縮めても読めないので**文のほうを短くするべき**であり、
    check_overlap.py の「画面外」で落として書き直させる。
    """
    if not text or not text.strip():
        return fontsize
    try:
        r = fig.canvas.get_renderer()
    except Exception:
        return fontsize
    fw = fig.canvas.get_width_height()[0]
    probe = fig.text(0.0, -1.0, text, fontsize=fontsize)
    try:
        w = probe.get_window_extent(renderer=r).width / fw
    finally:
        probe.remove()
    if w <= max_w or w <= 0:
        return fontsize
    return max(fontsize * max_w / w, fontsize * min_scale)


def text_fit(fig, x: float, y: float, s: str, fontsize: float,
             max_w: float = 0.92, **kw):
    """fig.text と同じだが、画面幅に収まるまで字を縮める。"""
    return fig.text(x, y, s, fontsize=fit_fontsize(fig, s, fontsize, max_w), **kw)


def draw_rich_text(fig, x: float, y: float, text: str, fontsize: float,
                   base_color: str = INK, emph_color: str = None,
                   outline: float | None = None, wrap: int = 0, line_h: float = 0.034,
                   block_fit: float | None = None):
    if emph_color is None:
        emph_color = EMPH
    """【】強調に対応したテキスト描画(中央揃え)。wrap>0で折り返し。

    block_fit: 最長行がこの幅(図の割合)に収まるようブロック全体を等縮小する。
    行ごとの自動縮小(0.86)と違い、ユニット内で文字サイズが揃う(ループ⑫)。
    """
    if outline is None:
        outline = outline_for(fontsize)
    lines = wrap_rich(text, wrap) if wrap else [parse_rich(text)]
    if block_fit:
        need = any(_needs_measure(segs, fontsize, "black") for segs in lines)
        renderer = None
        if need:
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
        worst = 0.0
        for segs in lines:
            total = sum(_measure_widths(fig, renderer, segs, fontsize, "black"))
            worst = max(worst, total)
        if worst > block_fit:
            fontsize = fontsize * block_fit / worst
            outline = outline_for(fontsize)
    for i, segs in enumerate(lines):
        draw_rich_line(fig, y - i * line_h * (fontsize / 40), segs, fontsize,
                       base_color=base_color, emph_color=emph_color,
                       outline=outline, ha_center_x=x)


def draw_subtitle(fig, text: str, pop: float = 1.0, tag: str | None = None):
    """R6/R7/R8: ナレーション文そのものを縁取りテロップで。【】は黄色。

    pop>1 で表示直後の「ポン」(スケール収束)を表現する(ループ10)。
    block_fit=0.70: 字幕はShorts右ボタン列(x>0.85)に掛けない(x 0.15〜0.85。ループ⑫)。
    横型(use_landscape)ではUIを避ける必要がないので 0.86 まで広げる。
    tag: 話者名(二人会話)。リッチ背景では字幕帯の左端に話者色ラインを敷き、
    立ち絵を消した図ユニットでも話者が視覚で分かるようにする(video-elements-2026-08.md)。
    頭上の名前プレート(draw_speaker_plate)と併用。
    """
    if RICH_BG:
        # テロップ帯(定番の「テロップ背景」)。行数で高さを変えるとユニット間で
        # ちらつくので、2行ぶんの固定帯にする
        top = SUBTITLE_Y + SUB_LINE_H * 0.80
        bot = SUBTITLE_Y - SUB_LINE_H * 1.55
        fig.add_artist(plt.Rectangle((0.0, bot), 1.0, top - bot,
                                     transform=fig.transFigure,
                                     facecolor="#0b0b0a", alpha=0.52, zorder=2.4))
        if tag:
            color = METAN_TAG_COLOR if tag == "めたん" else ZUNDA_TAG_COLOR
            fig.add_artist(plt.Rectangle((0.0, bot), 0.007, top - bot,
                                         transform=fig.transFigure,
                                         facecolor=color, alpha=0.95, zorder=2.5))
    draw_rich_text(fig, 0.5, SUBTITLE_Y, text, SUB_FS * pop, wrap=SUB_WRAP, line_h=SUB_LINE_H,
                   block_fit=SUB_BLOCK_FIT)


def draw_speaker_plate(fig, name: str):
    """二人会話: 話している側の頭上に名前プレートを出す(緑=ずんだもん/ピンク=めたん)。
    位置は立ち絵rectから計算するので縦型・横型どちらでも合う。"""
    import metan as _metan
    if name == "めたん":
        x0, y0, w_fr, h_fr = CHARA_RECTS["br"]
        art_w_fr = h_fr * H * (_metan.ART_W / _metan.ART_H) / W
        cx = x0 + w_fr - art_w_fr / 2
        color = METAN_TAG_COLOR
    else:
        x0, y0, w_fr, h_fr = CHARA_RECTS["bl"]
        cx = x0 + w_fr / 2
        color = ZUNDA_TAG_COLOR
    fig.text(cx, y0 + h_fr + 0.028, name, ha="center", va="center",
             color="#17202a", fontsize=BADGE_FS * 0.95, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.45", facecolor=color, edgecolor="none"))


def draw_badge(fig, text: str):
    """右上の注記バッジ(例:「年利5%と仮定の計算」)。打消し表示(戦略§6)。

    y=0.83: Shorts実機UIの安全域(深掘りループ⑩)。上部アイコン帯(上7%)の外、
    かつ右ボタン列(上40%〜)より上。0.935だと検索・カメラアイコンと重なる。
    fontsize=28: 動画の打消し表示は「強調表示の20〜30%未満の文字で2秒以下」だと
    読まれない(消費者庁・打消し表示実態調査)。常時表示+字幕(52pt)の54%を確保(深掘りループ⑫)。
    """
    fig.text(
        BADGE_XY[0], BADGE_XY[1], text, ha="right", va="center", color=INK_2, fontsize=BADGE_FS,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=SURFACE, edgecolor=BASELINE, linewidth=1.5),
    )


def draw_footer_brand(fig, text: str):
    fig.text(BRAND_XY[0], BRAND_XY[1], text, ha="center", va="center",
             color=MUTED, fontsize=BRAND_FS)


def require_voicevox():
    """レンダリング前のプリフライト。VOICEVOX未起動のままフォールバックTTSで
    合成すると「声がずんだもんでないのにクレジットあり」の事故になるため、
    本チャンネルの動画は必ずこれを呼んでから render_video する。"""
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:50021/version", timeout=5) as r:
            r.read()
    except Exception as e:
        raise SystemExit(
            f"VOICEVOXエンジンに接続できません({e})。"
            "先に `bash production/setup_voicevox.sh` を実行してください。"
        )


def style_axes(ax):
    ax.set_facecolor("none")  # 背景グラデーションを透かす
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(BASELINE)
        ax.spines[s].set_linewidth(1.5)
    ax.tick_params(colors=MUTED, labelsize=20, length=0)
    ax.grid(axis="y", color=GRID, linewidth=1.2)
    ax.set_axisbelow(True)


def save_frame(fig, path: Path, facecolor: str = SURFACE):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, facecolor=facecolor)
    plt.close(fig)


# 立ち絵のオーバーレイ位置(deep-loops ㉙: 字幕の上・セーフエリア内。字幕=最前面のZ順)
CHARA_RECTS = {
    "bl": [0.000, 0.245, 0.342, 0.22],
    "br": [0.658, 0.245, 0.342, 0.22],
}


def draw_chara(fig, pos: str, mouth: int, eyes: str, expr: str, dy: float = 0.0,
               alpha: float = 1.0):
    from zunda import draw_zunda
    ax = fig.add_axes(CHARA_RECTS[pos])
    ax.axis("off")
    # dyは13スケール単位 → 素材915pxに換算(呼吸±0.10→7px、ジャンプ0.5→35px)。
    # 素材は左向きなので、左下配置では反転して画面内側(右)を向かせる(ミラー定石)
    draw_zunda(ax, mouth=mouth, eyes=eyes, expr=expr, dy_px=dy / 13.0 * 915.0,
               flip=(pos == "bl"), alpha=alpha)


def draw_metan_chara(fig, talking: bool, t: float, alpha: float = 1.0):
    """めたん(右下・公式ポートレート)。素材300×500の縦横比を保つため、
    右下rectの高さを使い、幅は比から出して**右端に寄せる**。"""
    import metan
    from zunda import breath_offset
    x0, y0, w_fr, h_fr = CHARA_RECTS["br"]
    art_w_fr = h_fr * H * (metan.ART_W / metan.ART_H) / W
    ax = fig.add_axes([x0 + w_fr - art_w_fr, y0, art_w_fr, h_fr])
    ax.axis("off")
    dy = breath_offset(t * 0.93, 13, 2.4) / 13.0 * metan.ART_H
    dy += metan.talk_bob_px(t, talking)
    metan.draw_metan(ax, dy_px=dy, alpha=alpha)


def render_video(units: list[Unit], scene_painters: dict, outdir: Path, out_name: str,
                 speaker: int = DEFAULT_SPEAKER, bgm: bool = True,
                 chara: bool = True, bgm_variant: int | None = None,
                 bands: list[tuple[int, str, str]] | None = None) -> dict:
    """ユニット列とシーン描画関数からmp4を作る。

    scene_painters: {scene名: painter(fig, t)}。tはユニット内アニメーションの進行度
    (0→1、静止ユニットでは常に1.0)。
    chara=True でずんだもん立ち絵(口パク・目パチ・呼吸・表情)を合成(deep-loops ㉙)。
    bgm_variant: BGMのローテーション(未指定は動画名から決定。量産型対策㉚)。
    """
    from zunda import mouth_track, BlinkSchedule, breath_offset, CHARA_FPS
    setup_fonts()
    workdir = outdir / "work"
    workdir.mkdir(parents=True, exist_ok=True)

    # ---- 途中で死んでも再開できるようにする(ループ68)
    #
    # このコンテナはセッションがアイドルになると回収される。9分の動画は
    # レンダリングに2〜3時間かかるので、**必ず途中で殺される**。
    # 毎回ゼロからやり直していると永久に終わらないので、作業を残して再開する。
    #
    # ただし台本を直したのに古いフレームを使ってしまうと最悪なので、
    # **台本と調声の署名が一致したときだけ**残す。1文字でも変えたら捨てる。
    sig = render_signature(units, scene_painters, speaker, bgm, chara, out_name,
                           bands=bands)
    sig_file = workdir / "signature.txt"
    resumed = sig_file.exists() and sig_file.read_text().strip() == sig
    # **署名は「何を描くか」しか見ていない。「どこにどう描くか」は見ていない。**
    # render_signature が見るのは units と SCENES の**キー**なので、
    # scenes_long.py / shortlib.py の中で文字の位置や幅を直しても署名は変わらない。
    # そのまま再開すると、**古いレイアウトのフレームが残ったまま
    # 「再レンダリング済み」の動画が出る**(2026-08-22に踏みかけた)。
    # 描画モジュールが署名より新しければ、再開せずに全部描き直す。
    if resumed:
        _here = Path(__file__).resolve().parent
        _src = [Path(__file__).resolve()] + [
            _here / n for n in ("scenes_long.py", "scenes_common.py",
                                "scenes_fp.py", "fplib.py")]
        newest = max((f.stat().st_mtime for f in _src if f.exists()), default=0)
        if newest > sig_file.stat().st_mtime:
            print("[resume] 描画モジュールが署名より新しい。"
                  "レイアウトが変わっている可能性があるのでフレームを捨てて描き直します")
            resumed = False
    if not resumed:
        for old in workdir.glob("frame_*.png"):
            old.unlink()
        for old in workdir.glob("seg_*.wav"):  # ユニット数が減った再レンダリングでの残留(㊲)
            old.unlink()
        sig_file.write_text(sig)
    else:
        n_done = len(list(workdir.glob("frame_*.png")))
        print(f"[resume] 署名が一致。フレーム{n_done}枚と音声を再利用します")

    wavs, engine = synthesize(units, workdir, speaker=speaker)

    seed = sum(ord(c) for c in out_name)
    if bgm_variant is None:
        bgm_variant = seed % len(BGM_VARIANTS)
    blink = BlinkSchedule(seed)
    breath_phase = (seed % 7) * 0.9

    frames, durations, padded = [], [], []
    unit_secs: list[float] = []   # ユニットごとの尺(長尺のチャプター時刻を出すため)
    se_events: list[tuple[float, str]] = []
    bgm_mute: list[tuple[float, float]] = []   # BGMを完全に切る区間(止め)
    elapsed = 0.0
    thumbnail = None
    for i, (u, w) in enumerate(zip(units, wavs)):
        # 章チップ(左上)の表示内容をこのユニットの章に合わせる
        global CURRENT_BAND
        CURRENT_BAND = None
        if bands:
            for start, label, color in bands:
                if i >= start:
                    CURRENT_BAND = (label, color)
        pw = workdir / f"seg_{i:02d}_pad.wav"
        pad_wav(w, pw, u.pad)
        d_total = duration_of(pw)
        padded.append(pw)
        unit_secs.append(d_total)
        # 長い「止め」の間はBGMも切る(ループ71 フェーズ8)。
        # ダッキングの release は300msなので、0.6秒の間を作ると
        # **その間にBGMが戻ってきて盛り上がる**。止めたつもりが逆になる。
        if u.pad >= LONG_STOP_PAD:
            bgm_mute.append((elapsed + d_total - u.pad, elapsed + d_total))
        if u.se:
            se_events.append((elapsed + (0.07 if u.cover else 0.0) + u.se_at, u.se))
        if u.puchun:
            # ユニット頭に「プチュン」(u.seはリベール側=se_atで少し後に鳴らせる)
            se_events.append((elapsed + (0.07 if u.cover else 0.0), "puchun"))

        chara_on = chara and u.chara != "none"
        mtrack = mouth_track(pw, CHARA_FPS) if chara_on else []

        def emit(t: float, sub_idx: int, dur: float, pop: float = 1.0,
                 painter=None, with_subtitle: bool = True,
                 t_unit: float = 0.0, static_chara: bool = False, no_chara: bool = False):
            f = workdir / f"frame_{i:02d}_{sub_idx:03d}.png"
            # 再開: すでにあるフレームは**描かずに**飛ばす。
            # 最初は savefig だけ飛ばしていたが、重いのは描画のほうなので効果が無かった。
            if resumed and f.exists() and f.stat().st_size > 0:
                frames.append(f)
                durations.append(dur)
                return f
            fig = new_canvas(elapsed + t_unit)
            (painter or scene_painters[u.scene])(fig, t)
            if chara_on and not no_chara:
                tg = elapsed + t_unit
                if static_chara:
                    mouth = 0
                else:
                    mi = min(len(mtrack) - 1, max(0, int(t_unit * CHARA_FPS)))
                    mouth = mtrack[mi] if mtrack else 0
                dy = breath_offset(tg, 13, breath_phase)
                # 強調ジャンプ(㉙R9: SE/驚きのユニット頭で1回。高さ約4%)
                if not static_chara and (u.se in ("don", "impact") or u.face == "surprised"):
                    bt = t_unit - (0.07 if u.cover else 0.0)
                    if 0 <= bt < 0.35:
                        dy += 0.5 * math.sin(math.pi * bt / 0.35)
                if DUO:
                    # 二人会話: ずんだもん左(聞き手)・めたん右(解説役)。
                    # 口パク/ボブは話者側だけ、非話者は減光(duo-skit-2026-08.md)。
                    z_active = (u.speaker or DEFAULT_SPEAKER) != METAN_SPEAKER
                    draw_chara(fig, "bl", mouth if z_active else 0,
                               blink.eyes(tg) if not static_chara else "open",
                               u.face, dy if z_active else breath_offset(tg, 13, breath_phase),
                               alpha=1.0 if z_active else 0.72)
                    draw_metan_chara(fig, talking=(not z_active and mouth > 0 and not static_chara),
                                     t=tg, alpha=0.72 if z_active else 1.0)
                    draw_speaker_plate(fig, "ずんだもん" if z_active else "めたん")
                else:
                    draw_chara(fig, u.chara, mouth,
                               blink.eyes(tg) if not static_chara else "open", u.face, dy)
            if with_subtitle:
                tag = None
                if DUO:
                    tag = ("めたん" if (u.speaker or DEFAULT_SPEAKER) == METAN_SPEAKER
                           else "ずんだもん")
                draw_subtitle(fig, u.subtitle, pop=pop, tag=tag)
            save_frame(fig, f)
            frames.append(f)
            durations.append(dur)
            return f

        anim = min(u.anim, d_total)
        head = 0.07 if u.cover else 0.0
        if u.cover:
            # フィードの静止表示・サムネ用(ループ7)。専用構図 <scene>__cover があれば
            # 字幕なしのサムネ設計で描く(深掘り⑨)
            cover_painter = scene_painters.get(f"{u.scene}__cover")
            cf = emit(1.0, 990, 0.07, painter=cover_painter,
                      with_subtitle=(cover_painter is None), no_chara=True)
            thumbnail = cf
        anim = min(anim, d_total - head)
        if anim > 0:
            n = max(2, int(anim * u.fps))
            for k in range(n):
                t = (k + 1) / n
                emit(t, k, anim / n, pop=(1.06 if k == 0 else 1.0),
                     t_unit=head + anim * (k + 0.5) / n)
            hold = d_total - anim - head
            if hold > 0.01:
                if chara_on:
                    m = max(1, int(round(hold * CHARA_FPS)))
                    for j in range(m):
                        emit(1.0, n + j, hold / m,
                             t_unit=head + anim + hold * (j + 0.5) / m)
                elif RICH_BG:
                    # 背景が流れるので、立ち絵なしの静止区間も低fpsで割る(常に動く画面)
                    m = max(1, int(round(hold * DRIFT_FPS)))
                    for j in range(m):
                        emit(1.0, n + j, hold / m,
                             t_unit=head + anim + hold * (j + 0.5) / m)
                else:
                    emit(1.0, n, hold)
        else:
            body = d_total - head
            if chara_on:
                m = max(1, int(round(body * CHARA_FPS)))
                for j in range(m):
                    emit(1.0, j, body / m, t_unit=head + body * (j + 0.5) / m)
            elif RICH_BG:
                m = max(1, int(round(body * DRIFT_FPS)))
                for j in range(m):
                    emit(1.0, j, body / m, t_unit=head + body * (j + 0.5) / m)
            else:
                emit(1.0, 0, body)
        elapsed += d_total

    out_mp4 = outdir / out_name
    assemble(frames, durations, padded, out_mp4, workdir, bgm=bgm, se_events=se_events,
             bgm_variant=bgm_variant, bgm_mute=bgm_mute)
    if thumbnail is not None:
        import shutil
        shutil.copy(thumbnail, outdir / "thumbnail.png")
    return {"mp4": out_mp4, "engine": engine, "total_sec": sum(durations),
            "unit_secs": unit_secs}
