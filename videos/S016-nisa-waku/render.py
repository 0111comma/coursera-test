#!/usr/bin/env python3
"""S016: NISAは売っても、枠がその年には戻らない。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  NISAで売ったら、枠はいつ、いくら戻るのか。
答え:
  その年には戻らない。翌年に、買った値段のぶんだけ戻る。
  100万円で買って150万円で売っても、戻るのは100万円ぶん。

この人の欲求(yokkyu-map C: 無駄にしたくない):
  **NISAの枠を無駄にしたくない。売ったせいで枠が減るなら、売り方を考えたい。**

ネタの根拠(demand-2026-08.md の実測):
  NISA系が検索流入の最大クラスタ。S003(NISA枠1800万)は視聴率64.1%。
  上位3本の共通点は「視聴者がいま実際にやっていること」で、枠を埋めている途中の人に当たる。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・仮定の金額での計算"

BOKA, URINE = 1_000_000, 1_500_000
assert URINE - BOKA == 500_000

SCENES = {
    # 入口は日常語。「NISA」「投資信託」は2文目以降で出す
    "fueta": sc.card("株や投資信託の積立が", "増えていた", "※ 金額はすべて仮定の例です",
                     BADGE, BRAND, main_size=104, head_fs=32),
    "fueta__cover": sc.cover("NISAで売ると、枠はいくら戻る?", "100万円",
                             "150万円で売っても、戻るのは買った値段", "2026年8月時点", BRAND),
    "ne0": sc.bars2("その年に売った1本",
                    ("買ったとき", 10.0, "100万円"),
                    ("売ったとき", 15.0, "150万円"), BADGE, BRAND, ymax=17),
    "ne1": sc.bars2("売った後、枠はどちらの額で戻るか",
                    ("売った値段", 15.0, "150万円"),
                    ("戻ってくる枠", 10.0, "100万円"), BADGE, BRAND, ymax=17),
    "itsu": sc.card("枠が使えるのは", "翌年から", "※ 1月1日にまとめて空く",
                    BADGE, BRAND, main_size=118, head_fs=32),
    "son": sc.bars2("売値のほうが低い年",
                    ("売った値段", 8.0, "80万円"),
                    ("戻ってくる枠", 10.0, "100万円"), BADGE, BRAND, ymax=13),
    "matome": sc.hayami("売る前に見る4つ",
                        [("売った値段", "関係しない"), ("買った値段", "この分が戻る"),
                         ("使えるのは", "翌年から"), ("年間の上限", "360万円")],
                        "※ 2026年8月時点。取得価額(簿価)ベースで戻ります",
                        BADGE, BRAND, col1="見るところ", col2="どうなるか", focal=1),
    "shime": sc.chips("取得価額は、証券会社の画面で見られます",
                      ["すぐ言える", "調べれば分かる", "分からない", "まだ売らない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("fueta", "貯金のつもりで積み立てた株が、増えていたとする。", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.25),
    Unit("fueta", "その積み立てに、NISAを使っていたとするのだ。", anim=1.4, speed=1.05),
    Unit("ne0", "たとえば100万円で、買っていたとするのだ。", anim=1.6,
         speed=1.05),
    Unit("ne0", "そしてそれが、150万円になったとする。", anim=0.0,
         speed=1.05),
    Unit("ne0", "そこで売っても、増えた分に税金はかからないのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("ne1", "まず戻ってくるのは、売った150万円ではないのだ。", anim=1.6,
         speed=1.05),
    Unit("ne1", "その枠は、買ったときの100万円のほうで戻るのだ。", anim=0.0,
         face="surprised", se="impact", se_at=0.32, speed=1.05, intonation=1.25),
    Unit("ne1", "だから差の50万円ぶんは、枠として返ってこないのだ。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("itsu", "しかも使えるようになるのは、売った年ではないのだ。", anim=1.4,
         speed=1.05),
    Unit("itsu", "その枠が空くのは、翌年になってからなのだ。", anim=0.0, speed=1.05),
    Unit("son", "ちなみに値下がりして売ると、逆のことが起きるのだ。", anim=1.6,
         speed=1.05),
    Unit("son", "その80万円で売っても、戻る枠は100万円のままなのだ。", anim=0.0,
         speed=1.05),
    Unit("matome", "つまり枠を決めているのは、買ったときの値段なのだ。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("matome", "そして年間の上限は、いま360万円までなのだ。", anim=0.0,
         speed=1.05),
    Unit("shime", "だから売る前に、いくらで買ったかを見てほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S016.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
