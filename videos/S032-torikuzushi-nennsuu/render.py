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

    # ---- 65歳の根拠(年金が始まる年齢)
    "kaishi": sf.hero("65歳", "年金が始まる年齢", name="02_point"),

    # ---- **途中式は画面に置いて、声は結果だけ**(2026-08-23のレビュー)
    #      割り算の過程を声に出すと、視聴者は計算につきあわされて退屈する。
    #      ただし**文字カードは図ではない**ので、帯と人の絵で見せる
    "kara": sf.timeline(65, 65 + 200 / 12, 90, "お金がある", "", show_gap=False,
                        empty_label="81歳", title="1000万円を毎月5万円ずつ"),

    # ---- 90歳の根拠。**男女ならべず、長いほうの1点に絞る**
    "seizon": sf.people(2, 1, "2人に1人", title="女性の場合"),
    "obi": sf.timeline(65, 65 + 200 / 12, 90, "お金がある", "貯金ゼロ 8年",
                       empty_label="81歳", title="90歳まで生きたら"),

    # ---- 上限と痛みを1つの棒で見せる(結果を2度言わない)
    "hikaku": sf.bars([("予定", 50000, "5万円"), ("使える額", 33000, "3万3000円")],
                      highlight=1, title="毎月の取り崩し額"),

    # ---- 持ち帰る式
    "kime": sf.person("02_point"),
    # 図はナレーションと同義にしない(Mayer 冗長性)。**道標として短く**
    "shiki": sf.formula("貯金額 ÷ 月数", "= 毎月使える額"),
    "cta2": sf.cta("", "02_point", show_comment=True),
}

UNITS = [
    # ---- カバー
    Unit("ie", "貯金1000万円。毎月5万円で何歳まで?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.2, chara="none"),

    # ---- 前提1: なぜ65歳からなのか(年金が始まる年齢)
    Unit("kaishi", "年金が始まる【65歳】から、貯金を毎月5万円使います。", anim=1.2,
         speed=1.05, chara="none"),

    # ---- 答えだけ。割り算は画面の「1000万円 ÷ 毎月5万円」が見せる
    Unit("kara", "【81歳】で、その貯金が底をつきます。", anim=1.2,
         se="don", speed=1.0, intonation=1.2, chara="none"),
    Unit("kara", "【貯金】がゼロのあと、生活費はどうしますか?", anim=0.0,
         speed=1.05, pad=0.3, chara="none"),

    # ---- 前提2: なぜ90歳まで考えるのか(厚労省 令和7年簡易生命表)
    Unit("seizon", "いま【90歳】まで生きる女性は、2人に1人です。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("obi", "貯金はゼロ。【90歳】までの【8年】は年金だけ。", anim=1.2,
         se="impact", se_at=0.2, speed=1.0, intonation=1.2, pad=0.35, chara="none"),

    # ---- **結果は1度だけ言う。**そのまま痛みへ繋ぐ(2026-08-23のレビュー)
    Unit("hikaku", "90歳まで持たせるなら、使えるのは毎月【3万3000円】。", anim=1.2,
         se="don", speed=1.0, intonation=1.2, chara="none"),
    Unit("hikaku", "予定より毎月【1万7000円】、暮らしを削ることになります。", anim=0.0,
         se="impact", se_at=0.25, speed=1.0, intonation=1.2, pad=0.4, chara="none"),

    # ---- 結論と方法を1行ずつ
    Unit("kime", "決めるのは金額ではなく、持たせる【年齢】です。", anim=1.2,
         se="don", speed=1.05, chara="none"),
    Unit("shiki", "その【年齢】を月数にして、貯金額を割るだけです。", anim=1.2,
         speed=1.05, chara="none"),

    # ---- **安心**。恐怖と同じ言葉(通帳)で返す
    Unit("shiki", "こうすれば、【貯金】が途中で尽きません。", anim=0.0,
         speed=1.05, pad=0.3, chara="none"),

    # ---- 締めは1行。**問いとお願いを分けない**
    Unit("cta2", "あなたの貯金は何歳まで?コメントで教えてください。", anim=1.2,
         speed=1.05, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S032.mp4", speaker=14, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
