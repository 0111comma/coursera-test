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
    "jogen": sc.card("年収500万円・独身なら", "上限6万円", "※ 年収と家族の人数で変わります",
                     BADGE, BRAND, main_size=104, head_fs=32),
    "nagare": sc.bars2("6万円を出したとき",
                       ("税から引かれる", 5.8, "5万8千円"),
                       ("自分で払う額", 0.2, "2千円"), BADGE, BRAND, ymax=7),
    "henrei": sc.card("お米・肉・果物など", "1万8千円ぶん", "※ 品物は自治体が選んでいます",
                      BADGE, BRAND, main_size=94, head_fs=32,
                      ask="あなたは今年、やりましたか?"),
    "sashi": sc.bars2("差し引きすると",
                      ("届いたもの", 1.8, "1万8千円"),
                      ("自分で払った額", 0.2, "2千円"), BADGE, BRAND, ymax=2.4),
    "matome": sc.hayami("やらないと消える額",
                        [("1年", "1万6千円"), ("10年", "16万円"),
                         ("月あたり", "1333円"), ("税金の総額", "変わらない")],
                        "※ 2026年8月時点。年収500万円・独身の目安です",
                        BADGE, BRAND, col1="どのくらいの期間", col2="いくら消えるか",
                        focal=1),
    "shime": sc.chips("おすすめの返礼品は?",
                      ["お米", "肉や魚", "果物", "日用品"],
                      BADGE, BRAND),
}

UNITS = [
    # ループ71のユーザー指摘をそのまま反映した組み直し:
    #   ・「その人が出せる目安」→ 年収500万円なら上限は6万円と**決まっている**
    #   ・「6万円を出したとする」→ ふるさと納税で**納めた**
    #   ・「持ち出し」→ **自分で払う額**
    #   ・「お礼に返礼品が届く」→ 重言(お礼=返礼)。「返礼品が届く」だけにする
    #   ・「差し引きで1万6千円が残る」→ **誰の手元に**残るのかを書く
    #   ・「これをやらないと、その分が消える」→ 指示語が続いて何の話か分からない
    #   ・「しかもこれを10年やらないと」→「もし10年間、〜しなかったら?」
    #   ・指示語は1本で4回まで(ここでは2回)
    Unit("toi", "ふるさと納税、やらないと年いくら損?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("jogen", "たとえば年収500万円の人の、上限を見る。", anim=1.4,
         speed=1.05),
    Unit("jogen", "ふるさと納税に使える上限が、6万円。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("nagare", "その6万円を、ふるさと納税で納める。", anim=1.6, speed=1.05),
    Unit("nagare", "すると5万8千円が、税から引かれる。", anim=0.0, speed=1.05),
    Unit("nagare", "だから自分で払うのは、2千円だけ。", anim=0.0, speed=1.05),
    Unit("henrei", "そのかわり、返礼品が届くのだ。", anim=1.6,
         face="happy", speed=1.05),
    Unit("henrei", "返礼品は、寄付した6万円の3割まで。", anim=0.0,
         speed=1.05),
    Unit("henrei", "つまり6万円なら、返礼品は1万8千円ぶん。", anim=0.0,
         se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("henrei", "返礼品はお米や肉、果物や日用品。", anim=0.0,
         speed=1.05),
    Unit("sashi", "返礼品から2千円を引くと、1万6千円ぶん。", anim=1.6,
         se="don", speed=1.05, intonation=1.2),
    Unit("sashi", "やらない人は、1万6千円を逃している。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("matome", "もし10年間、ふるさと納税をしなかったら?", anim=1.6, speed=1.05),
    Unit("matome", "もらえない額は10年で、16万円。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("matome", "ただし払う税金は、減っていない。", anim=0.0, speed=1.05),
    Unit("matome", "税金は、払う先が変わるだけなのだ。", anim=0.0, speed=1.05),
    Unit("matome", "だから返礼品のぶんだけ、得になる。", anim=0.0, speed=1.05),
    Unit("shime", "なお上限は、年収と家族で変わる。", anim=1.4, speed=1.05),
    Unit("shime", "だから今年のうちに、上限を調べてほしい。", anim=0.0,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S017.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
