#!/usr/bin/env python3
"""S032: 1000万円を月5万ずつ取り崩すと、何歳で尽きるのか。

新デザイン1本目(自前キャラ・明るい背景・冥鳴ひまり)。
型は competitor-shorts-teardown-2026-08-23.md の分解にもとづく:
  0〜5% カバー / 5〜73% 本編 / 73〜76% 結論 / 76〜100% CTA
  1カット1.6〜1.8秒。表は出しっぱなしにして**赤枠を1行ずつ動かす**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

TITLE = "1000万円 月5万で何歳まで?"
F.use_fp_theme(TITLE, speaker=14)      # 冥鳴ひまり

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

M0 = V.RESULT[0.00]; M3 = V.RESULT[0.03]; M5 = V.RESULT[0.05]
assert M0[0] == 200 and round(M0[2]) == 82

SCENES = {
    "ie": sf.person("01_base"),
    "ie__cover": sf.cover("老後のお金", "1000万円を月5万で", "何歳まで持つ?"),
    "toi": sf.person_bubble("03_troubled", "いくら使っていいの?"),
    "warizan": sf.hero("200か月", "1000万 ÷ 5万", name="01_base"),
    "odoroki": sf.person("04_surprised"),
    "hyo": sf.table(["利回り", "尽きる年齢"],
                    [("0%", "82歳"), ("3%", "88歳"), ("5%", "101歳")],
                    title="65歳から月5万ずつ取り崩した場合"),
    "hyo0": sf.table(["利回り", "尽きる年齢"],
                     [("0%", "82歳"), ("3%", "88歳"), ("5%", "101歳")],
                     highlight=0, title="65歳から月5万ずつ取り崩した場合"),
    "hyo3": sf.table(["利回り", "尽きる年齢"],
                     [("0%", "82歳"), ("3%", "88歳"), ("5%", "101歳")],
                     highlight=1, title="65歳から月5万ずつ取り崩した場合"),
    "hyo5": sf.table(["利回り", "尽きる年齢"],
                     [("0%", "82歳"), ("3%", "88歳"), ("5%", "101歳")],
                     highlight=2, title="65歳から月5万ずつ取り崩した場合"),
    "gyaku": sf.table(["利回り", "毎月いくらまで"],
                      [("0%", "2万7000円"), ("3%", "4万2000円"), ("5%", "5万3000円")],
                      title="95歳まで持たせるなら"),
    "gyaku0": sf.table(["利回り", "毎月いくらまで"],
                       [("0%", "2万7000円"), ("3%", "4万2000円"), ("5%", "5万3000円")],
                       highlight=0, title="95歳まで持たせるなら"),
    "kari": sf.person("03_troubled"),
    "kime": sf.person("02_point"),
    "shime": sf.cta("", "02_point"),
    "cta1": sf.cta("", "01_base"),
    "cta2": sf.cta("", "02_point", show_button=True),
}

UNITS = [
    # ---- カバー(0〜5%)
    Unit("ie", "1000万円、月5万でいつまで持つ?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.2, chara="none"),

    # ---- 本編
    Unit("toi", "老後のお金、いくら使っていいか分からないですよね。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("toi", "貯める話は多いのに、【使う】話は少ないんです。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("warizan", "まず、運用しない場合から。", anim=1.2, speed=1.05, chara="none"),
    Unit("warizan", "1000万円を月5万で割ると、【200か月】。", anim=0.0,
         se="don", speed=1.0, intonation=1.2, chara="none"),
    Unit("odoroki", "16年8か月しか持ちません。", anim=1.2,
         se="impact", se_at=0.2, speed=1.05, chara="none"),
    Unit("odoroki", "65歳から始めると、【82歳】で尽きます。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("hyo", "運用しながら取り崩すと、どうなるか。", anim=1.2, speed=1.05, chara="none"),
    Unit("hyo0", "運用しないなら、【82歳】。", anim=1.2, speed=1.05, chara="none"),
    Unit("hyo3", "年3%で回せば、【88歳】まで。", anim=1.2, speed=1.05, chara="none"),
    Unit("hyo5", "年5%なら、【101歳】まで持ちます。", anim=1.2,
         se="don", speed=1.05, chara="none"),
    Unit("kari", "ただし利回りは【仮定】です。減る年もあります。", anim=1.2,
         speed=1.05, pad=0.35, chara="none"),
    Unit("gyaku", "そこで、逆から決めます。", anim=1.2, speed=1.05, chara="none"),
    Unit("gyaku", "95歳まで持たせるなら、毎月いくらまでか。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("gyaku0", "運用しないなら、【2万7000円】まで。", anim=1.2,
         se="impact", se_at=0.25, speed=1.05, chara="none"),

    # ---- 結論(73〜76%)
    Unit("kime", "先に【何歳まで】を決めれば、毎月の額が決まります。", anim=1.2,
         se="don", speed=1.05, chara="none"),

    # ---- CTA(76〜100%)
    Unit("cta1", "このチャンネルでは今後も、", anim=1.2, speed=1.05, chara="none"),
    Unit("cta1", "お金の数字をひとつずつ確かめていきます。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("cta2", "よかったらチャンネル登録をお願いします。", anim=1.2,
         speed=1.05, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S032.mp4", speaker=14, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
