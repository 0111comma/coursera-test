#!/usr/bin/env python3
"""出荷物のゲート(2026-08-30 の厳格審査 thumbnail/high・craft/high)。

このゲートが無かったせいで、**同じクラスの欠陥が3回出荷物に残った**。

1. **鮮度** — output/<ID>.mp4 が render.py / production の描画コードより古い。
   2026-08-29 の版は mp4 が旧デザインのままで、thumbnail.png(新デザイン)と
   本編0秒目(旧デザイン)が別物だった。サムネの約束が再生1フレーム目で
   裏切られていたのに、14本のゲートを全部通っていた。

2. **サムネ一致** — mp4 の第0フレームと output/thumbnail.png が一致すること
   (平均絶対差 2/255 以内)。`render.py --thumb` は mp4 を更新しないので、
   サムネだけ差し替えて満足すると必ずここで割れる。

3. **強調枠の外周** — 強調枠(赤/緑のリング)の外側1〜6pxに、
   枠色でも面色でもない「第三の色」が出ていないこと。
   帯の矩形が枠の矩形より広いと、リングの外に地の帯が3〜4px露出する。
   これは2ラウンド連続で出荷物に残った(前回の修正が band() にしか
   入っておらず、合計行を描く hband() は広い矩形のままだった)。

4. **図と字幕のクリアランス** — 図の最下端と字幕ブロック上端の空きが
   30px以上あること。実測で 0〜1px の接触と 466px の空洞が同居していた。

使い方:
    python3 production/check_shukka.py videos/S033-subsc-30nen
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

import matplotlib                                    # noqa: E402
matplotlib.use("Agg")
import numpy as np                                   # noqa: E402
import shortlib as S                                 # noqa: E402

# 描画コードが変わったら mp4 は古い(このどれかより古ければ落とす)
SOURCES = ["render.py"]
LIB_SOURCES = ["scenes_fp.py", "fplib.py", "shortlib.py", "scenes_common.py"]
RING_COLORS = [(179, 32, 32), (94, 140, 63), (111, 102, 83)]   # RED / GREEN / NEUTRAL
EXEMPT = PRODUCTION / "gate_exempt.txt"


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"sh_{render_py.parent.name}",
                                                  render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def check_freshness(vdir: Path):
    """mp4 が描画コードより新しいこと。"""
    issues = []
    vid = vdir.name.split("-")[0]
    mp4 = vdir / "output" / f"{vid}.mp4"
    if not mp4.exists():
        return [("mp4", "未出荷", f"{mp4} が無い。焼いてから出荷すること")]
    mt = os.path.getmtime(mp4)
    for name in SOURCES:
        p = vdir / name
        if p.exists() and os.path.getmtime(p) > mt:
            issues.append(("mp4", "鮮度", f"{name} のほうが mp4 より新しい。"
                                          "焼き直すこと(--thumb はmp4を更新しない)"))
    for name in LIB_SOURCES:
        p = PRODUCTION / name
        if p.exists() and os.path.getmtime(p) > mt:
            issues.append(("mp4", "鮮度",
                           f"production/{name} のほうが mp4 より新しい。焼き直すこと"))
    return issues


def check_thumb_matches(vdir: Path):
    """mp4 の第0フレームと thumbnail.png が一致すること。"""
    vid = vdir.name.split("-")[0]
    mp4 = vdir / "output" / f"{vid}.mp4"
    thumb = vdir / "output" / "thumbnail.png"
    if not mp4.exists() or not thumb.exists():
        return []
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "f0.png"
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4),
                            "-vframes", "1", str(out)], capture_output=True)
        if r.returncode != 0 or not out.exists():
            return [("mp4", "読めない", "第0フレームを取り出せなかった")]
        a = np.asarray(Image.open(out).convert("RGB"), dtype=np.float32)
        b = np.asarray(Image.open(thumb).convert("RGB"), dtype=np.float32)
    if a.shape != b.shape:
        return [("mp4", "サムネ不一致", f"寸法が違う {a.shape} vs {b.shape}")]
    d = float(np.abs(a - b).mean())
    if d > 2.0:
        return [("mp4", "サムネ不一致",
                 f"第0フレームと thumbnail.png の平均絶対差 {d:.1f}/255。"
                 "サムネだけ差し替えて mp4 を焼き直していない")]
    return []


def _runs(mask_1d, minlen):
    """1次元マスクの連続 True 区間で minlen 以上のものを返す。"""
    out, start = [], None
    for i, v in enumerate(mask_1d):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= minlen:
                out.append((start, i - 1))
            start = None
    if start is not None and len(mask_1d) - start >= minlen:
        out.append((start, len(mask_1d) - 1))
    return out


def _ring_leak(img: np.ndarray, ring_rgb, tol=22):
    """強調枠の外周1〜6pxに『枠色でも面色でもない第三の色』が出ていないか。

    枠を**矩形として**特定する: 縦60px以上つづく列(左右の辺)と
    横400px以上つづく行(上下の辺)が2組そろってはじめて枠とみなす。
    こうしないと、同じ色の**文字のインク**を枠と誤認して、帯の中の文字の
    左右をスキャンし、常に「帯色が見える」と鳴ってしまう。
    """
    rgb = img.astype(int)
    ring = (np.abs(rgb - np.array(ring_rgb)).max(axis=2) <= tol)
    if ring.sum() < 400:
        return []
    H_, W_ = ring.shape
    vcols = [x for x in range(W_) if _runs(ring[:, x], 60)]
    hrows = [y for y in range(H_) if _runs(ring[y, :], 400)]
    if len(vcols) < 2 or len(hrows) < 2:
        return []
    x_l, x_r = min(vcols), max(vcols)
    y_t, y_b = min(hrows), max(hrows)
    if x_r - x_l < 400 or y_b - y_t < 40:
        return []
    bad = []
    for y in range(y_t + 12, y_b - 12, 4):
        for x, step in ((x_l, -1), (x_r, +1)):
            seen = [tuple(rgb[y, x + step * k]) for k in range(1, 11)
                    if 0 <= x + step * k < W_]
            if _is_third_color(seen):
                bad.append((int(y), int(x), seen[:3]))
    for x in range(x_l + 40, x_r - 40, 40):
        for y, step in ((y_t, -1), (y_b, +1)):
            seen = [tuple(rgb[y + step * k, x]) for k in range(1, 11)
                    if 0 <= y + step * k < H_]
            if _is_third_color(seen):
                bad.append((int(y), int(x), seen[:3]))
    return bad[:3]


# 帯の地。これが枠の外に3px以上つづけて出ていたら「第三の色」
_BANDS = [(239, 226, 200), (249, 230, 220), (232, 240, 220), (234, 226, 210)]
_NOT_INK = [(243, 231, 211), (249, 241, 227), (255, 253, 247)]


_CARD = (255, 253, 247)


def _is_third_color(seen):
    """枠の外に帯色が3px以上つづき、**その先にカード白が来る**なら露出。

    「その先が白」を要件にするのは、カードの落ち影(クリームと SHADOW の
    中間色)が帯色の許容範囲に入ってしまうため。影はカードの**外**にしか
    出ないので、白へ抜けるかどうかで内と外を分けられる。
    """
    run = 0
    for k, c in enumerate(seen):
        is_band = any(max(abs(c[i] - b[i]) for i in range(3)) <= 3 for b in _BANDS)
        is_ground = any(max(abs(c[i] - g[i]) for i in range(3)) <= 6
                        for g in _NOT_INK)
        run = run + 1 if (is_band and not is_ground) else 0
        if run >= 3:
            rest = seen[k + 1:]
            if any(max(abs(c2[i] - _CARD[i]) for i in range(3)) <= 4
                   for c2 in rest):
                return True
    return False


def check_thumb_density(vdir: Path):
    """サムネの**面積配分**(2026-08-30 thumbnail/medium)。

    素地(クリーム地+ドット)が広すぎると「情報の無い板」に見える。
    ただし Shorts 実機の安全帯(上8.5%・下15%)は**空けるのが正しい**ので、
    その外側を除いた帯の中で測る。
    """
    thumb = vdir / "output" / "thumbnail.png"
    if not thumb.exists():
        return []
    from PIL import Image
    import fplib as F
    a = np.asarray(Image.open(thumb).convert("RGB")).astype(int)
    m = np.zeros(a.shape[:2], dtype=bool)
    for c in _GROUND:
        m |= (np.abs(a - np.array(c)).max(axis=2) <= 18)
    h = a.shape[0]
    safe = m[int(h * F.UI_TOP_FRAC):h - int(h * F.UI_BOTTOM_FRAC)]
    issues = []
    if safe.mean() > 0.35:
        issues.append(("thumbnail", "素地が多い",
                       f"安全帯の中の素地率 {safe.mean() * 100:.0f}%(35%未満に)"))
    rows = safe.mean(axis=1) > 0.92
    run = best = 0
    for v in rows:
        run = run + 1 if v else 0
        best = max(best, run)
    if best > 100:
        issues.append(("thumbnail", "空白帯",
                       f"安全帯の中に {best}px の連続空白(100px以内に)"))
    return issues


def check_pixels(vdir: Path):
    """全カットの t=1.0 を描いて、強調枠の露出と字幕クリアランスを見る。"""
    render_py = vdir / "render.py"
    if not render_py.exists() or vdir.name.startswith("L"):
        return []
    mod = _load(render_py)
    scenes = getattr(mod, "SCENES", {})
    units = getattr(mod, "UNITS", [])
    if not scenes:
        return []
    import scenes_fp as sf
    from PIL import Image
    issues = []
    sub_top_px = sf.sub_top() * S.H
    with tempfile.TemporaryDirectory() as td:
        for u in units:
            for key in (u.scene, f"{u.scene}__cover"):
                painter = scenes.get(key)
                if painter is None:
                    continue
                fig = S.new_canvas(1.0)
                painter(fig, 1.0)
                p = Path(td) / f"{key}.png"
                S.save_frame(fig, p)
                img = np.asarray(Image.open(p).convert("RGB"))
                for rc in RING_COLORS:
                    for y, x, seen in _ring_leak(img, rc):
                        issues.append((key, "強調枠の外に地の帯",
                                       f"y={y} x={x} の外周に {seen}"))
                        break
                if key.endswith("__cover"):
                    continue
                # 図の最下端と字幕ブロック上端の空き(0〜1px接触と466px空洞の
                # 両方を1本の判定で捕まえる)
                bot = _content_bottom_px(img)
                if bot is None:
                    continue
                gap = (S.H - bot) - sub_top_px
                if gap < sf.CLEAR_MIN * S.H:
                    issues.append((key, "字幕との衝突",
                                   f"図の最下端と字幕上端の空きが {gap:.0f}px"
                                   f"({sf.CLEAR_MIN * S.H:.0f}px以上とること)"))
    return issues


# 地(クリーム #f3e7d3 と地紋 #f9f1e3)。これ以外の色を「図のインク」とみなす
_GROUND = [(243, 231, 211), (249, 241, 227)]


def _content_bottom_px(img: np.ndarray):
    """図のいちばん下のインク行(画像座標。上が0)を返す。"""
    rgb = img.astype(int)
    ink = np.ones(rgb.shape[:2], dtype=bool)
    for g in _GROUND:
        ink &= (np.abs(rgb - np.array(g)).max(axis=2) > 10)
    rows = np.where(ink.sum(axis=1) > 8)[0]
    return int(rows.max()) if len(rows) else None


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir()
        if (p / "render.py").exists() and p.name.startswith("S"))
    exempt = set()
    if EXEMPT.exists():
        exempt = {ln.split("#")[0].strip() for ln in EXEMPT.read_text().splitlines()
                  if ln.split("#")[0].strip()}
    total = 0
    # 項目ごとの免除も読む(2026-09-03)。形式: <ID>:shukka:<項目名>  # 理由
    # 項目名は issues の kind(例「素地が多い」)。**動画まるごと外さずに、
    # 落ちている1項目だけを理由つきで外す**ため。全体を外すと鮮度・サムネ一致の
    # ような、外してはいけない判定まで一緒に消える
    per_item = {}
    if EXEMPT.exists():
        for ln in EXEMPT.read_text().splitlines():
            body, _, reason = ln.partition("#")
            parts = [x.strip() for x in body.strip().split(":")]
            if len(parts) == 3 and parts[1] == "shukka" and reason.strip():
                per_item.setdefault(parts[0], set()).add(parts[2])
    for vdir in targets:
        if vdir.name in exempt:
            print(f"[--] {vdir.name} (gate_exempt)")
            continue
        issues = (check_freshness(vdir) + check_thumb_matches(vdir)
                  + check_thumb_density(vdir) + check_pixels(vdir))
        skip = per_item.get(vdir.name.split("-")[0], set())
        if skip:
            issues = [it for it in issues if it[1] not in skip]
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — {len(issues)}件")
            for where, kind, detail in issues:
                print(f"       {where:16} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}件。出荷物と描画の食い違いを直すこと。")
        sys.exit(1)
    print("結果: 出荷物は基準内")


if __name__ == "__main__":
    main()
