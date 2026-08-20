#!/usr/bin/env python3
"""S020: ふるさと納税の2000円は、何回払うのか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  自己負担2000円は、寄付するたびに払うのか。
答え:
  年に1回だけ。だから寄付先を分けるほど、2000円は薄まる。

この人の欲求(yokkyu-map C: 無駄にしたくない):
  **せっかくやるなら、いちばん得な使い方をしたい。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・仮定の金額での計算"

JIKO = 2_000
assert 30_000 - JIKO == 28_000

SCENES = {
    "toi": sc.card("この動画の問い", "何回払うの?", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, main_size=110, head_fs=32),
    "toi__cover": sc.cover("ふるさと納税の2000円、何回払うの?", "年1回",
                           "分けるほど、2000円は薄まる",
                           "2026年8月時点", BRAND),
    "ichi": sc.bars2("1か所だけに寄付すると",
                     ("届く返礼品", 3.0, "3000円"),
                     ("自分で払う額", 2.0, "2000円"), BADGE, BRAND, ymax=3.6),
    "juu": sc.bars2("10か所に分けたとき",
                    ("届く返礼品", 30.0, "3万円"),
                    ("自分で払う額", 2.0, "2000円"), BADGE, BRAND, ymax=36),
    "usumaru": sc.card("寄付1万円あたりの負担", "200円まで下がる",
                       "※ 10か所に分けた場合", BADGE, BRAND,
                       main_size=76, head_fs=32,
                       ask="あなたは何か所に寄付した?"),
    "matome": sc.hayami("分け方でどう変わるか",
                        [("1か所だけ", "残るのは1000円"), ("10か所", "残るのは2万8000円"),
                         ("自分で払う額", "どちらも2000円"), ("上限を超えた分", "自腹")],
                        "※ 2026年8月時点。上限は年収と家族の人数で変わります",
                        BADGE, BRAND, col1="何か所に寄付するか", col2="どうなるか", focal=1),
    "shime": sc.chips("分けるときのコツは?",
                      ["定番から選ぶ", "時期をずらす", "家族で分ける", "まだやってない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "ふるさと納税の2000円、何回払うの?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("ichi", "たとえば自治体ひとつに、1万円を納める。", anim=1.4, speed=1.05),
    Unit("ichi", "その寄付に、返礼品が届くのだ。", anim=0.0, speed=1.05),
    Unit("ichi", "返礼品は寄付の3割までと、決まっている。", anim=0.0, speed=1.05),
    Unit("ichi", "つまり返礼品は、3000円ぶん届くのだ。", anim=0.0,
         speed=1.05),
    Unit("ichi", "そこから2000円を引くと、1000円ぶんが残る。", anim=0.0,
         speed=1.05),
    Unit("juu", "では10の自治体に、1万円ずつ納めると?", anim=1.6, speed=1.05),
    Unit("juu", "すると納めた額は、10万円になるのだ。", anim=0.0, speed=1.05),
    Unit("juu", "返礼品も10倍で、3万円ぶんが届く。", anim=0.0,
         face="happy", speed=1.05),
    Unit("juu", "でも自分で払う額は、2000円のままなのだ。", anim=0.0,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("usumaru", "だから残るのは、2万8000円ぶんになるのだ。", anim=1.6,
         se="don", speed=1.05, intonation=1.2),
    Unit("usumaru", "この2000円は、年に1回だけなのだ。", anim=0.0,
         speed=1.05),
    Unit("usumaru", "だから分けるほど、2000円は薄まるのだ。", anim=0.0,
         speed=1.05),
    Unit("matome", "1万円あたりで見ると、2000円が200円になる。", anim=1.6,
         speed=1.05),
    Unit("matome", "ただし上限を超えた分は、税から引かれない。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("matome", "超えた分は、まるごと自腹になるのだ。", anim=0.0, speed=1.05),
    Unit("shime", "だから今年は、分けて使ってほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S020.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
