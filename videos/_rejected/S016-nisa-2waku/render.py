#!/usr/bin/env python3
"""S016: つみたて投資枠と成長投資枠、どっちで積み立てるのか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  毎月の積立を、どちらの投資枠で設定すればいいのか。
答え:
  月10万円までなら、つみたて投資枠だけでいい。
  そこを超えたい月だけ、成長投資枠を足す。

この人の欲求(yokkyu-map B: 大きな選択を間違えたくない):
  **積立を増やしたい。でも設定を選び間違えたくない。**
  欲求マップ B の note のとおり、**判定を1つの数字に落とす**。ここでは月10万円。

作り直しの経緯(ループ71のユーザー指摘):
  前の版は「売ったら投資枠はいくら戻るか」だった。
  ユーザー:「だから何って思う。これはどの欲求に訴求している動画なの?」
  そのとおりで、簿価で戻ることの損得は**1800万円を使い切りそうな人にしか発生しない**。
  しかも視聴者は売っていない。積み立てている最中で、
  demand-2026-08.md 自身が書いた「視聴者がいま実際にやっていること」を外していた。
  仕組み(簿価・翌年復活)から入って視聴者を後から貼りつけた形だった。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点の制度・仮定の金額での計算"

TSUMITATE_YEAR, SEICHO_YEAR = 1_200_000, 2_400_000
assert TSUMITATE_YEAR // 12 == 100_000
assert (TSUMITATE_YEAR + SEICHO_YEAR) // 12 == 300_000

SCENES = {
    # 入口は日常語。「投資枠」は3ユニット目でその場で意味を言う
    "toi": sc.card("この動画の問い", "月いくらまで?", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, main_size=104, head_fs=32),
    "toi__cover": sc.cover("NISAの積立、月いくらまで入る?", "10万円",
                           "超えたい月だけ、成長投資枠を足す",
                           "2026年8月時点", BRAND),
    "kabe": sc.card("ここで止まる", "月10万円", "※ 年120万円を12で割った額",
                    BADGE, BRAND, main_size=124, head_fs=32),
    "futatsu": sc.bars2("1年で入れられる額",
                        ("つみたて投資枠", 12.0, "120万円"),
                        ("成長投資枠", 24.0, "240万円"), BADGE, BRAND, ymax=27),
    "gokei": sc.card("2つを合わせると", "月30万円", "※ 2つの投資枠を合わせた額",
                     BADGE, BRAND, main_size=124, head_fs=32,
                     ask="あなたの積立は、月10万円を超えますか?"),
    "shogai": sc.bars2("一生ぶんの1800万円",
                       ("成長投資枠で入る分", 12.0, "1200万円"),
                       ("つみたて投資枠の分", 6.0, "600万円"), BADGE, BRAND, ymax=14),
    "matome": sc.hayami("設定を決める4つ",
                        [("月10万円まで", "つみたて投資枠"), ("それを超える分", "成長投資枠"),
                         ("同じ商品", "どちらでも設定できる"), ("成長投資枠の上限", "1200万円")],
                        "※ 2026年8月時点。金額はすべて仮定の例です",
                        BADGE, BRAND, col1="いくら積み立てるか", col2="どちらで設定するか",
                        focal=0),
    "shime": sc.chips("いまの積立額は?",
                      ["月10万円未満", "ちょうど10万円", "超えている", "これから始める"],
                      BADGE, BRAND),
}

UNITS = [
    # 1ユニット目は、欲求を問いの形にして言う(ループ71のユーザー指摘)。
    #   「最初の1、2秒で、どの欲望に訴求してるのかを質問として言語化しろ」
    Unit("toi", "NISAの積立、月いくらまで入る?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("kabe", "その上限は、つみたて投資枠で決まるのだ。", anim=1.4, speed=1.05),
    Unit("kabe", "その投資枠とは、1年に買える上限のこと。", anim=0.0, speed=1.05),
    Unit("futatsu", "つみたて投資枠は、いま年120万円なのだ。", anim=1.6, speed=1.05),
    Unit("futatsu", "だから月にすると、10万円になるのだ。", anim=0.0, speed=1.05),
    Unit("futatsu", "では、それ以上は入れられないのか。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("futatsu", "実はもうひとつ、成長投資枠があるのだ。", anim=0.0,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("futatsu", "その成長投資枠は、年240万円なのだ。", anim=0.0, speed=1.05),
    Unit("gokei", "しかも同じ商品を、そこでも積み立てられる。", anim=1.6,
         speed=1.05),
    Unit("gokei", "だから合わせると、月30万円まで入るのだ。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("shogai", "でも一生ぶんの1800万円には、内訳がある。", anim=1.6,
         face="troubled", speed=1.05),
    Unit("shogai", "その成長投資枠は、1200万円まで。", anim=0.0, speed=1.05),
    Unit("shogai", "だから残りの600万円は、つみたて投資枠の分。", anim=0.0,
         speed=1.05),
    Unit("matome", "つまり月10万円までなら、つみたて投資枠だけ。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("matome", "そこを超えたい月だけ、成長投資枠を足すのだ。", anim=0.0,
         speed=1.05),
    Unit("shime", "だから今の積立額を見て、決めてほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S016.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
