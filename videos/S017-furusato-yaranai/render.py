#!/usr/bin/env python3
"""S017: ふるさと納税をやらないと、年にいくら損しているのか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  やっていない人は、1年でいくらぶんを取り逃がしているのか。
答え:
  年収500万円・独身の目安で 約1万6千円。10年やらなければ16万円。

この人の欲求(yokkyu-map A: 取られたくない / C: 無駄にしたくない):
  **面倒でやっていない。でも、やらないことの値段は知っておきたい。**

S005(公開済み・視聴率79.2%)との違い:
  S005 は「**なぜ実質2000円なのか**」という仕組みの話。
  この動画は「**やらない人が1年でいくら取り逃がしているか**」という金額の話。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・年収500万円独身の目安"

JOGEN, HENREI, JIKO = 60_000, 18_000, 2_000
assert HENREI - JIKO == 16_000

SCENES = {
    "toi": sc.card("この動画の問い", "年いくら損?", "※ 年収500万円・独身の目安です",
                   BADGE, BRAND, main_size=110, head_fs=32),
    "toi__cover": sc.cover("ふるさと納税、やらないと年いくら損?", "1万6千円",
                           "10年やらなければ、16万円",
                           "2026年8月時点", BRAND),
    "jogen": sc.card("この人が出せる目安", "6万円", "※ 年収と家族の人数で変わります",
                     BADGE, BRAND, main_size=128, head_fs=32),
    "nagare": sc.bars2("6万円を出したとき",
                       ("税から引かれる", 5.8, "5万8千円"),
                       ("じぶんの持ち出し", 0.2, "2千円"), BADGE, BRAND, ymax=7),
    "henrei": sc.card("そのとき届くもの", "1万8千円ぶん", "※ 品物は自治体が選んでいます",
                      BADGE, BRAND, main_size=94, head_fs=32,
                      ask="あなたは今年、やりましたか?"),
    "sashi": sc.bars2("差し引きすると",
                      ("届いたもの", 1.8, "1万8千円"),
                      ("持ち出し", 0.2, "2千円"), BADGE, BRAND, ymax=2.4),
    "matome": sc.hayami("やらないと消える額",
                        [("1年", "1万6千円"), ("10年", "16万円"),
                         ("月あたり", "1333円"), ("税金の総額", "変わらない")],
                        "※ 2026年8月時点。年収500万円・独身の目安です",
                        BADGE, BRAND, col1="どのくらいの期間", col2="いくら消えるか",
                        focal=1),
    "shime": sc.chips("あなたは今年やった?",
                      ["もうやった", "これからやる", "毎年やらない", "知らなかった"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "ふるさと納税、やらないと年いくら損?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("jogen", "たとえば年収500万円で、独身だとする。", anim=1.4, speed=1.05),
    Unit("jogen", "その人が出せる目安は、6万円なのだ。", anim=0.0, speed=1.05),
    Unit("nagare", "その6万円を、出したとするのだ。", anim=1.6, speed=1.05),
    Unit("nagare", "するとそのうち5万8千円が、税から引かれる。", anim=0.0, speed=1.05),
    Unit("nagare", "だから持ち出しは、2千円だけなのだ。", anim=0.0, speed=1.05),
    Unit("henrei", "そしてお礼に、返礼品が届くのだ。", anim=1.6, speed=1.05),
    Unit("henrei", "その返礼品は、寄付した額の3割まで。", anim=0.0, speed=1.05),
    Unit("henrei", "だから6万円なら、1万8千円ぶんになるのだ。", anim=0.0,
         face="happy", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("sashi", "だから差し引きで、1万6千円が残るのだ。", anim=1.6,
         se="don", speed=1.05, intonation=1.2),
    Unit("sashi", "これをやらないと、その分が消えるのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("matome", "しかもこれを10年やらないと、どうなるか。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("matome", "その10年ぶんは、16万円になるのだ。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("matome", "ただし払う税金そのものは、減っていない。", anim=0.0, speed=1.05),
    Unit("matome", "その税金は、払う先が変わるだけなのだ。", anim=0.0, speed=1.05),
    Unit("matome", "だから返礼品のぶんだけ、まるごと得なのだ。", anim=0.0, speed=1.05),
    Unit("shime", "だから今年ぶんだけでも、出してほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S017.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
