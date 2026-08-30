#!/usr/bin/env python3
"""見た目のゲート(2026-08-30)。

`docs/research/design-rules.md` のうち、**機械で見られる規則だけ**を実装したもの。
作った理由は check_kotoba.py と同じ: 批評パネルを毎本回す代わりに、
パネルが出した指摘を規則にして機械に見させる。

判定(design-rules.md の規則番号に対応):
  T7  強調の用量   — 1行の【】が2トークン以上、または強調の文字比率が40%超
  C1  色リテラル   — render.py の中に生の #rrggbb が散らばっている(部品側で持つこと)
  M2  線形補間     — 描画部品に min(1.0, t*N) 系の等速アニメが残っている
  M1  尻の静止     — 各ユニットの最後の2フレームが同一(ナレーション後半が止め絵)

M1 は output/work/ にフレームが残っているときだけ走る(焼いた直後なら残っている)。
無いときは黙って飛ばす。**フレームが無いことを合格の根拠にしない。**

免除は production/gate_exempt.txt に `<動画ID>:design:<番号|*>  # 理由`。

使い方:
    python3 production/check_design.py                    # 全動画
    python3 production/check_design.py videos/S033-...    # 1本だけ
"""
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

# T2(桁区切り)はゲートにしない。
# fplib.fmt_disp が描画の直前に4桁以上を自動で桁区切りするので、render.py の
# リテラルが「3162円」でも画面は「3,162円」になる。リテラルを見る判定は
# **17件すべてが偽陽性**だった(2026-08-30に実装して即撤回)。
# 偽陽性を出すゲートは無視されるようになり、ゲート全体の信用を壊す。
# T2 は fmt_disp の実装で担保されている、として目視検収に残す。

# T7: 強調の用量
EMPH_RE = re.compile(r"【(.+?)】")

# C1: 生の色リテラル。定数定義(NAME = "#xxxxxx")の行は除く
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
CONST_DEF_RE = re.compile(r"^\s*[A-Z_][A-Z0-9_]*\s*=")

# M2: 等速の線形補間。イージングが無いと「機械が動かした」感じになる
LINEAR_RE = re.compile(r"min\(\s*1(?:\.0)?\s*,\s*t\s*[*/]")

# 免除に使う番号(ユニット番号を持たない全体判定は 0)
GLOBAL = 0


def load_exempt(gate: str):
    """gate_exempt.txt から免除を読む。`*` はその動画をまるごと免除。"""
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


def check_common_parts():
    """動画によらない共通部品の検査(M2 線形補間)。"""
    issues = []
    for name in ("scenes_fp.py", "scenes_common.py", "scenes_long.py", "fplib.py"):
        f = PRODUCTION / name
        if not f.exists():
            continue
        for i, ln in enumerate(f.read_text().splitlines(), 1):
            if ln.lstrip().startswith("#"):
                continue
            if LINEAR_RE.search(ln):
                issues.append(f"M2 {name}:{i} 等速の線形補間 `{ln.strip()[:60]}`。"
                              f"イージング(ease_out 系)を通すこと")
    return issues


def frame_units(vdir: Path):
    """output/work/ のフレームをユニット番号ごとにまとめる(あれば)。"""
    work = vdir / "output" / "work"
    if not work.is_dir():
        return {}
    groups = {}
    for f in work.glob("frame_*.png"):
        m = re.match(r"frame_(\d+)_(\d+)\.png$", f.name)
        if not m:
            continue
        unit, sub = int(m.group(1)), int(m.group(2))
        if sub >= 900:          # 990 はカバー(静止1枚)なので対象外
            continue
        groups.setdefault(unit, []).append((sub, f))
    return {u: [f for _, f in sorted(v)] for u, v in groups.items()}


def tail_is_frozen(frames):
    """ユニット末尾の2フレームで**図が**動いているか(M1 尻の静止)。

    画面全体の差分で見てはいけない。背景のドット壁紙が常に流れているので、
    図が完全に止まっていても全画面差分は 0.7% ほど出る。実際、最初に全画面で
    実装したら「静止ゼロ件」で合格してしまった(審査団は同じ動画で
    「9本のユニットで最終20%が完全静止」と実測していた)。
    **尻の生存を背景の動きに肩代わりさせない**、というのが規則の趣旨。

    だから (1) 図の領域(上下の帯と字幕帯を除く)に絞り、
    (2) 弱い差(アンチエイリアスや壁紙のドリフト)を捨てて
    輝度差40以上の「本当に変わった画素」だけを数える。
    実測: 動いているユニット 0.2〜1.4% / 止まっているユニット 0.000%。
    """
    if len(frames) < 2:
        return None             # 1枚しか無いユニットは判定しない(短すぎる)
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return None
    a = np.asarray(Image.open(frames[-2]).convert("RGB"), dtype=np.int16)
    b = np.asarray(Image.open(frames[-1]).convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        return None
    diff = np.abs(a - b).max(axis=2)
    h, w = diff.shape
    fig = diff[int(h * 0.20):int(h * 0.72), int(w * 0.05):int(w * 0.95)]
    return float((fig > 40).mean()) < 0.0005


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    src = render_py.read_text()
    issues = []

    # ---- T7 強調の用量(字幕1行あたり)
    try:
        sys.path.insert(0, str(vdir))
        sys.modules.pop("verify", None)
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"d_{vdir.name}", render_py)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        units = getattr(mod, "UNITS", [])
    except Exception as e:      # noqa: BLE001
        return [(GLOBAL, f"render.py を読めない: {e}")]
    finally:
        if sys.path and sys.path[0] == str(vdir):
            sys.path.pop(0)
        sys.modules.pop("verify", None)

    for i, u in enumerate(units):
        toks = EMPH_RE.findall(u.subtitle)
        if len(toks) >= 2:
            issues.append((i + 1, f"T7 強調が1カットに{len(toks)}箇所 "
                                  f"({'/'.join(toks)})。視線の着地点が割れる"))
            continue
        if toks:
            plain = EMPH_RE.sub(r"\1", u.subtitle)
            ratio = len(toks[0]) / max(1, len(plain))
            if ratio > 0.40:
                issues.append((i + 1, f"T7 強調の文字比率 {ratio:.0%}(40%超)。"
                                      f"強調は数字トークンだけに絞る"))

    # ---- C1 色リテラルの散在
    for i, ln in enumerate(src.splitlines(), 1):
        s = ln.lstrip()
        if s.startswith("#") or CONST_DEF_RE.match(ln):
            continue
        if HEX_RE.search(ln):
            issues.append((GLOBAL, f"C1 render.py:{i} に生の色 "
                                   f"{HEX_RE.search(ln).group()}。"
                                   f"色は部品側のトークンで持つこと"))

    # ---- M1 尻の静止(焼いたフレームが残っているときだけ)
    groups = frame_units(vdir)
    for unit, frames in sorted(groups.items()):
        if unit >= len(units):
            continue
        if tail_is_frozen(frames):
            issues.append((unit + 1, "M1 ユニット末尾が止め絵(最後の2フレームが同一)。"
                                     "ナレーション後半に動きが無い"))

    ex = load_exempt("design").get(vdir.name.split("-")[0], set())
    if "*" in ex:
        return []
    if ex:
        issues = [it for it in issues if it[0] not in ex]
    return sorted(issues)


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    common = check_common_parts()
    if common:
        total += len(common)
        print(f"[NG] production/(共通部品) — {len(common)}件")
        for why in common:
            print(f"       {why}")
    for vdir in targets:
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — 見た目 {len(issues)}件")
            for n, why in issues:
                where = f"#{n}" if n else "全体"
                print(f"       {where}  {why}")
        else:
            print(f"[OK] {vdir.name}")
    if total:
        print(f"\n{total}件。docs/research/design-rules.md を見て直すこと")
        sys.exit(1)
    print("\n見た目のゲート: 合格")


if __name__ == "__main__":
    main()
