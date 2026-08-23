#!/usr/bin/env python3
"""S032: 1000万円を月5万ずつ取り崩すと、何歳で尽きるのか。

新デザイン1本目(自前キャラ・明るい背景・冥鳴ひまり)。
型は competitor-shorts-teardown-2026-08-23.md の分解にもとづく:
  0〜5% カバー / 5〜73% 本編 / 73〜76% 結論 / 76〜100% CTA
  1カット1.6〜1.8秒。表は出しっぱなしにして**赤枠を1行ずつ動かす**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

TITLE = "1000万円を毎月5万円ずつ使うと?"
BADGE = "※ 運用しない場合の計算。物価の変動は考えていません"
F.use_fp_theme(TITLE, speaker=14,
               badge=BADGE)      # 冥鳴ひまり

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

# 台本に出す値は verify.py と一致していること(ズレたらここで落ちる)
assert V.MONTHS_0 == 200 and (V.EMPTY_Y, V.EMPTY_M) == (81, 8)
assert V.GAP_MONTHS == 8 * 12 + 4          # 90歳まで 8年4か月 足りない
assert V.CAP_0 == 33_000 and V.CUT == 17_000
assert V.CAP[0.03] == 47_000

SCENES = {
    "ie": sf.person("01_base"),
    "ie__cover": sf.cover("老後のお金、どこまで使える?", "1000万円を毎月5万円ずつ", "何歳まで持つ?"),

    # ---- 65歳の根拠(年金が始まる年齢)を、数字と同じ画面に出す
    "kaishi": sf.hero("65歳", "年金が始まる年齢", name="02_point"),

    # ---- 割り算を一段ずつ。表は出しっぱなしで赤枠を動かす
    "keisan0": sf.table(["", ""],
                        [("1000万円 ÷ 5万円", "200か月"), ("200か月", "16年8か月")],
                        highlight=0, title="毎月5万円ずつ使うと"),
    "keisan1": sf.table(["", ""],
                        [("1000万円 ÷ 5万円", "200か月"), ("200か月", "16年8か月")],
                        highlight=1, title="毎月5万円ずつ使うと"),
    "kara": sf.hero("81歳8か月", "65歳 + 16年8か月", name="04_surprised"),

    # ---- 90歳の根拠(厚労省 令和7年簡易生命表)
    "seizon": sf.bars([("男性", 26.7, "4人に1人"), ("女性", 50.8, "2人に1人")],
                      highlight=0, title="90歳まで生きる人"),
    "seizon2": sf.bars([("男性", 26.7, "4人に1人"), ("女性", 50.8, "2人に1人")],
                       highlight=1, title="90歳まで生きる人"),
    # 目盛は **81歳8か月**。82歳に丸めると、声「81歳8か月」と食い違う
    "obi": sf.timeline(65, 65 + 200 / 12, 90, "お金がある", "8年4か月 空",
                       empty_label="81歳8か月", title="90歳まで生きたら"),

    # ---- 上限もまた割り算1回
    "keisan2": sf.table(["", ""],
                        [("90歳までの月数", "300か月"), ("毎月使える額", "3万3000円")],
                        highlight=0, title="貯金1000万円を90歳まで"),
    "keisan3": sf.table(["", ""],
                        [("90歳までの月数", "300か月"), ("毎月使える額", "3万3000円")],
                        highlight=1, title="貯金1000万円を90歳まで"),
    "hikaku": sf.bars([("つもり", 50000, "5万円"), ("使える額", 33000, "3万3000円")],
                      highlight=1, title="毎月の取り崩し額"),

    # ---- 持ち帰る式
    "kime": sf.person("02_point"),
    "shiki": sf.formula("貯金 ÷ 持たせたい月数", "= 毎月使っていい額"),
    "toi2": sf.person("01_base"),
    "cta2": sf.cta("", "02_point", show_button=True),
}

UNITS = [
    # ---- カバー
    Unit("ie", "貯金1000万円。毎月5万円で何歳まで?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.2, chara="none"),

    # ---- 前提1: なぜ65歳からなのか(年金が始まる年齢)
    Unit("kaishi", "年金が始まる【65歳】から、毎月5万円ずつ使います。", anim=1.2,
         speed=1.05, chara="none"),

    # ---- 割り算1回。**声は丸め、画面は正確なまま**(端数の連続は聞き手を置いていく)
    Unit("keisan0", "1000万円を5万円で割ると、【200か月】。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("keisan1", "200か月は、【16年】以上です。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("kara", "65歳に【16年】を足すと、【81歳】をすぎます。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("kara", "【81歳】で貯金が底をつきます。足りますか?", anim=0.0,
         se="don", speed=1.0, intonation=1.2, pad=0.3, chara="none"),

    # ---- 前提2: なぜ90歳まで考えるのか(厚労省 令和7年簡易生命表)
    Unit("seizon", "いま【90歳】まで生きる人は、男性の4人に1人。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("seizon2", "女性なら、【2人に1人】が90歳まで。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("obi", "90歳まで生きたら、【8年】以上も足りません。", anim=1.2,
         se="impact", se_at=0.2, speed=1.0, intonation=1.2, pad=0.3, chara="none"),

    # ---- 上限もまた割り算1回
    Unit("keisan2", "65歳から90歳までは、【300か月】。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("keisan3", "1000万円を300か月で割ると、【3万3000円】。", anim=1.2,
         se="don", speed=1.0, intonation=1.2, chara="none"),

    # ---- 痛みは金額の差ではなく、**暮らしがどうなるか**で言う
    Unit("hikaku", "毎月5万円のつもりが、使えるのは【3万3000円】。", anim=1.2,
         speed=1.0, chara="none"),
    Unit("hikaku", "毎月【1万7000円】ぶん、暮らしが縮みます。", anim=0.0,
         se="impact", se_at=0.25, speed=1.0, pad=0.35, chara="none"),

    # ---- 結論は1行に圧縮する(「金額ではない」を2回言わない)
    Unit("kime", "決めるのは【金額】ではなく、【何歳まで】です。", anim=1.2,
         se="don", speed=1.05, chara="none"),

    # ---- 持ち帰る式。「月数」は耳で引っかかるので言わない
    Unit("shiki", "何歳までかが決まれば、【何か月】かが決まります。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("shiki", "貯金を、その【何か月】かで割ります。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("toi2", "あなたの貯金は、何歳まで持たせますか?", anim=1.2,
         speed=1.05, chara="none"),

    # ---- CTA。**視聴者が次に何を得られるか**を名指しする
    Unit("cta2", "【2000万円】の貯金なら? 登録して次の動画へ。", anim=1.2,
         speed=1.05, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S032.mp4", speaker=14, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
