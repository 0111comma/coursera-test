#!/usr/bin/env python3
"""S014: 気づかず払う手数料ワースト3(T5ワースト型)。数値はverify.pyとassert照合。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "大手銀行の例・2026年8月時点"

assert 220 * 52 == 11_440, "verify.pyと不一致"
assert int(11_440 / 0.0040) == 2_860_000, "verify.pyと不一致"
assert 990 - 110 == 880, "verify.pyと不一致"


SCENES = {
    "hero_count": sc.hero_count(11_440, "{:,}円", BADGE, BRAND, size=112,
                                lead="その手数料、1年でいくら?"),
    "hero_count__cover": sc.cover("その手数料、1年でいくら?", "年1万1440円", "ワースト3を数えたら",
                                  "週1のコンビニATMの場合", BRAND, main_size=96),
    "hero_full": sc.hero("年1万1440円", "週1のコンビニATMだけで(220円×52回)", BADGE, BRAND,
                         size=96, sub_fs=28),
    "intro": sc.card("今日の数字", "手数料ワースト3", "(ありがち順・このチャンネル調べ)", BADGE, BRAND,
                     main_size=54),
    "w3": sc.card("3位: 振込手数料", "窓口だと最大990円", "(他行宛て。改定で値上がり傾向)", BADGE, BRAND,
                  main_size=52),
    "w3b": sc.card("同じ振込でも", "アプリなら110円〜", "(窓口との差、最大880円)", BADGE, BRAND,
                   main_size=52),
    "w2": sc.card("2位: 時間外手数料", "夜のATMは110円〜", "(コンビニATMの夜間は330円)", BADGE, BRAND,
                  main_size=50,
                     ask="あなたは、どれを払ってる?"),
    "w1": sc.reveal("1回220円", "1位: コンビニATM(日中でも)", "時間外なら330円", BADGE, BRAND, size=104),
    "tsumi": sc.card("週1回使うと", "年1万1440円", "(220円 × 52週)", BADGE, BRAND, main_size=56),
    "kansan": sc.card("これ、金利0.4%なら", "預金286万円分の利息", "(2,860,000円 × 0.40% = 11,440円)", BADGE, BRAND,
                      main_size=44),
    "jigyaku": sc.card("ここだけの話", "自分のお金を出すのに\nお金を払う", "(冷静に考えるとすごい仕組みなのだ)", BADGE, BRAND,
                       main_size=40),
    "muryo": sc.card("ただし", "無料の条件は銀行ごと", "(回数・時間帯・条件を一度確認)", BADGE, BRAND,
                     main_size=48),
    "chips": sc.chips("あなたはどれ払ってる?", ["コンビニATM派", "つい時間外", "窓口で振込", "ぜんぶ無料"], BADGE, BRAND),
    "loop_back": sc.hero("年1万1440円", "週1のコンビニATMだけで(220円×52回)", BADGE, BRAND,
                         size=96, sub_fs=28),
}

# 全ビートを But/Therefore で繋ぐ(D10・ループ㊶)。check_flow.py で断絶0件を確認すること。
UNITS = [
    Unit("hero_count", "【1万1440円】。1年で消えていく手数料。", anim=1.2, cover=True,
         se="pop", face="surprised", speed=1.05, intonation=1.2, pitch=0.0),
    Unit("intro", "この手数料、ありがちなワースト3なのだ。", anim=1.2, speed=1.15),
    Unit("w3", "3位、振込。窓口だと最大990円なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15),
    Unit("w3b", "同じ振込が、アプリなら110円なのだ。", anim=1.2, speed=1.15),
    Unit("w2", "その振込と同じで、2位は時間外手数料。", anim=1.2, speed=1.15),
    Unit("w1", "そして1位のコンビニATMが【220円】。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("tsumi", "これを週1回で、年間【1万1440円】なのだ。", anim=1.2, se="don", speed=1.1,
         intonation=1.15),
    Unit("kansan", "この額、預金286万円の利息と同じ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("jigyaku", "その預金を出すのに、お金を払ってるのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("muryo", "ただし無料の条件は、銀行ごとに違うのだ。", anim=1.2, speed=1.15),
    Unit("chips", "あなたは、どれを払ってる?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして週1の代償が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S014.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
