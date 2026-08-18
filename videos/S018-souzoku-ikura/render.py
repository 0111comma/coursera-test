#!/usr/bin/env python3
"""S018: 実家のタンス預金は、相続のときに調べられる。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  家に置いた現金を申告しなかったら、いくら余計に取られるのか。
答え:
  本来の税額に、最大40%が上乗せされる。100万円なら140万円。延滞税は別。

この人の欲求(yokkyu-map A: 取られたくない):
  **あとから余計に取られたくない。知らずに申告漏れになるのが怖い。**

ネタの根拠(demand-2026-08.md の実測):
  S007(タンス預金の20年後の価値)は検索流入が最多クラスタなのに視聴率4.2%、
  動画単体でも39.8%で7本中最下位。**流入はあるのに逃していた唯一の動画。**
  検索意図は「20年後の価値」ではなく「バレるのか」「いくら取られるのか」だった。

不安を煽る動画にしないため、**基礎控除で申告が要らない人が多いことを必ず言う。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・仮定の金額での計算"

HONRAI = 1_000_000
assert int(HONRAI * 0.40) == 400_000

SCENES = {
    "toi": sc.card("この動画の問い", "いくらから?", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, main_size=110, head_fs=32),
    "toi__cover": sc.cover("親の家、相続税はいくらからかかる?", "4,200万円",
                           "そこに、家にある現金も入る", "2026年8月時点", BRAND),
    "kiso": sc.card("かからない線", "3000万円から", "※ ここに人数ぶんを足します",
                    BADGE, BRAND, main_size=94, head_fs=32),
    "kiso_z": sc.bars2("この線を超えなければ",
                        ("かからない線", 4.2, "4200万円"),
                        ("これ以下", 4.2, "申告も不要"), BADGE, BRAND, ymax=6),
    "bareru": sc.card("調べられるもの", "口座の出入り", "※ 記録は銀行に残ります",
                      BADGE, BRAND, main_size=76, head_fs=32,
                      ask="あなたの実家は超える?"),
    "zei0": sc.bars2("正しく出した人と、隠した人",
                     ("正しく申告", 10.0, "100万円"),
                     ("隠していた場合", 10.0, ""), BADGE, BRAND, ymax=16),
    "zei1": sc.bars2("正しく出した場合と",
                     ("正しく申告", 10.0, "100万円"),
                     ("隠していた場合", 14.0, "140万円"), BADGE, BRAND, ymax=16),
    "dankai": sc.hayami("上乗せの段階",
                        [("うっかり漏れ", "少なめ"), ("申告していない", "中くらい"),
                         ("隠したと判断", "最大40%"), ("延滞税", "これとは別")],
                        "※ 2026年8月時点。財産額ではなく、税額にかかります",
                        BADGE, BRAND, col1="どう扱われるか", col2="上乗せ", focal=2),
    "shime": sc.chips("あなたの実家はどっち?",
                      ["だいたい知っている", "知らない", "無いと思う", "聞きにくい"],
                      BADGE, BRAND),
}

UNITS = [
    # 1ユニット目は、欲求を問いの形にして言う(ループ71)。
    # 前の版は「実家を片づけていたら、現金が出てきたとする」から入り、
    # そこから基礎控除・税務調査・加算税へ話が3つに割れていた。
    # ユーザー:「マジゴミだと思う。マジで何の話してるかわかんない」
    # 背骨を1本にした: **いくらから税金がかかるのか** → その線に何が入るのか。
    Unit("toi", "親の家、相続税はいくらからかかる?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("kiso", "その線は、3000万円から始まるのだ。", anim=1.4, speed=1.05),
    Unit("kiso", "そこに、ひとり600万円を足すのだ。", anim=0.0, speed=1.05),
    Unit("kiso_z", "だからふたりなら、4200万円までなのだ。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("kiso_z", "その中なら、申告そのものが要らないのだ。", anim=0.0,
         face="happy", speed=1.05),
    Unit("bareru", "でもその線は、家だけでは決まらないのだ。", anim=1.6,
         face="troubled", speed=1.05),
    Unit("bareru", "その線には、家にある現金も入るのだ。", anim=0.0, speed=1.05),
    Unit("bareru", "では家の現金は、どこまで分かるのだろうか。", anim=0.0, speed=1.05),
    Unit("bareru", "そこでは税務署が、亡くなった人の口座を見る。", anim=0.0,
         face="surprised", se="impact", se_at=0.28, speed=1.05, intonation=1.2),
    Unit("bareru", "しかも10年前まで、さかのぼれるのだ。", anim=0.0, speed=1.05),
    Unit("bareru", "だからその出金は、使い道を聞かれるのだ。", anim=0.0, speed=1.05),
    Unit("zei0", "では書かずにいた場合、いくら増えるのか。", anim=1.6, speed=1.05),
    Unit("zei1", "たとえばその税額が、100万円だとする。", anim=1.6, speed=1.05),
    Unit("zei1", "その税額に、最大40%が上乗せされるのだ。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("zei1", "だから140万円を、払うことになるのだ。", anim=0.0, speed=1.05),
    Unit("dankai", "ただし上乗せは、隠し方の悪さで変わるのだ。", anim=1.6, speed=1.05),
    Unit("shime", "だから実家の現金も、早めに数えてほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S018.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
