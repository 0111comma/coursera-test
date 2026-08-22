#!/usr/bin/env python3
"""説明していない専門語の自動検出(2026-08-22)。

**手で用語リストを持つ方式は、何度でも漏れる。**
ループ71でユーザーに叱られた「枠って一般的な用語じゃないだろ?省略してんじゃん。
なんでそういうのチェックできないかな」がまさにそれで、check_teinei の JARGON は
手書きの一覧なので、載せ忘れた語は黙って通る。

実際、2026-08-22 の調査で **L001(納品済み)に2件の見逃し**が見つかった:
  - 「課税口座」: ナレーション9回・画面込み23回。**一度も意味を言っていない**
    (この動画の中心概念。NISA口座との対比が主題なのに定義が無い)
  - 「相殺」   : ナレーション2回・画面込み8回。同上

そこで向きを逆にする。**一覧に無い語を落とす**のではなく、
**3回以上出る複合語のうち、意味を言っていないものを全部出す**。
「説明しなくてよい」と判断した語だけを yougo_easy.txt に理由つきで足していく。

意味を言っている、と見なす型:
    「Xとは〜」「Xという〜」「〜をXと呼ぶ」「その名前が、X」「Xは、〜のこと」
    「X(よみ)」  ※ 画面のカードで読みを添えるのも説明とみなす

使い方:
    python3 production/check_yougo.py                    # 全動画
    python3 production/check_yougo.py videos/L001-...    # 1本だけ
"""
import re
import sys
from collections import Counter
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
EASY_FILE = PRODUCTION / "yougo_easy.txt"
MIN_HITS = 3          # 何回以上出たら説明を要求するか

try:
    from janome.tokenizer import Tokenizer
except ImportError:
    print("[NG] janome が入っていません。`pip install janome` を実行してください。",
          file=sys.stderr)
    sys.exit(2)

_T = Tokenizer()


def load_easy():
    out = set()
    if EASY_FILE.exists():
        for ln in EASY_FILE.read_text().splitlines():
            ln = ln.split("#")[0].strip()
            out.update(w for w in ln.split() if w)
    return out


def compounds(text):
    """連続する名詞をつないで複合語にする(「厚生」「年金」→「厚生年金」)。"""
    runs, cur = [], []
    for t in _T.tokenize(text):
        pos = t.part_of_speech.split(",")
        if pos[0] == "名詞" and pos[1] not in ("数", "代名詞", "非自立", "接尾"):
            cur.append(t.surface)
        else:
            if cur:
                runs.append("".join(cur))
            cur = []
    if cur:
        runs.append("".join(cur))
    return [r for r in runs if len(r) >= 3 and re.fullmatch(r"[一-龥ァ-ヴー]+", r)]


def explained(text, w):
    pats = [rf"{re.escape(w)}とは", rf"{re.escape(w)}という",
            rf"を[、]?{re.escape(w)}と(呼ぶ|言う|いう)",
            rf"名前(が|は)[、]?{re.escape(w)}",
            # 「持つあいだ払う手数料が、信託報酬なのだ」型(定義を先に言って名前を後に置く)
            rf"が[、]?{re.escape(w)}(な|だ|です|とい)",
            # 「信託報酬は、管理や運用にかかる費用。」型
            rf"{re.escape(w)}は[、][^。]*(こと|費用|仕組み|お金|制度|手数料|税|割合)",
            rf"{re.escape(w)}[((]"]
    if any(re.search(p, text) for p in pats):
        return True
    # 「源泉徴収」の説明が「源泉徴収**あり**とは〜」の形で書かれていることがある。
    # 語で始まる長い形が説明されていれば、その語は説明済みとみなす
    for m in re.finditer(rf"{re.escape(w)}[ぁ-ん一-龥ァ-ヴ]{{1,4}}", text):
        if any(re.search(p.replace(re.escape(w), re.escape(m.group(0))), text)
               for p in pats):
            return True
    return False


def check_video(vdir: Path, easy):
    rp = vdir / "render.py"
    if not rp.exists():
        return []
    src = rp.read_text()
    subs = re.findall(r'Unit\(\s*"[^"]+",\s*"([^"]+)"', src)
    if not subs:
        return []
    # 視聴者が目にするのは字幕だけではない。図の中の文字も数える
    screen = " ".join(re.findall(r'"([^"]{2,30})"', src))
    text = "".join(subs) + " " + screen
    hits = Counter(w for w in compounds(text) if w not in easy)
    bad = [(w, n) for w, n in hits.items() if n >= MIN_HITS and not explained(text, w)]
    bad.sort(key=lambda x: -x[1])
    return bad


def main():
    easy = load_easy()
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        bad = check_video(vdir, easy)
        if bad:
            total += len(bad)
            print(f"[NG] {vdir.name} — {len(bad)}語")
            for w, n in bad:
                print(f"       「{w}」を{n}回出しているのに、意味を一度も言っていない")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}語。**その場で意味を言う**か、"
              f"説明が要らない語なら理由を添えて production/yougo_easy.txt に足すこと。")
        sys.exit(1)
    print("結果: 説明していない専門語なし")


if __name__ == "__main__":
    main()
