#!/usr/bin/env python3
"""言葉・プロットのゲート(2026-08-30)。

`docs/research/kotoba-rules.md` のうち、**機械で見られる規則だけ**を実装したもの。

なぜ作るか: 厳格審査パネル(サブエージェント8人×複数ラウンド)を毎本回すのは
コストが見合わない。パネルが2回にわたって出した指摘を規則に落とし、
**その規則を機械が見る**ようにして、次の動画では最初から踏まないようにする。
文章で書いたルールが守られないのは、このリポジトリが何度も学んだこと。

判定(すべて kotoba-rules.md の規則番号に対応):
  K2  メタ宣言       — 「ここからが本題」の類。中身ゼロの進行アナウンス
  K3  数字の再カウント — 同じ数値が3ユニット以上つづけて主役の座にいる
  N3  条件節の連鎖   — 「〜ば。」「〜と。」の宙吊りが2カット続く
  N5  表記割れ       — 同じ語の「い抜き/い有り」が動画内で混在
  C1  二人称の砂漠   — 二人称も呼びかけも問いも無いユニットが4つ続く
  C4  リビールの語尾 — 着地SE(don/impact)のカットが「です・ます」で終わる
  C8  強調と声の同期 — 【】があるのに intonation の指定が無い

免除は他のゲートと同じく production/gate_exempt.txt に
`<動画ID>:kotoba:<ユニット番号>  # 理由` の形で書く(理由が無い行は無効)。

使い方:
    python3 production/check_kotoba.py                    # 全動画
    python3 production/check_kotoba.py videos/S033-...    # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

# ---- K2: 中身のない進行アナウンス。
# 「ここからが今日の本題です」に1カット(約2秒)を払っていた。
# 離脱の谷でいちばん払ってはいけない2秒だった、という審査の指摘。
META_RE = re.compile(r"(ここから|ここが).{0,6}(本題|本番|大事|重要)"
                     r"|本題(は|です|に入)"
                     r"|(今日|本日)の(話|テーマ|動画)(は|です)"
                     r"|最後まで(見て|ご覧)")

# ---- N3: 宙吊りの条件節。「〜ば。」「〜と。」で終わる文が続くと、
# 結論がいつまでも来ない感じになる(審査の「宙吊り仮定形」)。
HANGING_RE = re.compile(r"(れば|えば|けば|せば|てば|ねば|べば|めば|ると|すと|くと)[。…]?$")

# ---- C1: 二人称・呼びかけ・問い。これが続けて無い区間は「他人の家計簿」に聞こえる。
NININSHO_RE = re.compile(r"(あなた|きみ|君|自分|あなたの|ご自身|みなさん|皆さん)")
TOI_RE = re.compile(r"[??]")

# ---- C4: 着地のSEが鳴るカット(リビール)は体言止め・言い切りにする。
TEINEI_TAIL_RE = re.compile(r"(です|ます|ました|でした|ですね|ますね)[。…]?$")
REVEAL_SE = ("don", "impact")

# ---- N5: い抜きの検出。「〜てる」「〜でる」(い抜き)と「〜ている」「〜でいる」の混在。
INUKI_RE = re.compile(r"([ぁ-ん一-龥ァ-ヴー])(て|で)(る|た|ます|ない)")
IARI_RE = re.compile(r"([ぁ-ん一-龥ァ-ヴー])(てい|でい)(る|た|ます|ない)")

# 数値トークン(K3の再カウント検出用)
NUM_RE = re.compile(r"[0-9０-９][0-9０-９,，]*(?:億|万|千)?(?:円|か月|年|歳|%|回|日)?")

TAIL_EXEMPT = 2      # 締め・CTAは意図的な転換なので、連鎖系の判定から外す


def _load(render_py: Path):
    """render.py を読む。

    **各動画の verify.py は同じ `verify` という名前**なので、全動画を続けて読むと
    2本目以降が1本目の verify を掴んでしまう(実際に「MONTHLY が無い」で落ちた)。
    動画ごとに sys.modules から外し、sys.path も戻す。
    """
    vdir = str(render_py.parent)
    for name in ("verify",):
        sys.modules.pop(name, None)
    sys.path.insert(0, vdir)
    try:
        spec = importlib.util.spec_from_file_location(f"k_{render_py.parent.name}", render_py)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        if sys.path and sys.path[0] == vdir:
            sys.path.pop(0)
        sys.modules.pop("verify", None)


def load_exempt(gate: str):
    """production/gate_exempt.txt から、このゲートの免除を読む(理由の無い行は無効)。

    ユニット番号のかわりに `*` と書くと、その動画のこのゲートを丸ごと免除する。
    このゲートは既存30本より**後に**足したものなので、
    公開済み・公開判断済みの動画(触らない方針)は `*` で外す。
    """
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


def plain(u) -> str:
    return u.subtitle.replace("【", "").replace("】", "")


def emphasized(u) -> list:
    return re.findall(r"【(.+?)】", u.subtitle)


def main_numbers(text: str) -> set:
    """その文が「主役として」出している数値。桁区切りとカンマの揺れを吸収する。"""
    out = set()
    for m in NUM_RE.findall(text):
        norm = m.replace(",", "").replace("，", "")
        if re.fullmatch(r"[0-9０-９]{1,2}", norm.rstrip("円年歳%回日")):
            continue        # 1桁・2桁の裸の数(「3つ」「1つ」等)は主役ではない
        out.add(norm)
    return out


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    try:
        units = getattr(_load(render_py), "UNITS", [])
    except Exception as e:      # noqa: BLE001  render.py が壊れている場合は他ゲートが拾う
        return [(0, f"render.py を読めない: {e}")]
    if not units:
        return []
    subs = [plain(u) for u in units]
    issues = []

    # ---- K2 メタ宣言
    for i, s in enumerate(subs):
        if META_RE.search(s):
            issues.append((i + 1, f"K2 メタ宣言(中身のない進行アナウンス): 「{s}」"))

    # ---- K3 同じ数値が3ユニット以上つづけて出ている
    nums = [main_numbers(s) for s in subs]
    run_start, run_val = 0, None
    for i in range(len(nums) + 1):
        cur = nums[i] if i < len(nums) else set()
        common = (run_val & cur) if run_val is not None else None
        if run_val is not None and common:
            run_val = common
            continue
        if run_val is not None and i - run_start >= 3:
            issues.append((run_start + 1,
                           f"K3 同じ数値 {'/'.join(sorted(run_val))} が "
                           f"{i - run_start}ユニット連続で主役。"
                           f"既出の数字は言い直さず、次の情報へ進めること"))
        run_start, run_val = i, (cur or None)

    # ---- N3 宙吊りの条件節が2カット連続
    for i in range(1, len(subs) - TAIL_EXEMPT):
        if HANGING_RE.search(subs[i]) and HANGING_RE.search(subs[i - 1]):
            issues.append((i + 1, f"N3 条件節の宙吊りが2カット連続: "
                                  f"「{subs[i - 1]}」→「{subs[i]}」"))

    # ---- N5 い抜きの表記割れ(動画内で混在していたら落とす)
    inuki = {f"{a}{b}{c}" for s in subs for a, b, c in INUKI_RE.findall(s)}
    iari = {f"{a}{b[0]}{c}" for s in subs for a, b, c in IARI_RE.findall(s)}
    both = inuki & iari
    if both:
        issues.append((0, f"N5 同じ語で い抜き/い有り が混在: {'、'.join(sorted(both))}"))

    # ---- C1 二人称の砂漠(4ユニット連続で二人称も呼びかけも問いも無い)
    dry = 0
    for i, s in enumerate(subs[:len(subs) - TAIL_EXEMPT]):
        if NININSHO_RE.search(s) or TOI_RE.search(s):
            dry = 0
            continue
        dry += 1
        if dry == 4:
            issues.append((i + 1, "C1 二人称・問いが4ユニット連続で無い。"
                                  "ここは「他人の家計簿」に聞こえる区間になっている"))
            dry = 0

    # ---- C4 リビール(着地SE)の語尾が「です・ます」
    for i, u in enumerate(units):
        if getattr(u, "se", None) in REVEAL_SE and TEINEI_TAIL_RE.search(subs[i]):
            issues.append((i + 1, f"C4 着地SEのカットが丁寧語で終わっている: 「{subs[i]}」。"
                                  f"リビールは体言止め・言い切りにする"))

    # ---- C8 強調があるのに声の抑揚指定が無い
    for i, u in enumerate(units):
        if emphasized(u) and not getattr(u, "intonation", None):
            issues.append((i + 1, f"C8 【】強調があるのに intonation の指定が無い: "
                                  f"「{u.subtitle}」。画面だけ強調して声が平坦になる"))

    ex = load_exempt("kotoba").get(vdir.name.split("-")[0], set())
    if "*" in ex:
        return []
    if ex:
        issues = [it for it in issues if it[0] not in ex]
    return sorted(issues)


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — 言葉・プロット {len(issues)}件")
            for n, why in issues:
                where = f"#{n}" if n else "全体"
                print(f"       {where}  {why}")
        else:
            print(f"[OK] {vdir.name}")
    if total:
        print(f"\n{total}件。docs/research/kotoba-rules.md を見て直すこと")
        sys.exit(1)
    print("\n言葉・プロットのゲート: 合格")


if __name__ == "__main__":
    main()
