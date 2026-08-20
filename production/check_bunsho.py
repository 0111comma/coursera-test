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

# D1: 文頭の指示語。2つ続いたら落とす(ループ71でユーザー指摘により3→2)
SHIJI = ("その", "この", "それ", "これ")
SHIJI_RUN = 2

# D3〜D5(ループ71)。ユーザー指摘:
#   「そのっていうのが2回続いたり、だからっていうのが2回続いたり、
#     接続語が同じものが2回続くのは、喋り方としてバカっぽい」
#   「指示語を使いすぎかな。1分の動画で20回30回出てるのって普通に考えるとおかしい。
#     3から4回しか指示語を使わない縛りみたいなのもつけていい」
#
# なぜこうなったかの診断(言い訳なしの事実):
#   check_flow.py が「接続語を置くか、前の文に出た語を受けること」を要求する。
#   その要求を満たすいちばん安い形が「その〜」と「だから〜」だった。
#   **ゲートが欠陥を作った5回目**。だから数え上げのほうもゲートにする。
#   前の文を受けるなら、指示語ではなく**名詞をもう一度言う**のが正しい。
SHIJI_ANY = ("この", "その", "あの", "どの", "これ", "それ", "あれ", "どれ",
             "ここ", "そこ", "あそこ", "こう", "そう")
SHIJI_MAX = 4              # 1本で使ってよい指示語の総数
SETSUZOKU = ("だから", "そして", "でも", "しかも", "つまり", "では", "まず",
             "ただし", "すると", "ちなみに", "たとえば", "そこで", "しかし")
SETSUZOKU_MAX = 3          # 同じ接続語を1本で何回まで使ってよいか

# D7: ぼかし語(ループ71)。ユーザー指摘「ある名前が増えたって何?」
# 「ある◯◯」は名前を言えるのに勿体ぶる言い方で、聞き手を苛立たせるだけ。
# 名前があるなら最初から名乗る。
BOKASHI = re.compile(r"ある(名前|制度|もの|お金|仕組み|話|数字|言葉)")

# D6: 重言(同じ意味を2回言う)。ユーザー指摘「頭痛が痛いみたいな感じ」
JUGEN = (("お礼", "返礼品"), ("まず最初", ""), ("約", "ほど"), ("いま現在", ""),
         ("一番最初", ""), ("あとで後悔", ""), ("必ず必要", ""))

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


def tate(units):
    """台本を縦に並べて、指示語と接続語に印をつける。

    ユーザー指摘:「縦に書いてもらえるとわかると思うんだけど、
    そのっていうのが2回続いたり、だからっていうのが2回続いたり」
    目で見れば一発で分かるものを、目で見られる形で出す。
    """
    out = []
    for i, u in enumerate(units, 1):
        t = u.subtitle
        marks = [w for w in SHIJI_ANY if w in t]
        head = next((w for w in sorted(SETSUZOKU, key=len, reverse=True)
                     if t.startswith(w)), "")
        tag = ""
        if head:
            tag += f" [{head}]"
        if marks:
            tag += " [指示語:" + "".join(marks) + "]"
        out.append(f"  {i:2} {t}{tag}")
    return out


def check_video(vdir: Path):
    spec = importlib.util.spec_from_file_location(f"b_{vdir.name}", vdir / "render.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    units = mod.UNITS
    sents = sentences(units)
    bad, warn = [], []

    # 指示語・接続語の上限はショート(約17ユニット)で決めた**密度**の基準。
    # 横型の長尺(100ユニット超)に絶対数のまま当てると「1本で指示語4回」になり、
    # 日本語として不自然な縛りになる。CLAUDE.md「縦型と横型で基準が変わるものは
    # 形式を見て切り替える」に従い、長尺はユニット数に比例して上限を伸ばす。
    # 密度そのものはショートと同じ(緩めてはいない)
    src = (vdir / "render.py").read_text()
    scale = max(1, round(len(units) / 17)) if "use_landscape" in src else 1
    shiji_max = SHIJI_MAX * scale
    setsuzoku_max = SETSUZOKU_MAX * scale

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

    # D3: 指示語の総数
    subs = [u.subtitle for u in units]
    joined = "".join(subs)
    n_shiji = sum(joined.count(w) for w in SHIJI_ANY)
    if n_shiji > shiji_max:
        naka = [f"#{i}「{w}」" for i, t in enumerate(subs, 1)
                for w in SHIJI_ANY if w in t]
        bad.append(("(動画全体)", "指示語が多い",
                    f"{n_shiji}回。{shiji_max}回まで。"
                    f"前の文を受けるなら、指示語ではなく名詞をもう一度言うこと: "
                    f"{' '.join(naka[:10])}"))

    # D4: 同じ語で始まる文が2つ続く
    def head_of(t):
        for w in sorted(SETSUZOKU + SHIJI_ANY, key=len, reverse=True):
            if t.startswith(w):
                return w
        return None

    for i in range(1, len(subs)):
        a, b = head_of(subs[i - 1]), head_of(subs[i])
        if a and a == b:
            bad.append((f"#{i + 1}", "同じ出だしが連続",
                        f"「{a}」で始まる文が2つ続いている: "
                        f"「{subs[i - 1]}」/「{subs[i]}」"))

    # D5: 同じ接続語の使いすぎ
    for w in SETSUZOKU:
        n = sum(1 for t in subs if t.startswith(w))
        if n > setsuzoku_max:
            bad.append(("(動画全体)", "同じ接続語が多い",
                        f"「{w}」で始まる文が{n}個。{setsuzoku_max}個まで"))

    # D7: ぼかし語
    for i, t in enumerate(subs, 1):
        m = BOKASHI.search(t)
        if m:
            bad.append((f"#{i}", "ぼかし語",
                        f"「{m.group()}」— 名前があるなら最初から名乗ること: 「{t}」"))

    # D6: 重言
    for i, t in enumerate(subs, 1):
        for a, b in JUGEN:
            if b and a in t and b in t:
                bad.append((f"#{i}", "同じ意味を2回",
                            f"「{a}」と「{b}」は同じことを言っている: 「{t}」"))
            elif not b and a in t:
                bad.append((f"#{i}", "同じ意味を2回", f"「{a}」— 「{t}」"))

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
    if "--tate" in sys.argv:
        sys.argv.remove("--tate")
        for a in sys.argv[1:]:
            vdir = Path(a)
            spec = importlib.util.spec_from_file_location(f"t_{vdir.name}", vdir / "render.py")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            print(f"===== {vdir.name}(縦読み用。工程C: 音読して恥ずかしくないか)")
            for line in tate(mod.UNITS):
                print(line)
        return

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
