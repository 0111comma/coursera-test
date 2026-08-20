#!/usr/bin/env python3
"""S029: 10万円の買い物をリボにすると、総額いくらになるのか。

企画書は plan.md、数値は verify.py。
答え: 11万5795円。手数料だけで1万5795円、完済まで24ヶ月かかる。

この人の欲求(yokkyu-map A: 取られたくない):
  **手数料で取られたくない。知らないうちにリボになっているのが怖い。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・年15%は多くのカードの水準"

SOGAKU = 115_795
assert SOGAKU - 100_000 == 15_795

SCENES = {
    "toi": sc.card("この動画の問い", "総額いくら?", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, main_size=110, head_fs=32),
    "toi__cover": sc.cover("10万円の買い物、リボだと総額いくら?", "11万5795円",
                           "一括で払えば、手数料はゼロ",
                           "2026年8月時点", BRAND),
    "shikumi": sc.card("リボ払いとは", "毎月決まった額", "※ この例では毎月5000円",
                       BADGE, BRAND, main_size=92, head_fs=32),
    "tesu": sc.bars2("毎月の内わけ",
                     ("手数料", 1.25, "1250円"),
                     ("元が減る分", 3.75, "3750円"), BADGE, BRAND, ymax=4.4),
    "gokei": sc.bars2("払う総額",
                      ("一括払い", 10.0, "10万円"),
                      ("リボ払い", 11.58, "11万5795円"), BADGE, BRAND, ymax=13,
                      ),
    "kakan": sc.card("完済までの時間", "まる2年", "※ 毎月5000円の場合",
                     BADGE, BRAND, main_size=124, head_fs=32,
                     ask="あなたのカード、設定は一括?"),
    "matome": sc.hayami("リボで見る4つ",
                        [("手数料", "月1.25%"), ("完済まで", "まる2年"),
                         ("手数料の合計", "1万5795円"), ("一括払いなら", "ゼロ")],
                        "※ 2026年8月時点。10万円・毎月5000円の例です",
                        BADGE, BRAND, col1="どこを見るか", col2="いくら", focal=2),
    "shime": sc.chips("リボを避けるコツは?",
                      ["一括に固定する", "設定を毎回見る", "上限額を下げる", "カードを使わない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "10万円の買い物、リボだと総額いくら?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("shikumi", "たとえば10万円の買い物を、リボにする。", anim=1.4, speed=1.05),
    Unit("shikumi", "リボ払いは、毎月決まった額だけ払う方式。", anim=0.0, speed=1.05),
    Unit("shikumi", "そして毎月の支払いは、5000円とする。", anim=0.0, speed=1.05),
    Unit("tesu", "ただしリボには、手数料がかかるのだ。", anim=1.6,
         face="troubled", speed=1.05),
    Unit("tesu", "手数料の率は、いま月1.25%が多い。", anim=0.0, speed=1.05),
    Unit("tesu", "すると10万円の手数料は、月1250円。", anim=0.0,
         se="impact", se_at=0.30, speed=1.05, intonation=1.2),
    Unit("tesu", "だから5000円のうち、元が減るのは3750円。", anim=0.0, speed=1.05),
    Unit("kakan", "では完済まで続けると、どうなるのか。", anim=1.6, speed=1.05),
    Unit("kakan", "すると完済には、まる2年かかるのだ。", anim=0.0, speed=1.05),
    Unit("gokei", "2年ぶんの手数料は、1万5795円なのだ。", anim=1.6, speed=1.05),
    Unit("gokei", "1万5795円が、10万円に上乗せされるのだ。", anim=0.0,
         face="surprised", se="don", speed=1.05, intonation=1.25),
    Unit("gokei", "だから払うのは、あわせて11万5795円。", anim=0.0, speed=1.05),
    Unit("matome", "ちなみに一括払いなら、手数料はゼロ。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("matome", "つまり一括とくらべ、1万5795円高いのだ。", anim=0.0, speed=1.05),
    Unit("shime", "だから買う前に、支払いの方式を見てほしい。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S029.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
