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
  NISA系が検索流入の最大クラスタ(10回)。「nisa1800万円」の視聴率は129.1%。
  当初は「証券会社の変更」で企画したが、実測でニッチと分かったので差し替えた。
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
    "uru": sc.card("値上がりした投資信託", "売ってみる", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, main_size=104, head_fs=32),
    "uru__cover": sc.cover("NISAで売ると、枠はいくら戻る?", "100万円",
                           "150万円で売っても、戻るのは買った値段", "2026年8月時点", BRAND),
    "ne0": sc.bars2("買った値段と、売った値段",
                    ("買ったとき", 10.0, "100万円"),
                    ("売ったとき", 15.0, "150万円"), BADGE, BRAND, ymax=17),
    "ne1": sc.bars2("では、枠はいくら戻るのか",
                    ("売った値段", 15.0, "150万円"),
                    ("戻ってくる枠", 10.0, "100万円"), BADGE, BRAND, ymax=17),
    "itsu": sc.card("枠が戻る時期", "翌年", "※ 売った年には戻らない",
                    BADGE, BRAND, main_size=130, head_fs=32),
    "son": sc.bars2("値下がりして売った場合",
                    ("売った値段", 8.0, "80万円"),
                    ("戻ってくる枠", 10.0, "100万円"), BADGE, BRAND, ymax=13),
    "matome": sc.hayami("戻るのは、いつも買った値段のほう",
                        [("売った値段", "関係しない"), ("買った値段", "この分が戻る"),
                         ("戻る時期", "翌年"), ("年間の上限", "360万円")],
                        "※ 2026年8月時点。生涯投資枠1800万円・年間投資枠360万円",
                        BADGE, BRAND, col1="見るところ", col2="どうなるか", focal=1),
    "shime": sc.chips("あなたの持っている分は、いくらで買いましたか?",
                      ["100万円未満", "100〜300万円", "300万円以上", "調べていない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("uru", "積み立てた投資信託が、値上がりしたとする。", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.25),
    Unit("ne0", "たとえば100万円で買ったものが、150万円になった。", anim=1.6,
         speed=1.05),
    Unit("ne0", "そこで売ると、利益の50万円に税金はかからないのだ。", anim=0.0,
         speed=1.05),
    Unit("ne0", "でも売った後の枠が、思った額にならないのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("ne1", "まず戻ってくるのは、売った150万円ではないのだ。", anim=1.6,
         speed=1.05),
    Unit("ne1", "その戻る枠は、買ったときの100万円のほうなのだ。", anim=0.0,
         face="surprised", se="impact", se_at=0.32, speed=1.05, intonation=1.25),
    Unit("ne1", "だから差の50万円ぶんは、枠として戻らないのだ。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("itsu", "しかも戻るのは、売った年ではないのだ。", anim=1.4, speed=1.1),
    Unit("itsu", "その枠が使えるようになるのは、翌年からなのだ。", anim=0.0,
         speed=1.05),
    Unit("son", "ちなみに値下がりして売った場合は、逆になるのだ。", anim=1.6,
         speed=1.05),
    Unit("son", "その80万円で売っても、戻る枠は100万円のままなのだ。", anim=0.0,
         speed=1.05),
    Unit("matome", "つまり見るのは、売った値段ではなく買った値段。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("matome", "その買った値段が、翌年に戻ってくる枠になるのだ。", anim=0.0,
         speed=1.05),
    Unit("shime", "だから売る前に、いくらで買ったかを見てほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S016.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
