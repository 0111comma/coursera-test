#!/usr/bin/env python3
"""固有名詞は、初出のその場で「何者か」を言う(2026-09-08)。

ユーザー指摘(原文・**毎度言われている**):

  「なんか毎度言ってる気がするんだけど、ショート動画は自分以外が作成したコンテンツが
    溢れかえってるフィードの中急に現れるから過去の文脈とか過去に話したことが
    相手に伝わるとか思わないで。」
  「ネロの話前したみたいなノリで話してるのはなぜ?」

**ショートは、知らない人のフィードに突然現れる。**視聴者はこのチャンネルを見たことがなく、
前の動画も、いま出した人名も知らない。それなのに Z002 は

    #14 セネカも、皇帝ネロの家庭教師だった人。
    #15 ネロが即位してからは、その右腕。

と、ネロの生涯を視聴者が知っている前提で話していた(しかも #14 で皇帝と呼んだ人の
即位を #15 で説明するので、順番としても壊れている)。

**なぜ既存のゲートが止めなかったか。**check_yougo は
「同じ語を3回以上出して意味を一度も言っていない」ときだけ落ちる。ネロは2回、
モンテーニュは2回なので素通りした。**回数ではなく、初出かどうかで見る。**

判定:
  1. 字幕から固有名詞を拾う(カタカナ3字以上 / 『』の書名 / 一覧の人名)
  2. その**初出のカット**に、何者かを言う語(人・皇帝・哲学者・作家 …)か、
     同格の形(「〜って人」「〜っていう」)があるか
  3. 無ければ落とす。**次のカットで説明しても遅い**(1カットは3秒で、
     知らない名前が出た時点で視聴者は考えるのをやめる)

免除: production/gate_exempt.txt に `<ID>:koyuu:<語>  # 理由`
"""
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))
from render_units import subtitles, UnreadableRender  # noqa: E402

# 何者かを言っている印。**初出のカットの中に1つは要る**
SETSUMEI = (
    "って人", "という人", "っていう人", "って名前", "人ね", "人なの", "人だよ",
    "皇帝", "王", "先生", "哲学者", "政治家", "作家", "詩人", "学者", "心理学者",
    "医者", "弟子", "師匠", "奴隷", "長官", "役人", "貴族", "商人", "軍人",
    "って本", "という本", "っていう本", "本ね", "本なの", "本だよ", "書いた", "書いてる",
    "生まれ", "育ち", "時代", "世紀", "年前", "年ごろ", "国", "都市", "町", "島",
    "修道院", "学校", "会社", "宗教", "教会", "の名前", "って呼ば", "と呼ば",
)
# 説明が要らない語(誰でも知っている地名・国名など)。**理由を書いて足す**
YASASHII = {
    "ローマ", "フランス", "イタリア", "ギリシャ", "ヨーロッパ", "アメリカ", "イギリス",
    "キリスト", "キリスト教", "スマホ", "カレンダー", "メモ", "ストイック",
    # 固有名詞ではない普通のカタカナ語
    "セリフ", "ノート", "クセ", "ページ", "テレビ", "ネット", "アプリ", "ミス",
}
# 書名(『』)は、本だと分かる語が同じカットにあればよい
SHOMEI_OK = ("本", "書", "記録", "読", "書い", "写", "章", "訳", "出版", "刊")

# ---- 経歴語(2026-09-08 ユーザー「ネロの話前したみたいなノリで話してるのはなぜ?」)
#
# **説明していない前後関係を持ち出さない。**Z002 は #14 で「皇帝ネロ」と名乗ってから
# #15 で「ネロが即位してからは」と言っていた。視聴者はネロの生涯を知らないので、
#   (1) 皇帝と呼んだ人の即位を後から説明する、という順番の壊れ
#   (2) その人の経歴を知っている前提
# が同時に起きる。**人物の変化は、その人を出すカットで1回で言い切る。**
KEIREKI = ("即位", "退位", "引退", "改宗", "亡命", "追放", "復帰", "失脚",
           "就任", "辞任", "解放", "処刑", "帰国", "召還", "左遷", "出家")
# **2字の名前も拾う。**「ネロ」を3字以上の条件で取りこぼしていた(2026-09-08)
KATAKANA = re.compile(r"[ァ-ヴー]{2,}")
SHOMEI = re.compile(r"『([^』]+)』")


def load_exempt(vid: str) -> set:
    f = ROOT / "production" / "gate_exempt.txt"
    out = set()
    if not f.exists():
        return out
    for ln in f.read_text().splitlines():
        body, _, reason = ln.partition("#")
        parts = body.strip().split(":")
        if len(parts) == 3 and parts[0] == vid and parts[1] == "koyuu" and reason.strip():
            out.add(parts[2])
    return out


def check_video(vdir: Path):
    rp = vdir / "render.py"
    if not rp.exists():
        return []
    try:
        subs = subtitles(rp)
    except UnreadableRender as e:
        return [("(全体)", "台本を読めない", str(e))]
    ex = load_exempt(vdir.name.split("-")[0])
    seen, issues = {}, []
    for i, s in enumerate(subs, 1):
        for w in set(KATAKANA.findall(s)) | set(SHOMEI.findall(s)):
            if w in YASASHII or w in ex or w in seen:
                continue
            seen[w] = i
            ok = any(k in s for k in SETSUMEI)
            if w in SHOMEI.findall(s):
                ok = ok or any(k in s for k in SHOMEI_OK)
            if not ok:
                issues.append((f"#{i}", w,
                               f"「{w}」が初めて出るカットに、何者かを言う語がない: 「{s}」"))
    # 2つめの判定: **後から経歴を持ち出していないか**
    for i, s in enumerate(subs, 1):
        kw = [k for k in KEIREKI if k in s]
        if not kw:
            continue
        for w, first in seen.items():
            if w in s and first < i and w not in ex:
                issues.append((f"#{i}", w,
                               f"「{w}」を #{first} で出したあと、#{i} で経歴「{kw[0]}」を"
                               f"持ち出している: 「{s}」。**視聴者はその人の生涯を知らない。**"
                               f"変化は、その人を出すカットで1回で言い切ること"))
    return issues


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — 説明のない固有名詞 {len(issues)}件")
            for where, w, detail in issues:
                print(f"       {where:6} {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"{total}件。**ショートは知らない人のフィードに突然現れる。**"
              f"固有名詞は初出のその場で何者かを言うこと(次のカットでは遅い)。")
        sys.exit(1)
    print("結果: 固有名詞はすべて初出で説明されている")


if __name__ == "__main__":
    main()
