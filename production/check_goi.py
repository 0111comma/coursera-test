#!/usr/bin/env python3
"""語の省略と、意味を渡していない語の機械チェック(ループ71)。

ユーザー指摘:
  「そもそも枠ってなんだよ。この動画を見る人、枠って一般的な用語じゃないだろ?
    その、省略してんじゃん、枠っていう言葉自体が。
    なんでそういうのチェックできないかな、お前は。」

なぜ既存のチェックが素通りさせたかの診断(言い訳なしの事実):
  check_ryakugo.py の PAIRS は**手で書いた一覧**で、「投資枠→枠」を登録していなかった。
  check_teinei.py の JARGON も**手で書いた一覧**で、「枠」が入っていなかった。
  だから両方とも [OK] を出した。**登録し忘れた語は黙って通る**設計だった。

  ループ65で同じ構図を一度直している(文章のルール→機械チェック)。
  だが移した先が「禁止語の一覧」だったので、穴の形が変わっただけだった。

このチェックの設計 — **失敗の向きを逆にする**:
  禁止語を並べるのではなく、**許可語を並べる**(production/goi_futsu.txt)。
  一覧に無い語は落ちる。だから**登録し忘れは黙って通らず、うるさく落ちる**。
  誤検出は一覧に1行足せば消える。見逃しのほうが高くつく、という向きにした。

判定:
  同じ動画の中に長い語 T(例「投資枠」)があるのに、
  ナレーションでその一部 S(例「枠」)を**2回以上**単独で使っていて、
  S そのものの意味をどこでも言っていない → 落とす。
  S が普通語一覧にあれば見逃す。

  **2回以上**にしているのは、1回だけの「思った額に」のような使い方まで拾うと、
  1本あたり10件以上出て人の合否と合わなくなるため(ループ51の基準)。
  略語は癖として繰り返し出る。

やってみて分かった限界(確度A・実測):
  **公開済みの台本を「正しい例」として一覧を機械生成する案は使えなかった。**
  S003(公開済み)は「枠」を4回、意味を言わずに使っている。
  つまり**通った動画の中に同じ欠陥が入っている**ので、教師データにならない。
  一覧は手で作る。ただし向きは許可側なので、抜けは落ちて気づける。

  この判定は「長い語が同じ動画にある」ことが条件。
  長い語が一度も出てこない専門語(例: 動画の中で最初から最後まで「枠」しか
  言わない場合)は check_teinei.py の JARGON 側で受ける。

使い方:
    python3 production/check_goi.py                    # 全動画
    python3 production/check_goi.py videos/S016-...    # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

FUTSU_FILE = PRODUCTION / "goi_futsu.txt"
MIN_HITS = 2          # 単独使用が何回で「略している」とみなすか

GLOSS = "とは|のこと|と呼ぶ|と呼び|という|といい|といっ"

try:
    from janome.tokenizer import Tokenizer
except ImportError:                                   # 黙って通さない
    print("[NG] janome が入っていません。`pip install janome` を実行してください。\n"
          "     このチェックは形態素解析が無いと動きません(動詞の一部を"
          "名詞と取り違えるため)。", file=sys.stderr)
    sys.exit(2)

_T = Tokenizer()


def tokens(text: str):
    return [(t.surface, t.part_of_speech.split(",")[0],
             t.part_of_speech.split(",")[1]) for t in _T.tokenize(text)]


def noun_runs(text: str):
    """隣り合う名詞のかたまり(=複合語)を返す。「投資」+「枠」→「投資枠」。"""
    runs, cur = [], []
    for surf, pos, sub in tokens(text):
        if pos == "名詞" and sub not in ("数", "接尾", "非自立", "代名詞"):
            cur.append(surf)
        elif pos == "名詞" and sub == "接尾" and cur:
            cur.append(surf)
        else:
            if len(cur) >= 2:
                runs.append("".join(cur))
            cur = []
    if len(cur) >= 2:
        runs.append("".join(cur))
    return runs


def standalone_nouns(text: str):
    """複合語の一部ではない、単独の名詞を返す。"""
    ts = tokens(text)
    out = []
    for i, (surf, pos, sub) in enumerate(ts):
        if pos != "名詞" or sub in ("数", "非自立", "代名詞", "接尾"):
            continue
        prev_noun = i > 0 and ts[i - 1][1] == "名詞" and ts[i - 1][2] != "数"
        next_noun = i + 1 < len(ts) and ts[i + 1][1] == "名詞"
        if prev_noun or next_noun:
            continue                                  # 複合語の一部
        out.append(surf)
    return out


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"g_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def narration(vdir: Path):
    units = getattr(_load(vdir / "render.py"), "UNITS", [])
    return [u.subtitle.replace("【", "").replace("】", "") for u in units]


def screen_text(vdir: Path):
    """render.py の文字列リテラル = 画面に出る文字。"""
    src = (vdir / "render.py").read_text()
    src = re.sub(r'"""(.|\n)*?"""', "", src)          # docstring は画面ではない
    src = re.sub(r"(?m)^\s*#.*$", "", src)            # コメントも画面ではない
    return re.findall(r'"([^"\n]*)"', src)


def load_futsu():
    if not FUTSU_FILE.exists():
        return set()
    return {ln.split("#")[0].strip() for ln in FUTSU_FILE.read_text().splitlines()
            if ln.split("#")[0].strip()}


def glossed(word: str, texts):
    """その語**そのもの**に意味を渡しているか。

    直前が漢字・カタカナなら、意味を渡しているのは**より長い語**のほうである。
    「投資枠と呼ぶ」は「投資枠」の説明であって「枠」の説明ではない。
    ここを見落とすと、長い語を1回説明しただけで略語が通ってしまう。
    """
    pat = re.compile(r"(?<![一-龥ヶァ-ヴーA-Za-z])" + re.escape(word)
                     + r"(?:" + GLOSS + r")")
    return any(pat.search(t) for t in texts)


def check_video(vdir: Path, futsu):
    if not (vdir / "render.py").exists():
        return []
    subs = narration(vdir)
    texts = subs + screen_text(vdir)

    compounds = set()
    for t in texts:
        # 画面の文字は「①株」「(金利」のように記号が混じる。記号で切ってから見る
        for chunk in re.split(r"[^一-龥ヶァ-ヴーA-Za-z々0-9%]+", t):
            compounds.update(c for c in noun_runs(chunk)
                             if re.fullmatch(r"[一-龥ヶァ-ヴーA-Za-z々]{2,}", c))

    alone = {}                                  # 単独で使った名詞 -> [(番号, 字幕)]
    for i, s in enumerate(subs, 1):
        for w in standalone_nouns(s):
            alone.setdefault(w, []).append((i, s))

    issues = []
    for short, hits in sorted(alone.items()):
        if short in futsu or len(hits) < MIN_HITS:
            continue
        longer = sorted((c for c in compounds
                         if c != short and (c.startswith(short) or c.endswith(short))),
                        key=len)
        if not longer:
            continue
        if glossed(short, texts):
            continue
        n, line = hits[0]
        issues.append((f"#{n}", "略語",
                       f"「{longer[0]}」があるのに「{short}」だけで{len(hits)}回使っている: "
                       f"「{line}」。普通の語なら production/goi_futsu.txt に足すこと"))
    return sorted(set(issues))


def main():
    futsu = load_futsu()
    targets = [Path(a) for a in sys.argv[1:] if not a.startswith("-")] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        issues = check_video(vdir, futsu)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — {len(issues)}件")
            for where, kind, detail in issues:
                print(f"       {where:5} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}件。略さず呼び、初めて出す語はその場で意味を言うこと。")
        sys.exit(1)
    print("結果: 語の省略・未説明なし")


if __name__ == "__main__":
    main()
