#!/usr/bin/env python3
"""専門語の定訳と、直訳調の型を落とす機械ゲート(2026-09-05)。

ユーザー指摘(2026-09-05):
  「もうちょっと日本語ちゃんとしたい。英語を直訳したものに見えるので
    しっかり専門用語は日本語で使われている表現をしましょう。」

Z001 は、専門語を全部**その場の言い換え**で済ませていた:
  権内にあるもの → 「変えられるもの」/ 判断 → 「受け取り方」/
  論理療法 → 「いまの考えを直す治療」/ ABC理論 → 「考えを紙に書く」
言い換え自体は視聴者に必要だが、**定訳を一度も言わない**と、
(a) 調べようがない (b) 英語の概念を素人が訳し下ろした文に見える。
だから「定訳を1回は言い、そのうえで言い換える」を規則にする。

判定(render.py の UNITS = 読み上げる字幕に対して):
  T1 定訳の欠落 : production/teiyaku.txt の「言い換え」がナレーションにあるのに、
                  対応する**定訳が1回も出てこない**
  T2 接続語の偏り: 同じ語で始まる文が全体の CONJ_MAX_RATIO を超える
                  (「で、」を機械ゲート対策で貼ると起きる。日本語として不自然)
  T3 対比の直訳 : 「AじゃなくB」「AではなくB」の対比が CONTRAST_MAX 回を超える
                  (not A but B の直訳。日本語は「Aのせいじゃない。Bのせい」と切る)
  T4 「〜の。」止め: 説明文の「〜なの。」「〜たの。」が全体の NANO_MAX_RATIO を超える
                  (幼い口調が続くと、内容のある話が軽く聞こえる)

免除: production/gate_exempt.txt に `<ID>:teiyaku:<ユニット番号|*>  # 理由`
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCTION = ROOT / "production"
sys.path.insert(0, str(PRODUCTION))

CONJ_MAX_RATIO = 0.22     # 同じ接続語で始まる文の上限(全体に対する割合)
CONTRAST_MAX = 3          # 「〜じゃなく〜」の対比の上限
NANO_MAX_RATIO = 0.34     # 「〜なの。」「〜たの。」の上限
CONJ_HEADS = ("で、", "だから", "でも", "しかも", "そして", "じゃあ", "なのに", "つまり", "ただ")


def load_terms():
    f = PRODUCTION / "teiyaku.txt"
    out = []
    for ln in f.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) >= 2:
            out.append((parts[0], [w for w in parts[1].split(",") if w],
                        parts[2] if len(parts) > 2 else ""))
    return out


def load_exempt(gate: str):
    f = PRODUCTION / "gate_exempt.txt"
    out = {}
    if not f.exists():
        return out
    for ln in f.read_text().splitlines():
        body, _, reason = ln.partition("#")
        parts = body.strip().split(":")
        if len(parts) == 3 and parts[1] == gate and reason.strip():
            out.setdefault(parts[0], set()).add(parts[2].strip())
    return out


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"t_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def check_video(vdir: Path):
    rp = vdir / "render.py"
    if not rp.exists():
        return []
    subs = [u.subtitle.replace("【", "").replace("】", "")
            for u in getattr(_load(rp), "UNITS", [])]
    n = len(subs)
    if not n:
        return []
    joined = "".join(subs)
    issues = []

    # T1 定訳の欠落
    for teiyaku, iikae, src in load_terms():
        bare = teiyaku.strip("『』")
        if bare in joined or teiyaku in joined:
            continue
        hit = [w for w in iikae if w in joined]
        if hit:
            issues.append(("(全体)", "T1 定訳を言っていない",
                           f"「{hit[0]}」と言い換えているのに、定訳「{teiyaku}」が1回も出てこない。"
                           f"初出で1回言ってから言い換えること。{src}"))

    # T2 接続語の偏り
    for head in CONJ_HEADS:
        c = sum(1 for s in subs if s.startswith(head))
        if c > n * CONJ_MAX_RATIO:
            issues.append(("(全体)", "T2 同じ接続語で始まりすぎ",
                           f"「{head}」で始まる文が{c}/{n}カット"
                           f"(上限{int(n * CONJ_MAX_RATIO)})。"
                           f"接続語を貼らず、前の文の名詞をもう一度言うか、文を続けること"))

    # T3 対比の直訳(not A but B)
    contrast = [i for i, s in enumerate(subs, 1)
                if re.search(r"じゃなく|ではなく|じゃなくて|ではなくて", s)]
    if len(contrast) > CONTRAST_MAX:
        issues.append(("(全体)", "T3 「〜じゃなく〜」が多い",
                       f"{len(contrast)}回(#{'・#'.join(map(str, contrast))})。上限{CONTRAST_MAX}回。"
                       f"not A but B の直訳。日本語は「Aのせいじゃない。Bのせいなの」と2文に切る"))

    # T4 「〜なの。」止め
    nano = [i for i, s in enumerate(subs, 1)
            if re.search(r"(な|た|る|い)の[。?？!！]?$", s.rstrip())]
    if len(nano) > n * NANO_MAX_RATIO:
        issues.append(("(全体)", "T4 「〜なの。」が多い",
                       f"{len(nano)}/{n}カット(上限{int(n * NANO_MAX_RATIO)})。"
                       f"言い切り(「〜だ」「〜する」「体言止め」)を混ぜること"))
    return issues


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    ex = load_exempt("teiyaku")
    total = 0
    for vdir in targets:
        vid = vdir.name.split("-")[0]
        if "*" in ex.get(vid, set()):
            print(f"[--] {vdir.name} (gate_exempt)")
            continue
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — 定訳・直訳調 {len(issues)}件")
            for where, kind, detail in issues:
                print(f"       {where:8} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"{total}件。**専門語は日本語で定着している呼び方を1回は言う。**")
        print("      一覧は production/teiyaku.txt。接続語を貼って繋ぐのは日本語ではない。")
        sys.exit(1)
    print("結果: 定訳・直訳調は基準内")


if __name__ == "__main__":
    main()
