#!/usr/bin/env python3
"""ユーザーの指摘が未対応のまま焼こうとしていないかを見るゲート(2026-09-07)。

ユーザー指摘:

> と言うか言われたことをただ直してるよね? ちゃんと俺からの指摘も貯めてね。

サブエージェントの指摘は nihongo-stock / shiteki-stock に貯めてゲートで守って
いたのに、**ユーザー本人の指摘だけ、その場で直して終わりにしていた。**
いちばん重い指摘が記録に残らないので、次の動画で同じことをやる。

判定:
  docs/research/user-shiteki-stock.md の行のうち、
  その動画(または「全体」)に向いた行が「未対応」なら落とす。

**この一覧に「抽象化したルール」が空の行があるときも落とす。**
その1本を直しただけで終わらせない、というのがこのストックの目的なので、
ルール欄が空なら、指摘はまだ貯まっていない。

使い方:
    python3 production/check_user.py                    # 全動画
    python3 production/check_user.py videos/Z001-...    # 1本だけ
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STOCK = ROOT / "docs/research/user-shiteki-stock.md"

ROW_RE = re.compile(r"^\|\s*(U\d+)\s*\|")


def rows():
    """(ID, 動画, 原文, ルール, 状態) を返す。"""
    if not STOCK.exists():
        return []
    out = []
    for line in STOCK.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        c = [x.strip() for x in line.split("|")]
        # '' ID 日付 動画 原文 ルール 反映先 状態 ''
        if len(c) < 9:
            continue
        out.append((c[1], c[3], c[4], c[5], c[7]))
    return out


def main(video_dir: Path) -> int:
    vid = video_dir.name.split("-")[0]
    bad = []
    for tid, target, genbun, rule, status in rows():
        if target not in (vid, "全体"):
            continue
        if status.startswith("未対応"):
            bad.append((tid, "未対応", genbun))
        elif not rule:
            bad.append((tid, "ルールが空", genbun))
    if not bad:
        print(f"[OK] {video_dir.name}")
        return 0
    print(f"[NG] {video_dir.name} — ユーザー指摘 {len(bad)}件")
    for tid, why, genbun in bad:
        print(f"       {tid}  [{why}] {genbun[:60]}")
    return len(bad)


if __name__ == "__main__":
    targets = ([Path(a) for a in sys.argv[1:]]
               if len(sys.argv) > 1
               else sorted(p for p in (ROOT / "videos").iterdir()
                           if p.is_dir() and not p.name.startswith("_")))
    n = sum(main(t) for t in targets)
    print()
    if n:
        print(f"結果: {n}件。**ユーザーの指摘を残したまま焼かない。**"
              f"docs/research/user-shiteki-stock.md を見て、直すか、見送る理由を書くこと。")
    else:
        print("結果: 未対応のユーザー指摘なし")
    sys.exit(0)
