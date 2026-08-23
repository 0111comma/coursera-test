#!/usr/bin/env python3
"""前提と根拠のチェック — **説明していない数字を画面に出さない**(2026-08-23)。

ユーザー指摘:
  「65歳から始めて? なんで? 65歳からきりくじしたら81歳でそこを尽きるんだよね?
    言葉が足りなさすぎる。ちゃんと説明しよう!
    なんで95歳までを想定してるのかな? 平均の寿命だから? ちゃんと論理的に説明しよう!
    そもそものプロット計画の時点で何を誰にどの欲望に向けて伝えたいのかが
    設計されてないからカスみたいなプロットができるのでは?
    誰がどうみても何を言っているのか、何を伝えたいのかわかる文章を書こう!
    それがまず直す第一優先で絶対今後落としてほしくないゲートです!」

なぜ14本のゲートが素通りさせたか(言い訳なしの事実):
  どのゲートも「文の作り」「語の省略」「重なり」を見ていて、
  **その数字がどこから来たのか**を一度も見ていなかった。
  S032 は 65歳・95歳・3%・5% を理由なしで出し、それでも14本すべて合格した。

このチェックの設計:
  動画に出る数値を2種類に分ける。

    導出値 — verify.py が計算して出している値。台本の中で導出を見せればよい
    前提値 — 計算の入力。**なぜその数なのかは、外から持ってくるしかない**

  前提値には、企画書 plan.md の「## 前提と根拠」表に
  **根拠と出典(URL + 確認日)**があること。
  そのうえで、**その根拠がナレーションでも言われている**こと。
  表に書いてあっても、動画の中で言わなければ視聴者には届かない。

  どちらにも属さない数値は落とす(= 出どころ不明の数字)。

判定(すべて不合格):
  1. plan.md に「## 前提と根拠」の表がない
  2. 表の行に根拠か出典(URL)か確認日が欠けている
  3. 表の値が、ナレーションで根拠とともに語られていない
  4. ナレーションの数値が、表にも verify.py の出力にも無い

免除: production/gate_exempt.txt に `動画ID:zentei:ユニット番号  # 理由`
      (理由の無い行は無効)
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "production"))

SECTION = "## 前提と根拠"

# --- 数値の取り出しと正規化 ---------------------------------------------
# 台本の「1000万円」と verify.py の「10,000,000円」は同じ数。
# **同じ物差しに寄せてから**突き合わせないと、導出値まで「出どころ不明」に出る。
RATIO = re.compile(r"[0-9]+人に[0-9]+人")                  # 4人に1人
SPAN = re.compile(r"[0-9]+(?:歳|年)[0-9]+か月")            # 81歳8か月 / 16年8か月
MONEY = re.compile(r"[0-9][0-9,]*(?:億[0-9]*)?(?:万[0-9]*)?円")
COUNT = re.compile(r"[0-9][0-9,]*(?:億|万)?(?:歳|%|年|か月|ヶ月|人|倍|回)")
# 「1年でふえる割合」のような**言い方**の中の1は、根拠の要る数ではない
TRIVIAL_UNITS = ("年", "か月", "ヶ月", "人", "回")
# 根拠の突き合わせから外す語(意味を持たない一般語)
STOP = {"こと", "もの", "ため", "場合", "とき", "など", "ここ", "それ"}


def _yen(tok: str) -> int:
    t = tok.replace(",", "").rstrip("円")
    n = 0
    for unit, mul in (("億", 100_000_000), ("万", 10_000)):
        if unit in t:
            a, t = t.split(unit, 1)
            n += int(a or 1) * mul
    return n + (int(t) if t else 0)


def numbers_in(text: str) -> set[str]:
    """文字列から数値を拾い、**正規化した鍵**にして返す。"""
    out, rest = set(), text
    for pat, kind in ((RATIO, "ratio"), (SPAN, "span"), (MONEY, "yen"), (COUNT, "count")):
        for m in pat.finditer(rest):
            t = m.group(0)
            if kind in ("ratio", "span"):
                out.add(t)
            elif kind == "yen":
                out.add(f"¥{_yen(t)}")
            else:
                unit = re.sub(r"[0-9,億万]", "", t)
                num = t[:len(t) - len(unit)].replace(",", "")
                v = _yen(num + "円") if ("万" in num or "億" in num) else int(num)
                if v == 1 and unit in TRIVIAL_UNITS:
                    continue
                out.add(f"{v}{unit}")
        rest = pat.sub(" ", rest)      # 先に取った表現は、あとの型で二重に拾わない
    return out


def load_exempt(gate: str):
    f = ROOT / "production" / "gate_exempt.txt"
    out = {}
    if not f.exists():
        return out
    for ln in f.read_text().splitlines():
        body, _, reason = ln.partition("#")
        body = body.strip()
        if not body or not reason.strip():
            continue
        parts = body.split(":")
        if len(parts) != 3 or parts[1] != gate:
            continue
        try:
            out.setdefault(parts[0], set()).add(int(parts[2]))
        except ValueError:
            continue
    return out


def narration(vdir: Path) -> list[str]:
    src = (vdir / "render.py").read_text()
    return [u.replace("【", "").replace("】", "")
            for u in re.findall(r'Unit\(\s*"[^"]+",\s*"([^"]+)"', src)]


def screen_numbers(vdir: Path) -> set[str]:
    """render.py の中の**画面に出す文字列**から数値を拾う(図のラベル・表のセル)。"""
    src = (vdir / "render.py").read_text()
    src = re.sub(r'Unit\(\s*"[^"]+",\s*"[^"]+"', "", src)   # 字幕は除く
    out = set()
    for s in re.findall(r'"([^"]*)"', src):
        out |= numbers_in(s)
    return out


def verify_numbers(vdir: Path) -> set[str]:
    """verify.py を実行し、**その出力に出てくる値**を導出値として集める。
    計算で出したのだから、台本では導出を見せればよく、外部の根拠は要らない。"""
    f = vdir / "verify.py"
    if not f.exists():
        return set()
    try:
        r = subprocess.run([sys.executable, str(f.resolve())], capture_output=True,
                           text=True, timeout=120, cwd=str(vdir.resolve()))
    except Exception:
        return set()
    return numbers_in(r.stdout)


def parse_zentei(pmd: str):
    """plan.md の「## 前提と根拠」表を読む。返り値: [(値, 根拠, 出典), ...]"""
    m = re.search(r"^##\s*[0-9.]*\s*前提と根拠.*$", pmd, re.M)
    if not m:
        return None
    body = pmd[m.end():].split("\n## ", 1)[0]
    rows = []
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln.startswith("|") or set(ln) <= set("|- :"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("値", ""):
            continue
        rows.append(tuple(cells[:3]))
    return rows


def words_of(s: str) -> set[str]:
    """根拠の文から、突き合わせに使う語(漢字2字以上/カタカナ2字以上/数値)を取る。"""
    out = set(re.findall(r"[一-龥々]{2,}|[ァ-ヴー]{2,}", s))
    out |= numbers_in(s)
    return {w for w in out if w not in STOP}


def check_video(vdir: Path):
    if not (vdir / "render.py").exists():
        return []
    pp = vdir / "plan.md"
    pmd = pp.read_text() if pp.exists() else ""
    issues = []

    rows = parse_zentei(pmd)
    if rows is None:
        return [("plan.md", "前提表がない",
                 f"企画書に「{SECTION}」の表がない。**計算の入力になる数値は、"
                 "なぜその数かを根拠と出典つきで先に決めること**")]
    if not rows:
        return [("plan.md", "前提表が空", f"「{SECTION}」に行がない")]

    subs = narration(vdir)
    joined = "".join(subs)
    ex = load_exempt("zentei").get(vdir.name.split("-")[0], set())

    # 1. 表の行が形として揃っているか
    for val, riyu, src in rows:
        if not riyu:
            issues.append((f"表:{val}", "根拠なし", "なぜその数なのかが空"))
        low = src.replace(" ", "")
        is_katei = "仮定" in src or "仮定" in riyu
        if not is_katei and "http" not in low:
            issues.append((f"表:{val}", "出典なし",
                           "官公庁の一次資料のURLを書くこと(仮定なら「仮定」と書く)"))
        if not is_katei and not re.search(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}|確認", src):
            issues.append((f"表:{val}", "確認日なし", "いつ確認した数字かを書くこと"))

    # 2. 表の値が、ナレーションで**根拠とともに**語られているか
    for val, riyu, src in rows:
        num = next(iter(sorted(numbers_in(val), key=len, reverse=True)), val)
        hit = [i for i, s in enumerate(subs, 1) if num in s]
        if not hit:
            continue           # 台本で使っていない前提は、そもそも問題ない
        if hit[0] in ex:
            continue
        keys = words_of(riyu)
        # 根拠の語が、その値を言っている文か、その前後1文に出ていること
        ok = False
        for i in hit:
            window = "".join(subs[max(0, i - 2):min(len(subs), i + 1)])
            if any(k in window for k in keys):
                ok = True
                break
        if not ok:
            issues.append((f"#{hit[0]}", "根拠を言っていない",
                           f"「{num}」を使っているのに、なぜ{num}なのかを言っていない。"
                           f"企画書の根拠「{riyu[:28]}」を、その場で一言で言うこと"))

    # 3. ナレーションの数値が、前提表にも verify.py にも無い
    derived = verify_numbers(vdir)
    known = set()
    for val, riyu, _ in rows:
        known |= numbers_in(val) | numbers_in(riyu)   # 根拠の欄の数も同じ出典で裏づけ済み
    for i, s in enumerate(subs, 1):
        if i in ex:
            continue
        for n in sorted(numbers_in(s)):
            if n in known or n in derived:
                continue
            issues.append((f"#{i}", "出どころ不明",
                           f"「{n}」が企画書の前提表にも verify.py の出力にもない: 「{s}」"))
    return sorted(set(issues))


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — {len(issues)}件")
            for where, kind, detail in issues:
                print(f"       {where:8} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}件。**説明していない数字を画面に出さないこと。**")
        print("      前提は plan.md の「## 前提と根拠」に根拠と出典を書き、")
        print("      台本ではその根拠を一言で言ってから数字を出すこと。")
        sys.exit(1)
    print("結果: 前提はすべて根拠つきで語られている")


if __name__ == "__main__":
    main()
