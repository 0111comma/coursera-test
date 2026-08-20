#!/usr/bin/env python3
"""視聴維持の構造チェック(ループ71)。

ユーザー指示:「棒グラフの色を変えるとかまじでどうでもいい。
抜本的に視聴維持率を上げるための施策が必要」

実測のボトルネック(docs/research/hold-rate-2026-08.md):
  - Stayed to watch 28.9% — 7割が最初の1〜2秒で消える
  - 型が「冒頭のカバーで答えの数字を見せる」になっていて、
    フィードでは1フレーム目=本編なので、答えを先にネタバレしていた
  - 答えが動画の6割地点で出て、残り4割が補足と説教(離脱の尻尾)

判定(すべて不合格):
  H1 [ネタバレ] カバーの主役テキストに数字を出すなら「?」を含めること。
     答えの数字をマスクせず1フレーム目に置かない
  H2 [終盤の новое] 金額・歳・%の数字の「最後の初出」が全ユニットの60%以降にあること。
     前半で数字を出し切ると、後半に残る理由がなくなる
  H3 [ループ] 最終ユニットが冒頭の問いの内容語を1つ以上受けること。
     終わりが始まりに戻ると、2周目(視聴完了率100%超え)が出る

使い方:
    python3 production/check_hold.py                    # 全ショート
    python3 production/check_hold.py videos/S027-...    # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

# 判定対象の数字: 金額・歳・%(年号や時点表記は対象外)
MONEY = re.compile(r"[0-9][0-9,万億]*(?:円|歳|%)")
LATE = 0.60


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"h_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def content_words(text: str) -> set:
    words = set(re.findall(r"[一-龥]{2,}", text))
    words |= set(re.findall(r"[ァ-ヴー]{2,}", text))
    words |= set(re.findall(r"[0-9]+", text))
    return words


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists() or vdir.name.startswith("L"):
        return []
    src = render_py.read_text()
    units = getattr(_load(render_py), "UNITS", [])
    if not units:
        return []
    subs = [u.subtitle.replace("【", "").replace("】", "") for u in units]
    issues = []

    # H1: カバーに答えの数字を置かない(置くなら ? でマスク)
    m = re.search(r's[cl]\.cover\(\s*"[^"]*",\s*"([^"]*)"', src)
    if m:
        main = m.group(1)
        if re.search(r"[0-9]", main) and "?" not in main:
            issues.append(("cover", "ネタバレ",
                           f"1フレーム目の主役が答えの数字「{main}」。フィードでは"
                           f"1フレーム目=本編なので、数字は「?」でマスクすること"))

    # H2: 数字の最後の初出が60%以降
    seen, last_first = set(), 0
    for i, s in enumerate(subs):
        for n in MONEY.findall(s):
            if n not in seen:
                seen.add(n)
                last_first = i
    if seen and len(subs) > 1 and last_first / (len(subs) - 1) < LATE:
        issues.append((f"#{last_first + 1}", "数字が前半で出切っている",
                       f"最後の新しい数字が{last_first + 1}/{len(subs)}ユニット目"
                       f"({last_first / (len(subs) - 1):.0%})で出切る。"
                       f"答えの数字は{LATE:.0%}地点より後に置き、後半に残る理由を作ること"))

    # H3: 最終ユニットが冒頭の問いに戻る
    if len(subs) >= 2:
        if not (content_words(subs[0]) & content_words(subs[-1])):
            issues.append((f"#{len(subs)}", "ループしない締め",
                           f"最終文「{subs[-1]}」が冒頭の問い「{subs[0]}」の語を"
                           f"1つも受けていない。終わりを始まりに戻すこと"))
    return issues


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir()
        if (p / "render.py").exists() and p.name.startswith("S"))
    total = 0
    for vdir in targets:
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — {len(issues)}件")
            for where, kind, detail in issues:
                print(f"       {where:6} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}件。答えは引っ張り、終わりは始まりに戻すこと。")
        sys.exit(1)
    print("結果: 維持の構造は基準内")


if __name__ == "__main__":
    main()
