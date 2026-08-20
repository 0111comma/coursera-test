#!/usr/bin/env python3
"""公開前の自動チェック(ループ26)。使い方:
    python3 production/check_video.py videos/S001-tsumitate-fukuri

台本・レンダースクリプト・出力mp4を機械検証できる範囲で照合する。
(物語面のチェックリストD1〜D22は docs/research/plot-playbook.md で人が照合する)
"""
import importlib.util
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shortlib import SPEED_SCALE, SUB_WRAP, wrap_plain  # noqa: E402


def vv_total_sec(video_dir: Path):
    """VOICEVOX の音素長から尺を出す(S030で実測較正: 誤差±0.05秒/ユニット)。

    字数からの推定は数字の多い本ほど実測より短く出る(7172円=4字だが10モーラ)。
    S027/S028/S030 が「推定合格→焼いたら55.5秒超過」を繰り返したので、
    エンジンが起きていれば読み上げそのものの長さで判定する。
    式: (モーラ長合計 + 前後の無音0.15) ÷ 話速 + pad
    """
    try:
        urllib.request.urlopen("http://127.0.0.1:50021/version", timeout=3).read()
    except Exception:
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            f"cv_{video_dir.name}", video_dir / "render.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        units = mod.UNITS
    except Exception:
        return None
    total = 0.0
    for u in units:
        url = ("http://127.0.0.1:50021/audio_query?text="
               f"{urllib.parse.quote(u.tts_text())}&speaker=3")
        q = json.load(urllib.request.urlopen(
            urllib.request.Request(url, method="POST"), timeout=30))
        raw = 0.0
        for ap in q["accent_phrases"]:
            for mo in ap["moras"]:
                raw += (mo.get("consonant_length") or 0) + (mo["vowel_length"] or 0)
            if ap.get("pause_mora"):
                pm = ap["pause_mora"]
                raw += (pm.get("consonant_length") or 0) + (pm["vowel_length"] or 0)
        total += (raw + 0.15) / (u.speed * SPEED_SCALE) + u.pad
    return total

# 戦略§6(コンプライアンス): 断定・投資助言に当たる表現の禁止
# 1文字あたりの秒数(ループ58で再較正)。話速を1.3倍にしたので、
# 実測 0.1462秒/字(S011+S012の全543字を新しい速度で合成して測定)に4%の余裕を足した
SEC_PER_CHAR = 0.152

FORBIDDEN = ["儲かる", "必ず増え", "絶対に増え", "損しない", "買うべき", "おすすめの銘柄", "おすすめの証券"]


# ── 締めのコメント募集(ループ71のユーザー指摘) ──────────────────────
# 「『あなたは今年やった?』と聞いて100人がコメントするでしょ?
#   やったとかやってないとか言ってて、そのコメント欄になんの価値があるの?
#   人間をあまり馬鹿にしないでね。『おすすめのふるさと納税の返礼品は?』とか
#   そういった質問をする方が、コメント獲得率も上がると思うし、
#   コメント欄を開いてみようかなと思う人も増えると思うんだけどどう?」
#
# そのとおりで、自分の状態を答えるだけの問いは、
# **集まった答えを他の視聴者が読んでも何も得しない**。
# 情報を求める問いにする。ここでは問いの中に「情報を求める語」を必須にした。
ASK_INFO = ("おすすめ", "コツ", "どこで", "どうやって", "何のため", "他に",
            "なぜ", "どれ", "どんな", "何を", "決め手", "きっかけ", "使い道")


def check_comment_question(src: str, check):
    m = re.search(r'sc\.chips\(\s*"([^"]+)"', src) or \
        re.search(r'sl\.chips\(\s*"([^"]+)"', src)
    if not m:
        return
    q = m.group(1)
    ok = any(w in q for w in ASK_INFO)
    check(f"コメントの問いが情報を求めている: 「{q}」", ok,
          "自分の状態を答えるだけの問いは、集まっても他の人の役に立たない。"
          "おすすめ・コツ・どこで・何のため などを聞くこと")


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
    # 形式の判定。use_landscape() を呼ぶ render.py は横型の長尺
    LONG = "use_landscape" in src
    WRAP = 26 if LONG else SUB_WRAP
    FIG_W = 1920 if LONG else 1080
    BLOCK_FIT = 0.86 if LONG else 0.70
    SUB_PT = 40 if LONG else 52
    units = re.findall(r'Unit\(\s*"[^"]+",\s*"([^"]+)"', src)
    check("render.py にユニット定義", len(units) > 0, f"{len(units)}ユニット")
    total_chars = 0
    for u in units:
        plain = u.replace("【", "").replace("】", "")
        total_chars += len(plain)
        if len(plain) > (48 if LONG else 35):
            check(f"1文35字以内: {plain[:14]}…", False, f"{len(plain)}字")
        if len(wrap_plain(plain, WRAP)) > 2:
            check(f"字幕2行以内: {plain[:14]}…", False)
    check("ユニット文長(全体)", True, f"合計{total_chars}字")
    # 字幕の安全幅(ループ⑫): 最長行が block_fit=0.70 に収まる際の縮小率が75%未満なら
    # 読みにくくなるので文を書き直す(概算幅: 全角1.0/半角0.55/約物0.6)
    def _w(ch):
        return 0.6 if ch in "。、!?…" else (0.55 if ord(ch) < 0x100 else 1.0)
    for u in units:
        plain = u.replace("【", "").replace("】", "")
        for line in wrap_plain(plain, WRAP):
            frac = sum(_w(c) for c in line) * (SUB_PT / 72 * 100) / FIG_W
            if BLOCK_FIT / max(frac, 1e-9) < 0.75:
                check(f"字幕縮小75%未満: {line[:12]}…", False, f"行幅{frac:.2f}")
    # 実測から較正。0.152字/秒は平均値で、**数字が多い本ほど実測は伸びる**
    #   S013 276字/18u → 推定55.8s / 実測55.9s(一致)
    #   S012 345字/18u → 推定55.1s / 実測58.0s(+5%。金額の読み上げが多い)
    # 上限55.5sは60秒に対する安全余裕として置いてある。定数は動かさない
    est = total_chars * SEC_PER_CHAR + len(units) * 0.15
    vv = vv_total_sec(video_dir)
    if vv is not None:
        est = vv          # エンジンが起きていれば音素長ベース(誤差±1秒未満)を使う
    if LONG:
        # 尺は**下限で縛らない**(ループ70 フェーズ1)。
        # 「8分以上」を不合格条件にしていたら、8分に届かせるために内容を足した。
        # L002 は66ユニット(3.65分)で書き終えたあと、尺の理由だけで+89ユニット足している。
        # 8分はミッドロール広告の条件(収益側の閾値)で、視聴者のための数字ではない。
        # 尺の判定は**企画の段階**(plan.md「8分ぶんの中身があるか」)に移した。
        if est < 480:
            warns.append(f"推定尺が8分未満(約{est / 60:.1f}分)。"
                         "ミッドロール広告は付かない。**尺のために内容を足さないこと**")
            print(f"  [WARN] 推定尺 — 約{est / 60:.1f}分(8分未満。広告条件を満たさない)")
        else:
            check("推定尺", True, f"約{est / 60:.1f}分")
    else:
        check("推定尺 55秒以内", est <= 55.5, f"約{est:.0f}秒")
    joined = "".join(units) + src
    bad = [w for w in FORBIDDEN if w in joined]
    check("禁止表現なし(戦略§6)", not bad, ",".join(bad))
    # 横型(長尺)はシーンを scenes_long 側で組むので、render.py に draw_badge が出てこない。
    # 代わりに BADGE を各シーンに渡しているかで見る(渡さないとバッジは描かれない)
    # 縦型も同じ。scenes_common の card/bars2/hayami/chips は BADGE を受け取って
    # 内部で draw_badge を呼ぶので、render.py に "draw_badge" の字面は出てこない。
    # 字面ではなく「BADGE を定義して各シーンに渡しているか」で見る(ループ71)
    has_badge = "draw_badge" in src or (re.search(r"BADGE\s*=", src) and "BADGE" in src)
    check("仮定バッジの描画", bool(has_badge), "利回り等の仮定明示")

    check_comment_question(src, check)

    # P系(ループ㊳: ユーザーレビュー第7弾)。前置き・生活翻訳・情景ユーモア・中盤の問い
    cover_m = re.search(r'"[\w]+__cover":\s*s[cl]\.cover\(\s*"([^"]*)"', src)
    lead_m = re.search(r'lead="([^"]*)"', src)
    cover_top = cover_m.group(1) if cover_m else ""
    check("D23 前置き(1フレーム目に問い)", "?" in cover_top or (lead_m and "?" in lead_m.group(1)),
          f"cover上段='{cover_top}'。P1: 数字だけのカバーにしない")
    # 締めの4択より前に、二人称の問いが1つ以上あるか(P4: 中盤で自分ごと化させる)
    mid = src.split("sc.chips")[0]
    mid_q = re.findall(r'"[^"]*あなた[^"]*[??][^"]*"', mid)
    check("D26 中盤の問い(二人称・締めより前)", bool(mid_q),
          "" if mid_q else "P4: 締めの質問と同趣旨の問いを中盤の図解にも重ねる")
    # 運用利回りの仮定に基づく数字を扱う動画は、動画内に元本リスクの打消し表示が必要(ループ⑫)。
    # 物価上昇率など運用リターン以外の仮定や、事実のみの動画は対象外
    if "draw_badge" in src and re.search(r"(年\d|年利|利回り|リターン|運用).{0,10}仮定", src):
        check("動画内リスク表示(元本)", "元本" in src, "打消し表示: 消費者庁実態調査準拠")

    # 2.5 企画書(plan.md)の必須4行 — ループ㊹
    # 「誰が、なぜこの動画で指を止めるのか」を定義せずに render.py を書いたことが
    # ユーザー却下の根因だった。文章で書いたルールは守られないので、ここで落とす。
    pp = video_dir / "plan.md"
    pmd = pp.read_text() if pp.exists() else ""
    check("plan.md 存在", bool(pmd), "企画書なしで台本を書かない(docs/persona.md)")
    for key, hint in [("想定視聴者", "P-A/P-Bのどちらか+具体的な状況"),
                      ("指を止める理由", "この人はフィードで何を見て止まるのか"),
                      ("視聴後に得るもの", "この人は何が分かるようになるのか"),
                      ("この動画の結論", "ネタ選定ゲートF1: 予想と食い違うこと")]:
        check(f"plan.md「{key}」", key in pmd, hint)

    # 3. script.md の必須要素
    sp = video_dir / "script.md"
    smd = sp.read_text() if sp.exists() else ""
    check("script.md 存在", bool(smd))
    check("VOICEVOXクレジット", "VOICEVOX:" in smd, "キャラ利用ガイドライン必須")
    if "use_duo" in src:
        check("四国めたんクレジット(二人会話)", "VOICEVOX:四国めたん" in smd,
              "二人会話の動画は両方の音源クレジットが必須(duo-skit-2026-08.md)")
    # ループ㉛: #shortsは判定に不要(自動判定)。日本語ハッシュタグ2〜4個の行が方針
    tagline = re.search(r"^(#\S+(?:\s+#\S+)+)\s*$", smd, re.M)
    ntags = len(tagline.group(1).split()) if tagline else 0
    check("ハッシュタグ行2〜4個(日本語)", 2 <= ntags <= 4, f"{ntags}個")
    # 投資系は「投資助言ではありません」、制度系は「税務助言/推奨ではありません」等を許容
    check("免責文", bool(re.search(
        r"(助言|アドバイス)(では|でも)ありません|推奨(するもの|または否定するもの)?(では|でも)ありません", smd)))

    # 4. 出力mp4の機械検証
    mp4 = video_dir / "output" / next((p.name for p in (video_dir / "output").glob("*.mp4")), "none.mp4")
    if mp4.exists():
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
            capture_output=True, text=True).stdout.strip())
        if LONG:
            if dur < 480:
                warns.append(f"尺が8分未満({dur / 60:.1f}分)。ミッドロール広告は付かない")
                print(f"  [WARN] 尺 — {dur / 60:.1f}分(8分未満)")
            else:
                check("尺", True, f"{dur / 60:.1f}分")
        else:
            check("尺 60秒未満", dur < 60, f"{dur:.1f}s")
        vd = subprocess.run(["ffmpeg", "-i", str(mp4), "-af", "volumedetect", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
        m = re.search(r"mean_volume: ([-\d.]+) dB", vd)
        mean = float(m.group(1)) if m else -99
        check("平均音量 -18〜-11dB(≈-14LUFS)", -18 <= mean <= -11, f"{mean}dB")
        wh = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                             "-show_entries", "stream=width,height", "-of", "csv=p=0", str(mp4)],
                            capture_output=True, text=True).stdout.strip()
        want = "1920,1080" if LONG else "1080,1920"
        check(f"解像度 {want.replace(',', 'x')}", wh == want, wh)
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
