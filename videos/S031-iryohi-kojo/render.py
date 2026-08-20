#!/usr/bin/env python3
"""S031: 医療費20万円、いくら戻ってくるのか。

企画書は plan.md、数値は verify.py。
答え: 所得税1万210円 + 翌年の住民税1万円 = 2万210円(所得税率10%の人の例)。

この人の欲求(yokkyu-map A: 取られたくない・取り戻したい):
  **払った病院代のうち、戻せるぶんを取り戻したい。**
維持の型(hold-rate-2026-08.md): カバーは「??円」、答えは69%地点、締めは問いに戻す。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402
import shortlib as _sl  # noqa: E402

_sl.set_accent("tax")

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・所得税率10%の場合"

MODORU, HERU, GOKEI = 10_210, 10_000, 20_210
assert MODORU + HERU == GOKEI

SCENES = {
    "toi": sc.card("この動画の問い", "いくら戻る?", "※ 所得税率10%の人の例です",
                   BADGE, BRAND, main_size=104, head_fs=32),
    "toi__cover": sc.cover("医療費20万円、いくら戻ってくる?", "??円",
                           "レシートを捨てる前に",
                           "2026年8月時点", BRAND),
    "hiku": sc.bars2("戻りの計算",
                     ("かかった医療費", 20.0, "20万円"),
                     ("対象になる額", 10.0, "10万円"), BADGE, BRAND, ymax=24),
    "modori": sc.bars2("戻る・減る(この例)",
                       ("所得税の戻り", 1.021, "1万210円"),
                       ("住民税の減り", 1.0, "1万円"), BADGE, BRAND, ymax=1.3),
    "gokei": sc.card("合わせると", "2万210円", "※ 家族のぶんを足した場合",
                     BADGE, BRAND, main_size=110, head_fs=32,
                     ask="あなたの家は、いくら戻る?"),
    "matome": sc.hayami("レシートで取り戻す4つ",
                        [("かかった医療費", "20万円"), ("引く額", "10万円"),
                         ("戻り+減り", "2万210円"), ("病院への交通費", "足してよい")],
                        "※ 所得税率10%の例。税率は人によって変わります",
                        BADGE, BRAND, col1="項目", col2="この例では", focal=2),
    "shime": sc.chips("レシートを貯めるコツ、何かある?",
                      ["封筒にためる", "アプリで撮る", "家計簿につける", "貯めてない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "医療費20万円、いくら戻ってくる?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("toi", "家族の医療費を、1年分足したとする。", anim=1.4, speed=1.05),
    Unit("toi", "1年で20万円なら、医療費控除の対象。", anim=0.0, speed=1.05),
    Unit("hiku", "医療費控除は、20万円から10万円を引いた額。", anim=1.6, speed=1.05),
    Unit("hiku", "引いて残る10万円に、所得税率を掛ける。", anim=0.0, speed=1.05),
    Unit("modori", "掛ける所得税率は、10.21%なのだ。", anim=1.6, speed=1.05),
    Unit("modori", "所得税率を掛けると、1万210円戻るのだ。", anim=0.0,
         face="happy", speed=1.05, intonation=1.2),
    Unit("modori", "1万210円のほかに、翌年の住民税も減る。", anim=0.0, speed=1.05),
    Unit("modori", "住民税の減りは、10万円の10%なのだ。", anim=0.0, speed=1.05),
    Unit("modori", "10%はこの例では、1万円になるのだ。", anim=0.0, speed=1.05),
    Unit("gokei", "1万210円と1万円、合計2万210円。", anim=1.6,
         se="don", speed=1.05, intonation=1.25),
    Unit("gokei", "2万210円が、医療費20万円から戻る額。", anim=0.0, speed=1.05),
    Unit("gokei", "ただし2万210円には、確定申告が要るのだ。", anim=0.0,
         face="troubled", se="impact", se_at=0.30, speed=1.05),
    Unit("matome", "確定申告には、レシートを使うのだ。", anim=1.6, speed=1.05),
    Unit("matome", "レシートには、病院への交通費も足せる。", anim=0.0,
         face="surprised", speed=1.05, intonation=1.2),
    Unit("shime", "今年の医療費、レシートで数えてみるのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S031.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
