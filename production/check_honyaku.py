#!/usr/bin/env python3
"""AIの翻訳調を落とす機械ゲート(2026-09-04)。

ユーザー指摘(2026-09-03): 「英語の翻訳すぎるので日本語が不自然です」
→ 調査結果は docs/research/ai-nihongo-rules.md(症状 T1〜T10 と §3)。
そのうち**機械で見える形だけ**をここで落とす。文脈が要るもの(T1 無生物主語・
T3 動作主の消失・T7 抽象名詞)は人が見る(同文書 §4 の審査4体)。

ユーザーの方針(2026-08-29): 「一度指摘されたものは他の動画でも適応できるように
抽象化などしてルール化して」——サブエージェントを毎回4体回すのではなく、
一度出た指摘はここで止める。

見るもの(いずれも render.py の UNITS = 読み上げる字幕):
  T4   冗長な述部: 「することができ」「において」「に関して」「というもの」「を行う」
  T6   「〜的に」「〜性」(重要性・必要性・可能性 など)「〜化する」
  T8   読点が3つ以上の1文(耳で追えない)
  T9   定型句: 「まさに」「と言えるでしょう」「ではないでしょうか」「劇的」「非常に」
       「ぜひ」「が重要です」「が大切です」「素晴らしい」
  T10  体言止め(述語の無い文)が3カット連続
  §3-1 「〜のだ/なのだ」が全カットの 1/3 を超える(ずんだもんの語尾は3カットに1回まで)
  §3-2 述語の無い名詞に「なのだ」を付けている(「明日の一文なのだ」の型)
  T5   「あなた」が全カットの 1/4 を超える(二人称の入れすぎ)

使い方:
  python3 production/check_honyaku.py videos/Z001-joushi-kigen
  引数なしで videos/ 全部。誤検出は production/gate_exempt.txt に
  「<ID>:honyaku:<ユニット番号|*>  # 理由」で外す(理由の無い行は無効)。
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCTION = ROOT / "production"
sys.path.insert(0, str(PRODUCTION))

try:
    from janome.tokenizer import Tokenizer
except ImportError:
    print("[NG] janome が入っていません。`pip install janome` を実行してください。",
          file=sys.stderr)
    sys.exit(2)

_T = Tokenizer()

# ---- T4 冗長な述部
T4 = ["ことができ", "ことが可能", "において", "に関して", "というもの",
      "を行う", "を行い", "を行っ", "に対して", "における"]
# ---- T6 「〜的」「〜性」「〜化」
T6 = re.compile(r"[一-龥]{1,3}的に|[一-龥]{1,3}的な|重要性|必要性|可能性|効率性|生産性|"
                r"[一-龥]{1,3}化する|[一-龥]{1,3}化し")
# ---- T9 定型句(AIが書いた合図として読まれる語)
T9 = ["まさに", "と言えるでしょう", "といえるでしょう", "ではないでしょうか", "劇的",
      "革命的", "非常に", "ぜひ", "が重要です", "が大切です", "素晴らしい", "極めて",
      "言うまでもなく", "注目すべき", "興味深い"]
# ---- しきい値
NODA_MAX_RATIO = 1 / 3       # §3-1
ANATA_MAX_RATIO = 1 / 4      # T5
TAIGEN_RUN = 3               # T10 体言止めの連続
TOUTEN_MAX = 2               # T8 読点の上限(3つ以上で落とす)

PREDICATE_TAILS = ("だ", "る", "う", "い", "た", "ない", "ね", "よ", "か", "?", "？",
                   "!", "！", "のだ", "て", "で", "ろ", "え", "せ", "な", "ぞ", "さ")


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"h_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_exempt(gate: str):
    f = PRODUCTION / "gate_exempt.txt"
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
        if parts[2].strip() == "*":
            out.setdefault(parts[0], set()).add("*")
            continue
        try:
            out.setdefault(parts[0], set()).add(int(parts[2]))
        except ValueError:
            continue
    return out


def _strip(sub: str) -> str:
    return sub.replace("【", "").replace("】", "").strip()


def _last_token(text: str):
    toks = [t for t in _T.tokenize(text) if t.surface.strip()]
    return toks[-1] if toks else None


def is_taigen(text: str) -> bool:
    """体言止めか。末尾の記号を除いた最後の語が名詞で、問いでもない。"""
    core = text.rstrip("。.、,!！")
    if not core or core.endswith(("?", "？")):
        return False
    if core.endswith(PREDICATE_TAILS):
        return False
    tok = _last_token(core)
    return bool(tok) and tok.part_of_speech.startswith("名詞")


def noun_before_noda(text: str) -> bool:
    """「〜なのだ」の直前が名詞か(述語の無い文に語尾だけ付けている)。"""
    core = text.rstrip("。.!！")
    if not core.endswith("なのだ"):
        return False
    before = core[:-3]
    tok = _last_token(before)
    return bool(tok) and tok.part_of_speech.startswith("名詞")


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    units = getattr(_load(render_py), "UNITS", [])
    subs = [_strip(u.subtitle) for u in units]
    n = len(subs)
    if not n:
        return []
    issues = []          # (unit_no or 0, kind, detail)

    for i, s in enumerate(subs, 1):
        for w in T4:
            if w in s:
                issues.append((i, "T4 冗長な述部", f"「{w}」: {s}。動詞で言い切る"))
        m = T6.search(s)
        if m:
            issues.append((i, "T6 〜的/〜性/〜化", f"「{m.group(0)}」: {s}。和語に言い換える"))
        for w in T9:
            if w in s:
                issues.append((i, "T9 定型句", f"「{w}」: {s}。AIが書いた合図になる語。削る"))
        if s.count("、") > TOUTEN_MAX:
            issues.append((i, "T8 読点が多い",
                           f"読点{s.count('、')}つ: {s}。1文1情報。カットを割る"))
        if noun_before_noda(s):
            issues.append((i, "§3-2 名詞+なのだ",
                           f"{s}。述語の無い文に語尾だけ付いている。"
                           f"「〜だけだ」「〜になる」のように述語で終える"))

    # T10 体言止めの連続
    run = 0
    for i, s in enumerate(subs, 1):
        if is_taigen(s):
            run += 1
            if run == TAIGEN_RUN:
                issues.append((i, "T10 体言止めの連続",
                               f"#{i - TAIGEN_RUN + 1}〜#{i} が全部体言止め。"
                               f"声で聞くと述語が無くて落ち着かない。1つは述語で終える"))
        else:
            run = 0

    # §3-1 「のだ」率 / T5 「あなた」率
    noda = sum(1 for s in subs if re.search(r"(な|ん)?のだ[。!！?？]?$", s.rstrip("。!！")))
    if noda > n * NODA_MAX_RATIO:
        issues.append((0, "§3-1 「のだ」が多い",
                       f"{noda}/{n}カット。3カットに1回まで(ai-nihongo-rules.md §3)。"
                       f"残りは言い切りにする"))
    anata = sum(1 for s in subs if "あなた" in s)
    if anata > n * ANATA_MAX_RATIO:
        issues.append((0, "T5 二人称が多い",
                       f"「あなた」が{anata}/{n}カット。日本語は主語を省く。"
                       f"4カットに1回に絞り、残りは主語を落とす"))
    return issues


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    exempt = load_exempt("honyaku")
    total = 0
    for vdir in targets:
        vid = vdir.name.split("-")[0]
        ex = exempt.get(vid, set())
        if "*" in ex:
            print(f"[--] {vdir.name} (gate_exempt)")
            continue
        issues = [it for it in check_video(vdir) if it[0] not in ex]
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — 翻訳調 {len(issues)}件")
            for u, kind, detail in sorted(issues):
                where = f"#{u}" if u else "(全体)"
                print(f"       {where:6} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"{total}件。docs/research/ai-nihongo-rules.md の直し方で書き直すこと。")
        sys.exit(1)
    print("結果: 翻訳調なし")


if __name__ == "__main__":
    main()
