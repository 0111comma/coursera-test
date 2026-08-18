#!/usr/bin/env python3
"""S016: 積立を1年おくらせると、20年後にいくら違うのか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  「来年から」にすると、20年後の金額はいくら変わるのか。
答え:
  月3万円・年5%と仮定して 約95万円。
  そのうち出したお金の差は36万円だけで、残りの59万円は増えるはずだった分。

この人の欲求(yokkyu-map A/C: 損したくない・無駄にしたくない):
  **始めたほうがいいのは分かっている。でも「来年でいいや」と思っている。**

作り直しの経緯(ループ71のユーザー指摘):
  前の版は「つみたて投資枠は月10万円が上限」だった。
  ユーザー:「こんなものを作れと言った覚えはない。全部作り直して」
  診断: **答えを制度から借りていた。** 月10万円も上限360万円も、
  公式サイトに書いてある数値を読み上げているだけで、
  視聴者が自分では出さない数字ではなかった。だから「だから何」になる。
  実測の上位(S005 79.2% / S001 77.8% / S003 64.1%)はすべて
  **計算しないと出ない数字**が答えだった。ここを企画の条件に入れる。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "年5%は仮定・2026年8月時点"

MAN20, MAN19 = 1233, 1138
assert MAN20 - MAN19 == 95

SCENES = {
    "toi": sc.card("この動画の問い", "いくら損する?", "※ 毎月3万円・年5%と仮定した例です",
                   BADGE, BRAND, main_size=104, head_fs=32),
    "toi__cover": sc.cover("積立、1年おくらせるといくら損?", "95万円",
                           "出したお金の差は、36万円だけ",
                           "年5%は仮定", BRAND),
    "tsumi": sc.card("この例の積み立て方", "月3万円", "※ 増える保証はありません",
                     BADGE, BRAND, main_size=124, head_fs=32),
    "hikaku": sc.bars2("20年後の合計",
                       ("いま始める", 12.33, "1233万円"),
                       ("来年から", 11.38, "1138万円"), BADGE, BRAND, ymax=15),
    "sa": sc.card("その差", "95万円", "※ 同じ日にそろえて比べた額",
                  BADGE, BRAND, main_size=132, head_fs=32,
                  ask="あなたは今月、始めますか?"),
    "uchiwake": sc.bars2("95万円の中身",
                         ("出したお金の差", 3.6, "36万円"),
                         ("増えるはずだった分", 5.9, "59万円"), BADGE, BRAND, ymax=8),
    "matome": sc.hayami("始める前に見る4つ",
                        [("差の合計", "95万円"), ("出したお金の差", "36万円"),
                         ("増えるはずの分", "59万円"), ("NISAなら", "税金ゼロ")],
                        "※ 毎月3万円・年5%と仮定。増える保証はありません",
                        BADGE, BRAND, col1="1年おくらせると", col2="いくら", focal=2),
    "shime": sc.chips("あなたの積立は?",
                      ["もう始めた", "今月から", "来年から", "まだ考え中"],
                      BADGE, BRAND),
}

UNITS = [
    # 1ユニット目は、欲求を問いの形にして言う(ループ71)
    Unit("toi", "積立、1年おくらせるといくら損?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("tsumi", "たとえば毎月3万円を、積み立てるとする。", anim=1.4, speed=1.05),
    Unit("tsumi", "そして積立を、20年つづけるとする。", anim=0.0, speed=1.05),
    Unit("tsumi", "また積立が、年5%で増えたと仮定する。", anim=0.0, speed=1.05),
    Unit("hikaku", "すると20年後は、1233万円になるのだ。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("hikaku", "では1年おくらせて、19年にしてみる。", anim=0.0, speed=1.05),
    Unit("hikaku", "19年だと、1138万円になるのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("sa", "だから差は、95万円になるのだ。", anim=1.6,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("uchiwake", "でも出したお金の差は、36万円だけなのだ。", anim=1.6, speed=1.05),
    Unit("uchiwake", "つまり残りの59万円は、増えるはずだった分。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("uchiwake", "59万円が、待っただけで消えるのだ。", anim=0.0, speed=1.05),
    Unit("uchiwake", "では毎月1万円の人なら、どうなるのか。", anim=0.0, speed=1.05),
    Unit("uchiwake", "差はおよそ32万円と、小さくなるのだ。", anim=0.0, speed=1.05),
    Unit("matome", "しかもNISAなら、増えた分に税金がかからない。", anim=1.6, speed=1.05),
    Unit("matome", "でもふつうの口座なら、2割が引かれるのだ。", anim=0.0, speed=1.05),
    Unit("matome", "つまり待つほど、減るのは増える分なのだ。", anim=0.0, speed=1.05),
    Unit("shime", "だから今月ぶんだけでも、出してほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S016.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
