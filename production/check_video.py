#!/usr/bin/env python3
"""公開前の自動チェック(ループ26)。使い方:
    python3 production/check_video.py videos/S001-tsumitate-fukuri

台本・レンダースクリプト・出力mp4を機械検証できる範囲で照合する。
(物語面のチェックリストD1〜D22は docs/research/plot-playbook.md で人が照合する)
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shortlib import SUB_WRAP, wrap_plain  # noqa: E402

# 戦略§6(コンプライアンス): 断定・投資助言に当たる表現の禁止
FORBIDDEN = ["儲かる", "必ず増え", "絶対に増え", "損しない", "買うべき", "おすすめの銘柄", "おすすめの証券"]

def main(video_dir: Path) -> int:
    fails, warns = [], []

    def check(name, ok, detail=""):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            fails.append(name)

    print(f"チェック対象: {video_dir}")

    # 1. verify.py が通る
    vp = video_dir / "verify.py"
    if vp.exists():
        r = subprocess.run(["python3", str(vp)], capture_output=True, text=True)
        check("verify.py 実行", r.returncode == 0, (r.stderr or "").strip()[:80])
    else:
        check("verify.py 存在", False, "計算を含む動画は必須")

    # 2. render.py のユニット文の長さ・折り返し・禁止語
    rp = video_dir / "render.py"
    src = rp.read_text() if rp.exists() else ""
    units = re.findall(r'Unit\(\s*"[^"]+",\s*"([^"]+)"', src)
    check("render.py にユニット定義", len(units) > 0, f"{len(units)}ユニット")
    total_chars = 0
    for u in units:
        plain = u.replace("【", "").replace("】", "")
        total_chars += len(plain)
        if len(plain) > 35:
            check(f"1文35字以内: {plain[:14]}…", False, f"{len(plain)}字")
        if len(wrap_plain(plain, SUB_WRAP)) > 2:
            check(f"字幕2行以内: {plain[:14]}…", False)
    check("ユニット文長(全体)", True, f"合計{total_chars}字")
    # 字幕の安全幅(ループ⑫): 最長行が block_fit=0.70 に収まる際の縮小率が75%未満なら
    # 読みにくくなるので文を書き直す(概算幅: 全角1.0/半角0.55/約物0.6)
    def _w(ch):
        return 0.6 if ch in "。、!?…" else (0.55 if ord(ch) < 0x100 else 1.0)
    for u in units:
        plain = u.replace("【", "").replace("】", "")
        for line in wrap_plain(plain, SUB_WRAP):
            frac = sum(_w(c) for c in line) * (52 / 72 * 100) / 1080
            if 0.70 / max(frac, 1e-9) < 0.75:
                check(f"字幕縮小75%未満: {line[:12]}…", False, f"行幅{frac:.2f}")
    est = total_chars * 0.191 + len(units) * 0.15  # 実測2本(53.7s/265字, 55.9s/276字)から較正
    check("推定尺 55秒以内", est <= 55.5, f"約{est:.0f}秒")
    joined = "".join(units) + src
    bad = [w for w in FORBIDDEN if w in joined]
    check("禁止表現なし(戦略§6)", not bad, ",".join(bad))
    check("仮定バッジの描画", "draw_badge" in src, "利回り等の仮定明示")
    # 利回り等の仮定に基づく数字を扱う動画は、動画内に元本リスクの打消し表示が必要(ループ⑫)。
    # 仮定を含まない動画(制度上限の割り算など事実のみ)は対象外
    if "draw_badge" in src and "仮定" in src:
        check("動画内リスク表示(元本)", "元本" in src, "打消し表示: 消費者庁実態調査準拠")

    # 3. script.md の必須要素
    sp = video_dir / "script.md"
    smd = sp.read_text() if sp.exists() else ""
    check("script.md 存在", bool(smd))
    check("VOICEVOXクレジット", "VOICEVOX:" in smd, "キャラ利用ガイドライン必須")
    # ループ㉛: #shortsは判定に不要(自動判定)。日本語ハッシュタグ2〜4個の行が方針
    tagline = re.search(r"^(#\S+(?:\s+#\S+)+)\s*$", smd, re.M)
    ntags = len(tagline.group(1).split()) if tagline else 0
    check("ハッシュタグ行2〜4個(日本語)", 2 <= ntags <= 4, f"{ntags}個")
    # 投資系は「投資助言ではありません」、給与・制度系は「〜アドバイスではありません」等を許容
    check("免責文", ("投資助言ではありません" in smd) or ("アドバイスではありません" in smd))

    # 4. 出力mp4の機械検証
    mp4 = video_dir / "output" / next((p.name for p in (video_dir / "output").glob("*.mp4")), "none.mp4")
    if mp4.exists():
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
            capture_output=True, text=True).stdout.strip())
        check("尺 60秒未満", dur < 60, f"{dur:.1f}s")
        vd = subprocess.run(["ffmpeg", "-i", str(mp4), "-af", "volumedetect", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
        m = re.search(r"mean_volume: ([-\d.]+) dB", vd)
        mean = float(m.group(1)) if m else -99
        check("平均音量 -18〜-11dB(≈-14LUFS)", -18 <= mean <= -11, f"{mean}dB")
        wh = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                             "-show_entries", "stream=width,height", "-of", "csv=p=0", str(mp4)],
                            capture_output=True, text=True).stdout.strip()
        check("解像度 1080x1920", wh == "1080,1920", wh)
        # ループ⑭: 末尾に0.4秒以上の無音が残っているとループの継ぎ目に死に時間が生まれる。
        # 無音が動画末尾まで続くと silence_start だけ出て silence_end が出ないことを利用
        sil = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(max(dur - 2, 0)), "-i", str(mp4),
                              "-af", "silencedetect=noise=-30dB:d=0.4", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        check("末尾の死に時間なし(ループ継ぎ目)", sil.count("silence_start") == sil.count("silence_end"),
              "即切り0.15s(⑦/⑭)")
    else:
        check("output/*.mp4 存在", False)
    check("thumbnail.png 存在", (video_dir / "output" / "thumbnail.png").exists(), "カバーフレーム書き出し")

    print(f"\n結果: {'ALL PASS' if not fails else f'{len(fails)}件 FAIL'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
