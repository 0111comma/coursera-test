#!/usr/bin/env python3
"""学びのゲート(Z 番台。2026-09-05)。

ユーザー指摘(Z001): 「学びがほぼない。知識をさこの動画で分け与えてるんだよね?
  これば誰が言ったの? なぜこの本が残ってるの? 誰になぜ評価されているの? そう言う学びが一切ないんだけど?」

考え方だけ渡して、人名・書名・来歴を落とすと、自己啓発の雑学になる。
判定(Z 番台の plan.md と render.py に対して):
  1. plan.md に「## 1.7 学び」(見出しに「学び」)の節があり、表に「誰が言った」「なぜ残った」「誰がどう評価した」の3行がある
  2. 3行それぞれに URL(出典)がある
  3. 「誰が言った」の行の **太字の人名** が、ナレーション(UNITS の字幕)のどれかに出てくる
  4. 「なぜ残った」「誰がどう評価した」の行の太字の語のうち、少なくとも1つずつがナレーションに出てくる

免除: production/gate_exempt.txt に `<ID>:manabi:*  # 理由`
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ("誰が言った", "なぜ残った", "誰がどう評価した")


def _load_units(render_py: Path):
    sys.path.insert(0, str(ROOT / "production"))
    spec = importlib.util.spec_from_file_location(f"m_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return [u.subtitle.replace("【", "").replace("】", "") for u in getattr(mod, "UNITS", [])]


def load_exempt():
    f = ROOT / "production" / "gate_exempt.txt"
    out = set()
    if f.exists():
        for ln in f.read_text().splitlines():
            body, _, reason = ln.partition("#")
            parts = body.strip().split(":")
            if len(parts) == 3 and parts[1] == "manabi" and reason.strip():
                out.add(parts[0])
    return out


def check_video(vdir: Path):
    plan = vdir / "plan.md"
    issues = []
    if not plan.exists():
        return [("plan.md", "企画書が無い")]
    md = plan.read_text()
    m = re.search(r"^##[^\n]*学び[^\n]*\n(.*?)(?=^## )", md, re.S | re.M)
    if not m:
        return [("plan.md", "「## … 学び …」の節が無い。誰が言った・なぜ残った・誰がどう評価した、を表で書くこと")]
    body = m.group(1)
    rows = {}
    for q in QUESTIONS:
        r = re.search(rf"^\|\s*{q}\s*\|(.*?)\|(.*?)\|\s*$", body, re.M)
        if not r:
            issues.append(("plan.md", f"学びの表に「{q}」の行が無い"))
            continue
        rows[q] = (r.group(1), r.group(2))
        if "http" not in r.group(2):
            issues.append(("plan.md", f"「{q}」の行に出典の URL が無い"))
    narr = "".join(_load_units(vdir / "render.py"))
    for q, (ans, _src) in rows.items():
        bold = re.findall(r"\*\*(.+?)\*\*", ans)
        names = [b.strip("。、 ") for b in bold]
        if not names:
            issues.append(("plan.md", f"「{q}」の答えに太字の固有名(人名・書名)が無い"))
            continue
        if q == "誰が言った":
            if not any(n in narr for n in names):
                issues.append(("render.py", f"「誰が言った」の人名({'/'.join(names)})がナレーションに出てこない。"
                                            f"知識の動画は名前を言う"))
        elif not any(n in narr for n in names):
            issues.append(("render.py", f"「{q}」の答えの語({'/'.join(names)})が1つもナレーションに出てこない"))
    return issues


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    ex = load_exempt()
    total = 0
    for vdir in targets:
        vid = vdir.name.split("-")[0]
        if not vid.startswith("Z"):
            continue
        if vid in ex:
            print(f"[--] {vdir.name} (gate_exempt)")
            continue
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — 学び {len(issues)}件")
            for where, detail in issues:
                print(f"       {where:10} {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"{total}件。**知識の動画には「誰が言った・なぜ残った・誰がどう評価した」を入れる。**")
        sys.exit(1)
    print("結果: 学びの3問に答えている")


if __name__ == "__main__":
    main()
