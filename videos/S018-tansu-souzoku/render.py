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
    "genkin": sc.card("実家を片づけたら", "現金が出てきた", "※ 金額はすべて仮定の例です",
                      BADGE, BRAND, main_size=88, head_fs=32),
    "genkin__cover": sc.cover("家の現金、黙っていたらどうなる?", "1.4倍",
                              "本来の税額に、最大40%が上乗せ", "2026年8月時点", BRAND),
    "kiso_z": sc.bars2("無税で通る額",
                        ("線引きの額", 4.2, "4200万円"),
                        ("それ以下", 4.2, "かからない"), BADGE, BRAND, ymax=6),
    "kiso": sc.card("申告が要る人", "多くない", "※ 法定相続人の数で線が動きます",
                    BADGE, BRAND, main_size=110, head_fs=32),
    "bareru": sc.card("調べられるもの", "口座の出入り", "※ 通帳を捨てても記録は残ります",
                      BADGE, BRAND, main_size=76, head_fs=32),
    "zei0": sc.bars2("正しく出した人と、隠した人",
                     ("正しく申告", 10.0, "100万円"),
                     ("隠していた場合", 10.0, ""), BADGE, BRAND, ymax=16),
    "zei1": sc.bars2("本来の税額が100万円だとすると",
                     ("正しく申告", 10.0, "100万円"),
                     ("隠していた場合", 14.0, "140万円"), BADGE, BRAND, ymax=16),
    "dankai": sc.hayami("上乗せの段階",
                        [("うっかり漏れ", "少なめ"), ("申告していない", "中くらい"),
                         ("隠したと判断", "最大40%"), ("延滞税", "これとは別")],
                        "※ 2026年8月時点。財産額ではなく、税額にかかります",
                        BADGE, BRAND, col1="どう扱われるか", col2="上乗せ", focal=2),
    "shime": sc.chips("実家の現金、いくらあるか知っていますか?",
                      ["だいたい知っている", "知らない", "無いと思う", "聞きにくい"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("genkin", "実家を片づけていたら、現金が出てきたとする。", anim=1.0,
         cover=True, se="pop", speed=1.05, intonation=1.25),
    Unit("genkin", "その現金は、黙っていてもいいのだろうか。", anim=1.4,
         face="troubled", speed=1.05),
    Unit("kiso", "まず、ほとんどの人は申告そのものが要らないのだ。", anim=1.4,
         speed=1.05),
    Unit("kiso", "その線引きは、3000万円に人数ぶんを足した額なのだ。", anim=0.0,
         speed=1.05),
    Unit("kiso_z", "だから4200万円までは、かからない家が多いのだ。",
         anim=1.6, speed=1.05),
    Unit("bareru", "でもその線を超えると、話が変わるのだ。", anim=1.4, speed=1.05),
    Unit("bareru", "その税務署は、亡くなった人の口座の出入りを見られるのだ。", anim=0.0,
         speed=1.05),
    Unit("bareru", "しかも10年前まで、さかのぼれるのだ。", anim=0.0,
         face="surprised", se="impact", se_at=0.28, speed=1.05, intonation=1.2),
    Unit("bareru", "だからその記録にある大きな出金は、使い道を聞かれるのだ。", anim=0.0,
         speed=1.05),
    Unit("zei0", "では隠していた場合、いくら増えるのか。", anim=1.6, speed=1.05),
    Unit("zei0", "たとえばその税額が、100万円だとするのだ。", anim=0.0, speed=1.05),
    Unit("zei1", "その税額に、最大40%が上乗せされるのだ。", anim=1.6,
         se="don", speed=1.05, intonation=1.25),
    Unit("zei1", "だから140万円を、払うことになるのだ。", anim=0.0, speed=1.05),
    Unit("dankai", "ただしその上乗せは、隠し方の悪さで変わるのだ。", anim=1.6,
         speed=1.05),
    Unit("dankai", "そして遅れた日数ぶんの延滞税も、別にかかるのだ。", anim=0.0,
         speed=1.05),
    Unit("shime", "だから実家の現金は、早めに数えておいてほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S018.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
