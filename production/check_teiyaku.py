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
# **語別ではなく、接続語で始まるカットの総数**の上限(2026-09-07 日本語パネル5周目)。
# 「31カット中10カット(32%)が接続語始まり」は、語別の22%をどれも超えていないので
# T2 では止まらなかった。接続語を貼るのは check_flow を満たすいちばん安い形なので、
# 総量でも上限を置く(CLAUDE.md「接続語や指示語を貼る前に、名詞をもう一度言えないかを先に試す」)
CONJ_TOTAL_MAX_RATIO = 0.25
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
    #
    # 2026-09-08: ここは**言い換えが字幕に出ているとき**しか発火しなかった。
    # 定訳も言い換えも両方まるごと消した台本(概念ごと落とした版)は素通りする。
    # Z002 は「ストア派」「写本」「随筆」「政治顧問」がどれも言い換えごと消えていて [OK] だった。
    # plan.md の §1.7(学び)に太字で書いてある語は、**動画で言うと自分で決めた語**なので、
    # 消えていたら落とす。企画書に無い語は、これまでどおり言い換えがあるときだけ見る
    plan_words = set()
    pm = vdir / "plan.md"
    if pm.exists():
        import re as _re
        for m in _re.finditer(r"\*\*([^*]{2,20})\*\*", pm.read_text()):
            plan_words.add(m.group(1).strip("。、 "))
    for teiyaku, iikae, src in load_terms():
        bare = teiyaku.strip("『』")
        if bare in joined or teiyaku in joined:
            continue
        if bare in plan_words or teiyaku in plan_words:
            issues.append(("(全体)", "T1 企画書の語を言っていない",
                           f"plan.md が**{teiyaku}**と太字で書いているのに、"
                           f"ナレーションに1回も出てこない。**言うと決めた語を落とさない**。{src}"))
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

    # T2b 接続語の総量(語別ではなく、接続語で始まるカットの数)
    #     check_flow を「接続語を貼る」で満たすと、語別の上限は超えないまま
    #     全体の3分の1が接続語で始まる台本になる(2026-09-07 5周目で 10/31)
    ALL_HEADS = CONJ_HEADS + ("たとえば", "例えば", "実は", "さて", "ちなみに", "そしたら",
                              "だって", "なら", "そこで", "まず", "答えは", "つまり", "こう")
    tot = sum(1 for s in subs if s.startswith(ALL_HEADS))
    if tot > n * CONJ_TOTAL_MAX_RATIO:
        heads = [s[:4] for s in subs if s.startswith(ALL_HEADS)]
        issues.append(("(全体)", "T2b 接続語で始まるカットが多い",
                       f"{tot}/{n}カット({tot / n:.0%}、上限{CONJ_TOTAL_MAX_RATIO:.0%})が"
                       f"接続語で始まっている: {'・'.join(heads[:12])}。"
                       f"接続語を貼る前に、前の文の名詞をもう一度言えないかを先に試すこと"))

    # T3 対比の直訳(not A but B)
    # 2026-09-08: 「じゃなく|ではなく」しか見ておらず、**2文に切った形**
    # 「Aじゃない。B」を数えていなかった(パネルが地の文で3回・引用込み5回を検出)。
    # 切れば直訳でなくなるわけではないので、同じ対比として数える
    contrast = [i for i, s in enumerate(subs, 1)
                if re.search(r"じゃなく|ではなく|じゃなくて|ではなくて"
                             r"|じゃない[。、]|ではない[。、]|じゃないの[。、]", s)]
    if len(contrast) > CONTRAST_MAX:
        issues.append(("(全体)", "T3 「〜じゃなく〜」が多い",
                       f"{len(contrast)}回(#{'・#'.join(map(str, contrast))})。上限{CONTRAST_MAX}回。"
                       f"not A but B の直訳。日本語は「Aのせいじゃない。Bのせいなの」と2文に切る"))

    # T4 「〜なの。」止め
    # 2026-09-08: (な|た|る|い)の。 だと「返すの。」「書いてるの。」「すむの。」を
    # 数え落とし、14/37 を 11/37 と報告して黙って通していた。**かなの直前は問わない**
    nano = [i for i, s in enumerate(subs, 1)
            if re.search(r"[ぁ-んァ-ヴ一-龥]の[。?？!！]?$", s.rstrip())]
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
