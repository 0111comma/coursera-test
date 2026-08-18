#!/usr/bin/env python3
"""S017: ふるさと納税、10月から返礼品のルールが変わる。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  いま見ている返礼品は、10月以降も同じように選べるのか。
答え:
  選べなくなるものがある。2026年10月から、加工品は「その地域で過半の付加価値が
  生まれたこと」を証明できないと返礼品にできない。

この人の欲求(yokkyu-map C: 無駄にしたくない):
  **欲しい返礼品を、もらい損ねたくない。**

ネタの根拠(demand-2026-08.md の実測):
  S005(ふるさと納税、なぜ実質2000円?)は視聴率79.2%で7本中の最高。
  上位3本の共通点は「視聴者がいま実際にやっていること」。今年ぶんをやる人に当たる。
  S005は「いくらまで(上限)」、この動画は「いつまでに(期限)」で重ならない。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・制度改正の予定"

SCENES = {
    "aki": sc.card("ふるさと納税", "年末にやればいい?", "※ 2026年8月時点の情報です",
                   BADGE, BRAND, main_size=68, head_fs=32),
    "aki__cover": sc.cover("ふるさと納税、10月に何が変わる?", "10月1日",
                           "選べる返礼品が入れ替わります", "2026年8月時点", BRAND),
    "koyomi0": sc.bars2("寄付できる日数で見ると",
                        ("9月30日まで", 4.3, "43日"),
                        ("10月1日から", 9.2, "年末まで92日"), BADGE, BRAND, ymax=11),
    "kijun": sc.card("何が厳しくなるか", "地場産品の基準", "※ 総務省の告示が改正されました",
                     BADGE, BRAND, main_size=72, head_fs=32),
    "kakou": sc.card("証明が要るもの", "過半の付加価値", "※ 一般販売価格の記載も義務に",
                     BADGE, BRAND, main_size=66, head_fs=32),
    "logo": sc.card("名前だけ地元の品", "実績が上限に", "※ 数量の裏づけが要るようになる",
                    BADGE, BRAND, main_size=82, head_fs=32),
    "kawaranai": sc.hayami("10月の境目",
                           [("地場産品の基準", "厳しくなる"), ("返礼品の調達費", "3割のまま"),
                            ("募集の経費", "5割のまま"), ("実質の負担", "変わらない")],
                           "※ 2026年8月時点の予定。対象外になる品は自治体の判断です",
                           BADGE, BRAND, col1="項目", col2="10月から", focal=0),
    "shime": sc.chips("欲しい返礼品は、もう決まっていますか?",
                      ["決まっている", "まだ選び中", "今年はやらない", "毎年おまかせ"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("aki", "ふるさと納税は、年末にやればいいと思っていないか。", anim=1.0,
         cover=True, se="pop", speed=1.05, intonation=1.25),
    Unit("aki", "でもそのふるさと納税に、10月の区切りがあるのだ。", anim=1.4,
         face="troubled", speed=1.05),
    Unit("kijun", "その日から、返礼品の基準が厳しくなるのだ。", anim=1.4, speed=1.05),
    Unit("kijun", "その基準とは、その土地の品かどうかを見る決まりのこと。", anim=0.0,
         speed=1.05),
    Unit("kakou", "まずその決まりで、加工品に証明が要るようになるのだ。", anim=1.4, speed=1.05),
    Unit("kakou", "その証明とは、値打ちの半分以上がその地域で生まれたかどうか。",
         anim=0.0, speed=1.05),
    Unit("logo", "そしてロゴを付けただけの品も、絞られるのだ。", anim=1.4,
         speed=1.05),
    Unit("logo", "その品は、1年以内に売れた数までしか出せなくなるのだ。", anim=0.0,
         se="impact", se_at=0.30, speed=1.05, intonation=1.2),
    Unit("koyomi0", "だから今の基準で選べるのは、9月末までなのだ。", anim=1.6,
         speed=1.05),
    Unit("koyomi0", "その日までは、あと43日しかないのだ。", anim=0.0,
         face="surprised", se="don", speed=1.05, intonation=1.25),
    Unit("kawaranai", "ただし全部が変わるわけでは、ないのだ。", anim=1.6, speed=1.05),
    Unit("kawaranai", "まず返礼品にかけられるお金は、3割のままなのだ。", anim=0.0,
         speed=1.05),
    Unit("kawaranai", "そして募集にかけられるお金も、5割のまま変わらないのだ。",
         anim=0.0, speed=1.05),
    Unit("kawaranai", "だから変わるのは、選べる品のほうだけなのだ。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("shime", "だから欲しい品があるなら、9月のうちに見てほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S017.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
