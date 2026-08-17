#!/usr/bin/env python3
"""「誰の、どんな欲求に向けた動画か」の機械チェック(ループ67)。

ユーザー指摘:
  「なぜ損得の結論が大事かというと、人のどんな欲求に対してこの動画を
    向けているんですかっていう問いがあるんだよね。
    変動金利、固定金利だと、家を買いたい人向け。家を買いたいけど損はしたくないと
    思ってる人に向けた訴求動画を作るべきじゃん。それがこの構成では伝わらない。
    S12も、会社が出してるから何なの?っていう。ただの雑学ですか?っていう。
    会社が払ってくれてんだね、ありがとうで終わる動画をわざわざ見続けようと思わなくない?」

診断(既存作を並べて分かったこと):
  合格をいただいた本と、却下された本を分けているのは
  **視聴者の身に何が起きるか**が書いてあるかどうかだった。

    S014 手数料  → 平日の昼に下ろす / 月1回にまとめる / 無料回数を調べる  「流れとても良い」
    S015 住民税  → 収入がない年に請求が来る                          「良いね」
    S011 年金    → 自分が何歳まで生きるかで損得が決まる                  合格
    S012 社会保険 → **何も起きない**(会社の財布の話)                  「面白くない」×2
    S013 金利    → **何も起きない**(3.83%を出して終わり)              「意味わかんない」

  オチを鋭くしても、視聴者の身に何も起きないなら雑学のままである。
  S012 は「会社も同じ額を払っている」→「69%しか残らない」と2回作り直したが、
  どちらも会社の財布の話で、**直す方向がそもそも間違っていた**。

  だからこれは台本の書き方の問題ではなく、**企画の問題**である。
  155ユニット書いてから気づくのでは遅いので、plan.md の段階で止める。

判定(plan.md に対して):
  1. 「この人の欲求」— 何をしたい / したくないのか。トピック名ではなく欲求
  2. 「視聴後に決められること」— 見終わったあと何を決める・何をするのか
  3. 2 が**動作**であること。「知る」「分かる」「気づく」だけなら不合格。
     それは雑学の定義そのもの

  台本の終盤5ユニットは**表示するだけ**にする。
  ここを機械で合否にすると、S011 の「長生きしすぎた時の保険なのだ」のような
  「行動語は無いが視聴者の身に起きる話」を落としてしまう
  (人の合否と一致しない機械判定は入れない — ループ51の教訓)。

使い方:
    python3 production/check_yokkyu.py                    # 全動画
    python3 production/check_yokkyu.py videos/S013-...    # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

YOKKYU_HEAD = re.compile(r"\*\*?この人の欲求\*\*?|^#+\s*この人の欲求", re.M)
KETTEI_HEAD = re.compile(r"\*\*?視聴後に決められること\*\*?|^#+\s*視聴後に決められること", re.M)
# 長尺だけ: 尺の見込みを**企画の段階で**書かせる(ループ70 フェーズ1)。
# check_video に「8分以上」を不合格条件で置いていたら、8分に届かせるために
# 内容を足した(L002は66ユニットで書き終えたあと尺のために+89ユニット足した)。
# 尺は書き上がってから測るものではなく、**企画のときに見込むもの**である。
SHAKU_HEAD = re.compile(r"\*\*?尺の見込み\*\*?|^#+\s*尺の見込み", re.M)

# 「決めること」に入っていなければならない動作。視聴者が手足を動かすか、選ぶか。
ACTIONS = (
    "決め", "選ぶ", "選べ", "変え", "やめ", "止め", "確かめ", "調べ", "そなえ", "備え",
    "残しておく", "寄せ", "まとめ", "申告", "見直", "比べて選", "avoid", "外す",
    "先に", "取っておく", "使う", "使わない", "borrow", "借りる", "借り換え", "続ける",
    "始める", "減らす", "増やす", "分ける", "置いておく", "計算する", "出す",
)
# これだけで終わっていたら雑学。ユーザーの言う「へえ、で終わる動画」
KNOW_ONLY = ("知る", "分かる", "わかる", "気づく", "理解", "納得", "へえ")

# 欲求は**視聴者の側の言葉**で書く。「〜について知りたい」は主題であって欲求ではない。
# これを課さないと「社会保険料の仕組みを知りたい」のような、
# トピック名を言い換えただけの行が通ってしまう(それが旧S012だった)。
WANT_MARKERS = (
    "したい", "たい。", "たい,", "たくない", "しくない", "嫌", "いやだ",
    "不安", "困", "迷", "心配", "怖", "避け", "減らし", "増やし", "守り",
    "損はしたく", "無駄にしたく", "間違えたく", "取られたく",
)


def _load_units(vdir: Path):
    rp = vdir / "render.py"
    if not rp.exists():
        return []
    spec = importlib.util.spec_from_file_location(f"y_{vdir.name}", rp)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return []
    return [u.subtitle.replace("【", "").replace("】", "") for u in getattr(mod, "UNITS", [])]


def _line_after(text: str, pattern: re.Pattern) -> str:
    m = pattern.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    # 見出しの行に続けて書いてあればそれを、無ければ**最初の空でない行**を取る
    for line in rest.split("\n"):
        line = line.lstrip(":: ").strip()
        if line:
            return line
    return ""


# 公開済みの本は作り直せない(過去の記録とズレる)。
# 判定は出すが、**この一覧の走行そのものは落とさない**。
# 落とすべきは「これから作る本」であって、済んだ本を赤いままにしても直せない。
# 新しく公開したらここに足すこと(CLAUDE.md のID方針と揃える)。
PUBLISHED = {f"S{n:03d}" for n in range(1, 12)}      # 2026-08-16時点で S001〜S011


def is_published(vdir: Path) -> bool:
    return vdir.name.split("-")[0] in PUBLISHED


def check_video(vdir: Path):
    plan = vdir / "plan.md"
    if not plan.exists():
        return [("plan.md", "企画書が無い", "欲求から立てた企画書なしに台本を書かない")]
    text = plan.read_text()
    issues = []

    yokkyu = _line_after(text, YOKKYU_HEAD)
    if not yokkyu:
        issues.append(("plan.md", "欲求が無い",
                       "「**この人の欲求**」を1行書くこと。"
                       "トピック名(住宅ローン・社会保険料)ではなく、"
                       "その人が何をしたい/したくないのかを書く"))
    elif not any(w in yokkyu for w in WANT_MARKERS):
        issues.append(("plan.md", "欲求が主題になっている",
                       f"「{yokkyu[:40]}」は主題であって欲求ではない。"
                       "「〜したい」「〜したくない」の形で、"
                       "視聴者の側の言葉で書くこと(docs/research/yokkyu-map.md §4)"))

    # 横型(長尺)だけ、尺の見込みを要求する
    if (vdir / "render.py").exists() and "use_landscape" in (vdir / "render.py").read_text():
        if not _line_after(text, SHAKU_HEAD):
            issues.append(("plan.md", "尺の見込みが無い",
                           "長尺は「**尺の見込み**」を1行書くこと。"
                           "この問いに何分ぶんの中身があるのかを、企画の段階で見込む。"
                           "書き上がってから尺のために内容を足すのは逆(01-length.md)"))

    kettei = _line_after(text, KETTEI_HEAD)
    if not kettei:
        issues.append(("plan.md", "決めることが無い",
                       "「**視聴後に決められること**」を1行書くこと。"
                       "ここが書けないなら、その企画は雑学である"))
    else:
        if not any(a in kettei for a in ACTIONS):
            only = [k for k in KNOW_ONLY if k in kettei]
            issues.append(("plan.md", "決めることが動作でない",
                           f"「{kettei[:40]}」には動作がない"
                           + (f"({only[0]}だけで終わっている)" if only else "")
                           + "。見た人が何を決める・何をするのかを書くこと"))
    return issues


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        issues = check_video(vdir)
        if issues:
            pub = is_published(vdir)
            if not pub:
                total += len(issues)
            print(f"[{'記録' if pub else 'NG'}] {vdir.name} — {len(issues)}件"
                  + ("(公開済みなので作り直さない。次に同じ型を作らないための記録)"
                     if pub else ""))
            for where, kind, detail in issues:
                print(f"       {where:9} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
        units = _load_units(vdir)
        if units:
            print(f"       (終盤3ユニット — 視聴者の身に何が起きるか、目で見ること)")
            for s in units[-3:]:
                print(f"         · {s}")
    print()
    if total:
        print(f"結果: {total}件。企画の段階で止めること。"
              f"155ユニット書いてから気づくのは高くつく。")
        sys.exit(1)
    print("結果: すべての企画に、欲求と決めることがある")


if __name__ == "__main__":
    main()
