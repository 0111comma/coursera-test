#!/usr/bin/env python3
"""日本語の文章としての作り方をチェックする(ループ71)。

ユーザー指示:
  「もうちょっとプロットの書き方について調べたほうがいいよ。日本語の文章の書き方」

なぜ必要か:
  これまでのゲートは9つあるが、すべて**内容**を見ている
  (話題があるか / つながっているか / 図があるか / 略していないか / 欲求があるか)。
  **日本語の文としてどう組んであるか**を見るものが1つも無かった。
  L001 を測ったら、読点の78%が主題の直後に打たれていて、
  本多勝一『日本語の作文技術』の読点2原則(修飾の境界 / 逆順)のどちらでもなかった。

判定(不合格):
  D1 同じ指示語で始まる文が3つ以上続く
     L001 #32〜#35 が「その」で4連続。S012(合格)とL002は最長2なので、3を境にする
  D2 なくても済む言葉(木下是雄)。「ということ」「を行う」「することができる」ほか

判定(注意。落とさない):
  W1 読点が主題・主語の直後にばかり打たれている(7割超)。
     本多勝一の第一原則は「長い修飾語が2つ以上あるとき、その境界に打つ」であり、
     主語の直後に機械的に打つことは原則に入っていない。
     ただし**これが人の合否を分けたという証拠は無い**(L001 78% / S012 50%)ので、
     落とさずに数だけ出す(ループ51の約束)
  W2 受動態が2割を超える(木下「受動態ではなく能動態で書く」)

使い方:
    python3 production/check_bunsho.py                 # 全動画
    python3 production/check_bunsho.py videos/L001-... # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

# D1: 文頭の指示語。3つ以上続いたら落とす
SHIJI = ("その", "この", "それ", "これ")
SHIJI_RUN = 3

# D2: 木下是雄「なくても済む言葉は一つも書かない」に当たる言い方
# 「のほう」は入れない。「小さいほう」「固定金利のほうが」は比較として要る語で、
# 冗長ではない。試しに入れたら L002 の正しい比較4件を落としたので外した。
MUDA = ("ということ", "という形", "を行う", "を行い", "することができ", "することが可能",
        "における", "に関しまして", "につきまして", "のような形", "かと思いま",
        "していただく", "せていただく")

# W1/W2 の閾値
TOUTEN_WARN = 0.70
UKEMI_WARN = 0.20

TOPIC_END = re.compile(r"(とは|では|なら|には|からは|は|が|も)$")
UKEMI = re.compile(r"(られる|られた|られて|れている|されて|される|された)")


def sentences(units):
    out = []
    for i, u in enumerate(units):
        for s in re.split(r"。", u.narration or u.subtitle):
            s = s.strip()
            if s:
                out.append((i, s))
    return out


def check_video(vdir: Path):
    spec = importlib.util.spec_from_file_location(f"b_{vdir.name}", vdir / "render.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    units = mod.UNITS
    sents = sentences(units)
    bad, warn = [], []

    # D1: 同じ指示語で始まる文が3つ以上続く
    run_word, run = None, []
    for i, s in enumerate(units):
        head = next((k for k in SHIJI if s.subtitle.startswith(k)), None)
        if head and head == run_word:
            run.append(i)
        else:
            if run_word and len(run) >= SHIJI_RUN:
                bad.append((f"#{run[0]}", "指示語の連続",
                            f"「{run_word}」で始まる文が{len(run)}連続 "
                            f"(#{run[0]}〜#{run[-1]})"))
            run_word, run = head, ([i] if head else [])
    if run_word and len(run) >= SHIJI_RUN:
        bad.append((f"#{run[0]}", "指示語の連続",
                    f"「{run_word}」で始まる文が{len(run)}連続 (#{run[0]}〜#{run[-1]})"))

    # D2: なくても済む言葉
    for i, s in sents:
        for w in MUDA:
            if w in s:
                bad.append((f"#{i}", "余分な語", f"「{w}」— {s}"))

    # W1: 読点の位置
    with_comma = [s for _, s in sents if "、" in s]
    if with_comma:
        topic = sum(1 for s in with_comma if TOPIC_END.search(s.split("、")[0]))
        ratio = topic / len(with_comma)
        if ratio > TOUTEN_WARN:
            warn.append(("読点の位置",
                         f"読点のある{len(with_comma)}文のうち{topic}文({ratio:.0%})が"
                         f"主題・主語の直後。読点は修飾の境界に打つ(本多勝一 第一原則)"))

    # W2: 受動態
    if sents:
        pas = sum(1 for _, s in sents if UKEMI.search(s))
        if pas / len(sents) > UKEMI_WARN:
            warn.append(("受動が多い",
                         f"{pas}/{len(sents)}文({pas / len(sents):.0%})が受動の形。"
                         f"能動で書く(木下是雄)"))

    return sorted(set(bad)), warn


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        bad, warn = check_video(vdir)
        total += len(bad)
        if bad:
            print(f"[NG] {vdir.name} — {len(bad)}件")
            for where, kind, detail in bad:
                print(f"       {where:6} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
        for kind, detail in warn:
            print(f"       WARN   [{kind}] {detail}")
    print()
    if total:
        print(f"結果: {total}件。日本語の文として組み直すこと。")
        sys.exit(1)
    print("結果: 文章の作りは基準内(WARNは落とさない)")


if __name__ == "__main__":
    main()
