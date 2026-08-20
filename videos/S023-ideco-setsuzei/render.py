#!/usr/bin/env python3
"""S023: iDeCoに月2万円入れると、税金は年にいくら減るのか。

企画書は plan.md、数値は verify.py。
答え: 年4万8504円。20年で97万円。しかも2026年12月から上限が上がる。

この人の欲求(yokkyu-map A: 取られたくない):
  **老後の備えもしたいが、いま払う税金は減らしたい。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402
import shortlib as _sl  # noqa: E402

_sl.set_accent("invest")  # カテゴリ色(docs/research/sakubun-gensoku.md とは別の画面施策)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・会社員で計算"

HERU = 48_504
assert HERU * 20 == 970_080

SCENES = {
    "toi": sc.card("この動画の問い", "いくら減る?", "※ 会社員の例です",
                   BADGE, BRAND, main_size=110, head_fs=32),
    "toi__cover": sc.cover("iDeCo月2万円、税金はいくら減る?", "48,504円",
                           "20年つづけると、97万円",
                           "2026年8月時点", BRAND),
    "kake": sc.card("この例の掛け金", "毎月2万円", "※ 60歳まで引き出せません",
                    BADGE, BRAND, main_size=128, head_fs=32),
    "zeiritsu": sc.bars2("引かれていた税",
                         ("所得税", 10.21, "10.21%"),
                         ("住民税", 10.0, "10%"), BADGE, BRAND, ymax=12),
    "heru": sc.card("毎年こう減る", "48504円", "※ 掛け金24万円 × 20.21%",
                    BADGE, BRAND, main_size=124, head_fs=32,
                    ask="あなたは年いくら払っている?"),
    "nijunen": sc.bars2("積み上がる節税",
                        ("20年ぶん", 97.0, "97万円"),
                        ("毎年ぶん", 4.85, "4万8504円"), BADGE, BRAND, ymax=115),
    "matome": sc.hayami("始める前に見る4つ",
                        [("毎年減る税金", "4万8504円"), ("20年ぶんなら", "97万円"),
                         ("いまの上限", "月2万3千円"), ("12月から", "月6万2千円")],
                        "※ 2026年8月時点。年収と控除の状況で税率は変わります",
                        BADGE, BRAND, col1="どこを見るか", col2="いくら", focal=1),
    "shime": sc.chips("老後の備え、何からがおすすめ?",
                      ["iDeCoから", "NISAから", "預金から", "まだ分からない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "老後の積立、税金はいくら減る?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("kake", "老後のための積立には、iDeCoがあるのだ。", anim=1.4, speed=1.05),
    Unit("kake", "iDeCoの掛け金は、全額が所得控除になる。", anim=0.0, speed=1.05),
    Unit("kake", "所得控除とは、税がかかる額を減らすもの。", anim=0.0, speed=1.05),
    Unit("zeiritsu", "たとえば毎月2万円を入れるとする。", anim=1.6, speed=1.05),
    Unit("zeiritsu", "つまり年24万円を、入れるのだ。", anim=0.0, speed=1.05),
    Unit("zeiritsu", "24万円ぶんに、税がかからなくなるのだ。", anim=0.0, speed=1.05),
    Unit("zeiritsu", "その税のうち所得税が、10.21%。", anim=0.0, speed=1.05),
    Unit("zeiritsu", "所得税に住民税の10%を、足すのだ。", anim=0.0, speed=1.05),
    Unit("zeiritsu", "住民税と足すと、20.21%になるのだ。", anim=0.0, speed=1.05),
    Unit("heru", "だから減る税金は、4万8504円。", anim=1.6,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("nijunen", "4万8504円を、20年つづけるとする。", anim=1.6, speed=1.05),
    Unit("nijunen", "すると減る税金は、97万円になるのだ。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("matome", "しかも入れられるのは、月2万3千円まで。", anim=1.6,
         speed=1.05),
    Unit("matome", "その2万3千円が、2026年12月に上がる。", anim=0.0, speed=1.05),
    Unit("matome", "会社員なら、月6万2千円まで入るのだ。", anim=0.0,
         face="happy", speed=1.05),
    Unit("matome", "ただし60歳まで、引き出せないのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("shime", "だから使う予定のないお金で、始めてほしい。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S023.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
