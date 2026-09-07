#!/usr/bin/env python3
"""Z003「スマホを置くと、なんで落ち着かないのか」

チャンネル「ヤケに心理学に詳しいずんだもん」の3本目。企画書は plan.md。
型は docs/channel-zunda/strategy.md §8 の #17(問い型)。

**型を散らす**: Z001 否定・エピクテトス / Z002 場面・セネカ / Z003 問い・パスカル。

**この動画のメッセージは1つだけ:**

    スマホは原因じゃない。人はもともと何もしない時間に耐えられない。
    だから今夜、風呂の前に棚に置く。

学びの3問は、この1つを深くするためだけに使う(plan.md §1.7 のカット上限 8/4/3)。
**この線に乗らないカットは、面白くても入れない。**

**視聴者は自分を責めている側**なので、「依存」「中毒」「意志が弱い」を1回も使わない。
**正直の幕**を置く(パスカルの結論は「神なき人間の悲惨」で、この動画はそこまで行かない)。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

F.POSE_DIR = ROOT / "assets" / "character-zunda"

TITLE = "スマホのせいじゃない"
BADGE = "※ 出典: パスカル『パンセ』ラフュマ136(初版1670年)"
F.use_fp_theme(TITLE, speaker=3, badge=BADGE)      # 3 = ずんだもん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402
import scenes_zunda as sz  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

SCENES = {
    # ---- 幕1 場面 → 判定
    "toi": sf.person("03_troubled", height=0.46),
    "toi__cover": sf.cover("風呂に入る前、自分のスマホを持ってくか一瞬まよわない?",
                           "今夜", "持ってく?",
                           name="03_troubled", main_lab="いまのあなた",
                           alt_val="棚に置く", alt_lab="あなたはどっち?",
                           disclaimer="※ 出典: パスカル『パンセ』ラフュマ136(初版1670年)"),
    "minai": sz.phone_hand("03_troubled", label="たいして見ない", on=True),
    "ochitsukanai": sz.thinking_loop("03_troubled"),
    "sei": sz.phone_hand("04_surprised", bubble="スマホのせい?", on=False),
    "jikan": sz.bubble_locked("04_surprised", "何もしない時間"),
    "taerarenai": sz.thinking_loop("04_surprised"),
    "hon1670": sz.book_now("02_point", "1670年の本", bubble="もう書いてある"),
    "mae350": sz.book_now("02_point", "350年前", bubble="スマホより先"),

    # ---- 幕2 誰が言った(8)
    "pascal": sz.ancient_person("04_surprised", "1600年代", "パスカル"),
    "atsuryoku": sz.memo_tag("02_point", "圧力の単位"),
    "shinu": sz.ancient_person("03_troubled", "39歳", "書き終える前に"),
    "shihen": sz.scraps("04_surprised", label="書きかけの紙片"),
    "zairyou": sz.scraps("03_troubled", label="本の材料"),
    "kibarashi": sz.memo_tag("02_point", "気晴らし"),
    "imi": sz.scraps("02_point", label="気晴らしの紙片"),
    "imi2": sz.memo_tag("03_troubled", "考えずにすませる"),
    "kari": sz.memo_tag("04_surprised", "狩りと賭け事"),

    # ---- 幕3 引用(5)
    "ima": sz.phone_hand("02_point", label="いまの気晴らし", on=True),
    "maeoki": sz.book_now("03_troubled", "350年前の紙片", bubble="こう書いてある"),
    "quote": sz.quote_card("部屋にじっとしていられない", "『パンセ』ラフュマ136"),
    "nigeru": sz.thinking_loop("04_surprised"),
    "nigesaki": sz.phone_hand("02_point", label="いまの逃げ先", on=True),

    # ---- 幕4 なぜ残った(4)
    "naze": sz.scraps("04_surprised", bubble="なんで読める?"),
    "shigo": sz.copyists("01_base", years=""),
    "anda": sz.scraps("02_point", label="1670年に出た", tied=True),
    "kezutta": sz.memo_tag("03_troubled", "危ない言葉を削って"),

    # ---- 幕5 誰が評価した(3)
    "voltaire": sz.book_now("04_surprised", "削って出した本", bubble="ほめられた?"),
    "hanron": sz.ancient_person("04_surprised", "1734年", "ヴォルテール"),
    "hanron2": sz.book_now("03_troubled", "一章まるごと", bubble="反論に使った"),
    "jinrui": sz.quote_card("人類の側につく", "ヴォルテール『哲学書簡』25"),

    # ---- 幕6 正直 → 動作 → 締め
    "yomitsugu": sz.book_now("02_point", "読み継がれた", bubble="噛みつかれて"),
    "shoujiki": sz.ancient_person("03_troubled", "パスカル", "結論はこの先"),
    "hisan": sz.book_now("03_troubled", "この先の話", bubble="ここでは扱わない"),
    "hisan2": sz.thinking_loop("03_troubled"),
    "mikata": sz.memo_tag("02_point", "借りるのは見方だけ"),
    "konya": sz.bubble_locked("02_point", "何もしない時間"),
    "konya2": sz.tonight("02_point"),
    "oku": sz.phone_shelf("05_happy", bubble="脱衣所の棚に"),
    "nanpun": sz.phone_shelf("05_happy", bubble="何分でもいい"),
    "owari": sz.go_home("05_happy"),
}

# 1カット3.0秒以内(check_tempo)。Z 番台の実測は 8.66字/秒、ゲートは 8.4 で見積もる
_F = dict(anim=1.7, speed=1.30, intonation=1.22, pad=0.05, chara="none")
_S = dict(anim=1.5, speed=1.30, intonation=1.22, pad=0.05, chara="none")
_D = dict(anim=1.9, se="don", speed=1.28, intonation=1.28, pad=0.12, chara="none")


def U(scene, sub, **kw):
    d = dict(_F)
    d.update(kw)
    return Unit(scene, sub, **d)


UNITS = [
    # ---- 幕1 場面 → 判定(8)。**責める語を1つも置かない**(plan §11)
    U("toi", "風呂に入る前、自分のスマホを持ってくか一瞬まよわない?", cover=True, se="pop",
      speed=1.28, intonation=1.25, pad=0.06),
    U("minai", "スマホを持っていっても、たいして見ないんだけどね。"),
    U("ochitsukanai", "なのにスマホを置いていくと、なんか落ち着かないよね。"),
    U("sei", "落ち着かないのは、スマホのせいだと思ってる?"),
    U("jikan", "スマホのせいじゃなくて、何もしない時間のせいだよ。"),
    U("taerarenai", "何もしない時間に、人はもともと耐えられないの。", **_D),
    U("hon1670", "何もしない時間の話は、1670年の本にもう書いてあるの。"),
    U("mae350", "1670年って、あなたのスマホの350年前ね。", **_S),

    # ---- 幕2 誰が言った(8)
    U("pascal", "その本を書いたのはパスカル。フランスの数学者ね。"),
    U("atsuryoku", "パスカルの名前、天気予報で聞いたことない? 気圧の単位ね。"),
    U("shinu", "パスカルは39歳で死ぬの。本を書き終える前にね。"),
    U("shihen", "だから『パンセ』は、本じゃなくて紙片の束だよ。"),
    U("zairyou", "紙片は、キリスト教を弁護する本の材料だったんだよ。"),
    U("kibarashi", "紙片のひとつが、あなたの今夜の話なんだよ。", **_S),
    U("imi", "紙片が書いてるのは、気晴らしの話。", **_S),
    U("imi2", "気晴らしって、死ぬことを考えずにすませる工夫のこと。"),
    U("kari", "気晴らしの例は、狩りと賭け事。あなたの手のなかじゃないの。"),

    # ---- 幕3 引用(5)
    U("ima", "その気晴らしの場所に、いまはスマホが入るの。"),
    U("maeoki", "スマホを置いた夜の不幸も、350年前の紙片にあるの。"),
    U("quote", "こう。「人の不幸はただ一つ、部屋にじっとしていられないこと」。"),
    U("nigeru", "部屋にじっとしていられないから、あなたも逃げ先を探すの。", **_D),
    U("nigesaki", "部屋から逃げる先が、いまはスマホなだけ。原因じゃないの。"),

    # ---- 幕4 なぜ残った(4)
    U("naze", "その紙片が、いまも読めるのはなんで?"),
    U("shigo", "答えは、パスカルが死んだあと、他人が編んだから。"),
    U("anda", "編んだのは甥と修道院の人。読める形にしたのは他人なの。"),
    U("kezutta", "他人が並べ替えるついでに、危ない言葉も削ってるんだよ。"),

    # ---- 幕5 誰が評価した(3)。**ほめた人ではなく、噛みついた人**を置く
    U("voltaire", "危ない言葉を削った本、ほめられたと思う?"),
    U("hanron", "その本にまっさきに噛みついたのが、ヴォルテール。1734年ね。"),
    U("hanron2", "ヴォルテールは一章まるごと、反論に使ったの。"),
    U("jinrui", "その一行が、「わたしは人類の側につく」。あなたも人類ね。", **_S),

    # ---- 幕6 正直 → 動作 → 締め(8)
    U("yomitsugu", "人類の側についた反論のおかげで、パスカルは読み継がれたの。"),
    U("shoujiki", "ただ、ここがパスカルの結論じゃないの。", **_S),
    U("hisan", "結論は、神のいない人間は悲惨だ、まで行くの。", **_S),
    U("hisan2", "悲惨って言われても、今夜のあなたには遠いよね。"),
    U("mikata", "悲惨までは行かないの。あなたに借りてほしいのは見方だけ。"),
    U("konya", "見方は、何もしない時間に人は耐えられない、の一つだけ。", **_S),
    U("konya2", "その見方だけ、今夜の脱衣所に持っていくの。"),
    U("oku", "だから今夜、あなたは風呂の前にスマホを脱衣所の棚に置くだけ。", **_D),
    U("nanpun", "脱衣所に置いたあとは、何分がまんとか決めなくていいの。"),
    U("owari", "また脱衣所でまよったら、スマホのせいじゃないって思い出して。"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z003.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
