#!/usr/bin/env python3
"""S019: 会社を辞めてから、失業手当が出るまでの空白が短くなった。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  自己都合で辞めたら、失業手当が出るまで何ヶ月空くのか。
答え:
  2025年4月から、給付制限が2ヶ月 → 1ヶ月に短くなった。待期7日 + 給付制限1ヶ月。

この人の欲求(yokkyu-map D: 不安を減らしたい):
  **辞めたい。でも、収入が無い期間が怖い。その不安を減らしたい。**

ネタの根拠(demand-2026-08.md):
  雇用保険は未着手の領域。「辞めたい」はいま実際に思っている人が多く、
  上位3本の共通点(視聴者がいま実際にやっていること)を満たす。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・自己都合で辞めた場合"

SCENES = {
    "yameru": sc.card("辞めたいけれど", "収入が止まる", "※ 会社員(雇用保険)の話です",
                      BADGE, BRAND, main_size=96, head_fs=32),
    "yameru__cover": sc.cover("辞めてから、お金が出るまで何ヶ月?", "1ヶ月",
                              "2025年4月から、空白がひと月縮みました", "2026年8月時点", BRAND),
    "mukashi": sc.card("前はどうだったか", "3ヶ月と言われた", "※ さらに前の制度の記憶",
                       BADGE, BRAND, main_size=76, head_fs=32),
    "obi0": sc.bars2("辞めてから、お金が出るまで",
                     ("前のきまり", 6.7, "2ヶ月と7日"),
                     ("いまのきまり", 6.7, ""), BADGE, BRAND, ymax=8),
    "obi1": sc.bars2("辞めてから、お金が出るまで",
                     ("前のきまり", 6.7, "2ヶ月と7日"),
                     ("いまのきまり", 3.7, "1ヶ月と7日"), BADGE, BRAND, ymax=8),
    "taiki": sc.card("最初の7日間", "待期", "※ この7日は誰でも同じ",
                     BADGE, BRAND, main_size=140, head_fs=32,
                     ask="あなたは自己都合ですか、会社都合ですか?"),
    "kaisha": sc.hayami("待つ長さの一覧",
                        [("自分から辞めた", "7日 + 1ヶ月"), ("会社の都合", "7日だけ"),
                         ("5年に3回以上", "7日 + 3ヶ月"), ("実際の振込", "さらに先")],
                        "※ 2026年8月時点。受け取るには加入していた月数の条件もあります",
                        BADGE, BRAND, col1="辞め方", col2="待つ長さ", focal=1),
    "shime": sc.chips("辞めるとしたら、いつを考えていますか?",
                      ["3ヶ月以内", "今年中", "まだ先", "辞めない"], BADGE, BRAND),
}

UNITS = [
    Unit("yameru", "会社を辞めたいけれど、給料が止まるのが怖い。", anim=1.0,
         cover=True, se="pop", speed=1.05, intonation=1.25),
    Unit("mukashi", "その空白は、3ヶ月だと聞いていないか。", anim=1.4,
         face="troubled", speed=1.05),
    Unit("mukashi", "でもその3ヶ月は、いまの決まりではないのだ。", anim=0.0,
         speed=1.05),
    Unit("obi0", "まずその決まりでは、最初に7日間の待ちがある。", anim=1.6,
         speed=1.05),
    Unit("taiki", "その7日間は、待期と呼ばれる期間のこと。", anim=1.4, speed=1.05),
    Unit("taiki", "そして待期は、辞め方に関係なく全員にある。", anim=0.0,
         speed=1.05),
    Unit("obi0", "その待期のあとに、もうひとつ待ちがつくのだ。", anim=1.6,
         speed=1.05),
    Unit("obi0", "そして自分から辞めた人は、そこが長かったのだ。", anim=0.0,
         speed=1.05),
    Unit("obi1", "でも去年から、そこが1ヶ月に縮んだのだ。", anim=1.6,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("obi1", "その前は2ヶ月だったので、ひと月ぶん早くなったのだ。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("kaisha", "ただし辞め方によって、待つ長さは変わるのだ。", anim=1.6,
         speed=1.05),
    Unit("kaisha", "まず会社の都合で辞めた人は、待期の7日だけなのだ。", anim=0.0,
         speed=1.05),
    Unit("kaisha", "でも5年に3回以上あると、3ヶ月に戻るのだ。", anim=0.0,
         speed=1.05),
    Unit("kaisha", "そして振り込みは、手続きのぶんさらに先なのだ。",
         anim=0.0, speed=1.05),
    Unit("shime", "だから辞める時期は、この長さを見て決めるのだ。",
         anim=1.4, face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S019.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
