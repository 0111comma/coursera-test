#!/usr/bin/env python3
"""S020: ふるさと納税の2000円は、何回払うのか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  自己負担2000円は、寄付するたびに払うのか。
答え:
  年に1回だけ。だから寄付先を分けるほど、2000円は薄まる。

この人の欲求(yokkyu-map C: 無駄にしたくない):
  **せっかくやるなら、いちばん得な使い方をしたい。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・仮定の金額での計算"

JIKO = 2_000
assert 30_000 - JIKO == 28_000

SCENES = {
    "toi": sc.card("この動画の問い", "何回払うの?", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, main_size=110, head_fs=32),
    "toi__cover": sc.cover("ふるさと納税の2000円、何回払うの?", "年1回",
                           "分けるほど、2000円は薄まる",
                           "2026年8月時点", BRAND),
    "seido": sc.card("じぶんが本当に払う額", "2000円だけ", "※ 残りは税金から引かれます",
                     BADGE, BRAND, main_size=110, head_fs=32),
    "ichi": sc.bars2("1か所だけの場合",
                     ("届く返礼品", 3.0, "3000円"),
                     ("自腹", 2.0, "2000円"), BADGE, BRAND, ymax=3.6),
    "juu": sc.bars2("10か所に分けたとき",
                    ("届く返礼品", 30.0, "3万円"),
                    ("自腹", 2.0, "2000円"), BADGE, BRAND, ymax=36),
    "usumaru": sc.card("1万円あたりの自腹", "200円に薄まる",
                       "※ 10か所に分けた場合", BADGE, BRAND,
                       main_size=80, head_fs=32,
                       ask="あなたは何か所に分けた?"),
    "matome": sc.hayami("分け方でどう変わるか",
                        [("1か所だけ", "残り1000円ぶん"), ("10か所", "残り2万8000円ぶん"),
                         ("自腹の2000円", "年に1回だけ"), ("上限の外", "まるごと自腹")],
                        "※ 2026年8月時点。上限は年収と家族の人数で変わります",
                        BADGE, BRAND, col1="どう寄付するか", col2="どうなるか", focal=1),
    "shime": sc.chips("分けるときのコツは?",
                      ["定番から選ぶ", "時期をずらす", "家族で相談する", "まだやってない"],
                      BADGE, BRAND),
}

UNITS = [
    # ループ71のユーザー指摘「普通に何の話か分からん」を受けて頭から書き直した。
    # タイトルの2000円が何なのか(自己負担)を、先に名乗ってから本題に入る
    Unit("toi", "ふるさと納税の2000円、何回払うの?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("seido", "ふるさと納税は、自治体に寄付する制度。", anim=1.4, speed=1.05),
    Unit("seido", "寄付した額は、あとで税金から引かれる。", anim=0.0, speed=1.05),
    Unit("seido", "ただしいまの制度で、2000円だけ自腹。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("ichi", "では自治体ひとつに、1万円を納める。", anim=1.6, speed=1.05),
    Unit("ichi", "その自治体からは、返礼品をもらえる。", anim=0.0, speed=1.05),
    Unit("ichi", "返礼品の値打ちは、寄付の3割まで。", anim=0.0, speed=1.05),
    Unit("ichi", "1万円の3割で、3000円ぶんなのだ。", anim=0.0, speed=1.05),
    Unit("ichi", "3000円から自腹を引くと、1000円ぶん。", anim=0.0, speed=1.05),
    Unit("juu", "では10の自治体に、1万円ずつ納めると?", anim=1.6, speed=1.05),
    Unit("juu", "納める額は、あわせて10万円になる。", anim=0.0, speed=1.05),
    Unit("juu", "返礼品も10倍の、3万円ぶんになる。", anim=0.0,
         face="happy", speed=1.05),
    Unit("usumaru", "でも自腹の2000円は、年に1回だけなのだ。", anim=1.6,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("usumaru", "1万円あたりの自腹は、200円に薄まる。", anim=0.0, speed=1.05),
    Unit("usumaru", "だから残る返礼品は、2万8000円ぶん。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("matome", "ただし寄付には、上限もあるのだ。", anim=1.6,
         face="troubled", speed=1.05),
    Unit("matome", "上限を超えた寄付は、まるごと自腹。", anim=0.0, speed=1.05),
    Unit("shime", "だから上限の内で、分けてほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S020.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
