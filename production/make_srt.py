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


def vv_durations(subs):
    """音声wavが無いときに、VOICEVOXの音素長からユニットごとの秒を出す。
    エンジンが起動していなければ None(そのときは古いsrtを消す)。"""
    import json
    import urllib.parse
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:50021/version", timeout=3).read()
    except Exception:
        return None
    import shortlib as S
    out = []
    for text in subs:
        for a, b in S.READING.items():
            text = text.replace(a, b)
        url = ("http://127.0.0.1:50021/audio_query?text="
               f"{urllib.parse.quote(text)}&speaker=3")
        try:
            q = json.load(urllib.request.urlopen(
                urllib.request.Request(url, method="POST"), timeout=30))
        except Exception:
            return None
        raw = 0.0
        for ap in q["accent_phrases"]:
            for mo in ap["moras"]:
                raw += (mo.get("consonant_length") or 0) + (mo["vowel_length"] or 0)
            if ap.get("pause_mora"):
                pm = ap["pause_mora"]
                raw += (pm.get("consonant_length") or 0) + (pm["vowel_length"] or 0)
        out.append((raw + 0.15) / S.SPEED_SCALE + 0.15)
    return out


def main():
    stale, estimated = [], []
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
            # **スキップして古いファイルを残してはいけない。**
            # 2026-08-22に発覚: uploads/S010.srt の中身が年金の動画、S015.srt が退職金の動画
            # だった。IDを付け替えたあと音声が無くてスキップされ、**別動画の字幕が
            # 公開済みの動画のキットに残り続けていた**。
            # 音声が無いときは VOICEVOX の音素長で秒を出して、必ず作り直す。
            durs = vv_durations(subs)
            if durs is None:
                out = ROOT / "uploads" / f"{sid}.srt"
                if out.exists():
                    out.unlink()
                    print(f"{sid}: 音声もVOICEVOXも無い。**古い{sid}.srtを削除**"
                          f"(別動画の字幕が残る事故を防ぐため)")
                stale.append(sid)
                continue
            print(f"{sid}: 音声が無いのでVOICEVOXの音素長から作成(実測ではない)")
            estimated.append(sid)
        else:
            durs = [wav_duration(p) for p in segs]
        t = 0.0
        lines = []
        for i, (sub, dur) in enumerate(zip(subs, durs), 1):
            lines.append(f"{i}\n{fmt(t)} --> {fmt(t + dur - 0.05)}\n{sub}\n")
            t += dur
        out = ROOT / "uploads" / f"{sid}.srt"
        out.write_text("\n".join(lines))
        mark = "(推定)" if sid in estimated else ""
        print(f"{sid}.srt ✓ ({len(subs)}行・{t:.1f}s){mark}")


    if stale or estimated:
        if stale:
            print(f"\n[NG] 音声もVOICEVOXも無く作れなかった: {', '.join(stale)}"
                  f"(古いsrtは消した。レンダリングするか、VOICEVOXを起動して再実行)")
        if estimated:
            print(f"[WARN] 実測ではなく推定で作った: {', '.join(estimated)}")
        raise SystemExit(1 if stale else 0)


if __name__ == "__main__":
    main()
