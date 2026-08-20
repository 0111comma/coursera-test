#!/usr/bin/env python3
"""S030: 銀行の100万円、置き場所でいくら変わるのか。

企画書は plan.md、数値は verify.py。
答え: 税引き後で年7172円、10年で7万1720円(普通0.4% vs 高い定期1.3%の水準)。

この人の欲求(yokkyu-map C: 無駄にしたくない):
  **給料の口座に置きっぱなしの100万円を、無駄にしたくない。**
維持の型(hold-rate-2026-08.md): カバーは「??円」、答えは82%地点、締めは問いに戻す。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402
import shortlib as _sl  # noqa: E402

_sl.set_accent("save")

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月の水準・100万円の場合"

SA_NEN, SA_10 = 7_172, 71_720
assert SA_NEN * 10 == SA_10

SCENES = {
    "toi": sc.card("この動画の問い", "いくら変わる?", "※ 100万円を1年置いた場合",
                   BADGE, BRAND, main_size=104, head_fs=32),
    "toi__cover": sc.cover("貯金100万円、置き場所でいくら変わる?", "??円",
                           "移すだけ。減る心配はない",
                           "2026年8月時点", BRAND),
    "futsu": sc.bars2("金利のちがい",
                      ("普通預金", 0.4, "年0.4%"),
                      ("高い定期預金", 1.3, "年1.3%"), BADGE, BRAND, ymax=1.6),
    "risoku": sc.bars2("1年の利息(税引き後)",
                       ("普通預金", 3.187, "3187円"),
                       ("高い定期預金", 10.359, "1万359円"), BADGE, BRAND, ymax=12),
    "sa": sc.card("置き場所だけの差", "年7172円", "※ 同じ100万円です",
                  BADGE, BRAND, main_size=110, head_fs=32,
                  ask="あなたはどこに置いてる?"),
    "matome": sc.hayami("置き場所で見る4つ",
                        [("普通預金", "3187円"), ("高い定期", "1万359円"),
                         ("1年の差", "7172円"), ("10年の差", "7万1720円")],
                        "※ 2026年8月の水準。金利は銀行と時期で変わります",
                        BADGE, BRAND, col1="どこに置くか", col2="利息(税引き後)", focal=3),
    "shime": sc.chips("預け先はどうやって選んだ?",
                      ["金利で比べた", "給料の口座のまま", "家から近い", "何となく"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "貯金100万円、置き場所でいくら変わる?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("toi", "給料の口座に、100万円があるとする。", anim=1.4, speed=1.05),
    Unit("toi", "口座の金利で、利息は変わるのだ。", anim=0.0, speed=1.05),
    Unit("futsu", "普通預金の金利は、年0.4%なのだ。", anim=1.6, speed=1.05),
    Unit("futsu", "0.4%なら利息は、年4000円。", anim=0.0, speed=1.05),
    Unit("futsu", "利息の税金を引くと、3187円になる。", anim=0.0, speed=1.05),
    Unit("risoku", "では定期預金に、移すとどうか。", anim=1.6, speed=1.05),
    Unit("risoku", "ネット銀行の定期預金は、年1.3%まである。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("risoku", "1.3%なら利息は、年1万3000円。", anim=0.0, speed=1.05),
    Unit("risoku", "税金を引いても、1万359円が残るのだ。", anim=0.0,
         face="happy", se="impact", se_at=0.30, speed=1.05, intonation=1.2),
    Unit("sa", "1万359円との差は、7172円なのだ。", anim=1.6,
         se="don", speed=1.05, intonation=1.25),
    Unit("sa", "1年で7172円の、置き場所の差なのだ。", anim=0.0, speed=1.05),
    Unit("matome", "7172円が10年積もると、どうなるか。", anim=1.6,
         face="surprised", speed=1.05, intonation=1.2),
    Unit("matome", "10年ぶんで、7万1720円になるのだ。", anim=0.0,
         face="surprised", speed=1.05, intonation=1.2),
    Unit("matome", "ただし定期預金のお金は、引き出しにくいのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("matome", "急に使うぶんは、普通預金に残すのだ。", anim=0.0, speed=1.05),
    Unit("shime", "100万円の置き場所、今日決めてみるのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S030.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
