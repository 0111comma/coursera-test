#!/usr/bin/env python3
"""台本(render.pyのUNITS)とレンダリング済み音声から字幕SRTを生成する。

根拠(投稿メタデータ調査): 手動字幕は自動字幕より信頼されて別途インデックスされ、
金融用語の誤認識(ニーサ/イデコ/高額療養費 等)を防ぐ。台本があるので追加コストゼロ。
タイミングは output/work/seg_XX_pad.wav の実測時間(=動画のタイムライン)から取る。
"""
import re
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def wav_duration(p: Path) -> float:
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / w.getframerate()


def fmt(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms//3600000:02d}:{ms%3600000//60000:02d}:{ms%60000//1000:02d},{ms%1000:03d}"


def main():
    for d in sorted(ROOT.glob("videos/[SL]0*")):
        sid = d.name.split("-")[0]
        if not (d / "render.py").exists():
            continue          # verify.pyだけの下ごしらえ段階(台本前)はスキップ
        src = (d / "render.py").read_text()
        subs = [s.replace("【", "").replace("】", "")
                for s in re.findall(r'Unit\(\s*"[^"]+",\s*"([^"]+)"', src)]
        # **辞書順で並べてはいけない。** seg_{i:02d} は i>=100 で3桁になるため、
        # sorted() だと seg_09 の次に seg_100 が来て、100ユニットを超える長尺の
        # 字幕の時刻が最大14.6秒ずれる(L001で実際に出荷してしまった。2026-08-21に発見)。
        # 動画本体は shortlib が順序どおりのリストで結合しているので無事だった。
        segs = sorted((d / "output" / "work").glob("seg_*_pad.wav"),
                      key=lambda q: int(re.search(r"seg_(\d+)_pad", q.name).group(1)))
        if len(segs) != len(subs):
            print(f"{sid}: seg数{len(segs)} != unit数{len(subs)} — スキップ(再レンダリングが必要)")
            continue
        t = 0.0
        lines = []
        for i, (sub, seg) in enumerate(zip(subs, segs), 1):
            dur = wav_duration(seg)
            lines.append(f"{i}\n{fmt(t)} --> {fmt(t + dur - 0.05)}\n{sub}\n")
            t += dur
        out = ROOT / "uploads" / f"{sid}.srt"
        out.write_text("\n".join(lines))
        print(f"{sid}.srt ✓ ({len(subs)}行・{t:.1f}s)")


if __name__ == "__main__":
    main()
