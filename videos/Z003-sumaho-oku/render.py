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
BADGE = "※ 出典: パスカル『パンセ』断章136(番号はラフュマ版。初版は1670年)"
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
                           disclaimer="※ 出典: パスカル『パンセ』断章136(番号はラフュマ版。初版は1670年)"),
    "minai": sz.phone_hand("03_troubled", label="たいして見ない", on=True),
    "ochitsukanai": sz.thinking_loop("03_troubled"),
    "sei": sz.phone_hand("04_surprised", bubble="スマホのせい?", on=False),
    "jikan": sz.bubble_locked("04_surprised", "何もしない時間"),
    "taerarenai": sz.thinking_loop("04_surprised"),
    "hon1670": sz.book_now("02_point", "1670年の本", bubble="もう書いてある"),
    "dareka": sz.ancient_person("04_surprised", "350年前", "そう書いた人"),
    "mae350": sz.book_now("02_point", "350年前", bubble="スマホより先"),

    # ---- 幕2 誰が言った(8)
    "pascal": sz.ancient_person("04_surprised", "1600年代", "パスカル"),
    "hisan2": sz.book_now("03_troubled", "神なき人間の悲惨", bubble="結論はこの先"),
    "atsuryoku": sz.memo_tag("02_point", "圧力の単位"),
    "shinu": sz.ancient_person("03_troubled", "39歳", "書き終える前に"),
    "shihen": sz.scraps("04_surprised", label="書きかけの紙"),
    "shihen2": sz.scraps("02_point", label="『パンセ』のもと", tied=True),
    "zairyou": sz.memo_tag("03_troubled", "キリスト教を守る本"),
    "kibarashi": sz.memo_tag("02_point", "気晴らし"),
    "imi": sz.scraps("02_point", label="気晴らしの紙"),
    "imi2": sz.memo_tag("03_troubled", "考えずにすませる"),
    "kari": sz.memo_tag("04_surprised", "たとえば狩り"),
    "kari2": sz.thinking_loop("04_surprised"),
    "kari3": sz.memo_tag("02_point", "追いかけるほう"),

    # ---- 幕3 引用(5)
    "ima": sz.phone_hand("02_point", label="いまの気晴らし", on=True),
    "maeoki": sz.book_now("03_troubled", "ラフュマ版 断章136", bubble="こう書いてある"),
    "quote": sz.quote_card("部屋にいられない", "『パンセ』断章136(ラフュマ版)"),
    "nigeru": sz.thinking_loop("04_surprised"),
    "nigesaki": sz.phone_hand("02_point", label="いまの逃げ先", on=True),

    # ---- 幕4 なぜ残った
    "naze": sz.scraps("04_surprised", bubble="なんで読める?"),
    "shigo": sz.copyists("01_base", years=""),
    "anda": sz.scraps("02_point", label="ペリエと仲間たち", tied=True),
    "kezutta": sz.scraps("03_troubled", label="ポール・ロワイヤル版", tied=True),
    "kezutta2": sz.memo_tag("03_troubled", "危ない言葉を削って"),
    "dake": sz.memo_tag("02_point", "削ったのはこの版だけ"),
    "ima_ban": sz.scraps("05_happy", label="パスカルの紙から"),
    "anshin": sz.book_now("05_happy", "さっきの一行", bubble="削られてない側"),

    # ---- 幕5 誰が評価した
    "voltaire2": sz.ancient_person("04_surprised", "1734年", "ヴォルテール"),
    "hanron": sz.book_now("03_troubled", "『哲学書簡』", bubble="第25書簡まるごと"),
    "hanron2": sz.memo_tag("04_surprised", "反論の中身"),
    "hanron3": sz.ancient_person("02_point", "ヴォルテール", "どこが悪い?"),
    "jinrui": sz.quote_card("人類の味方をする", "ヴォルテール『哲学書簡』第25書簡"),

    # ---- 幕6 正直 → 動作 → 締め
    "yomitsugu": sz.book_now("02_point", "読み継がれた", bubble="噛みつかれて"),
    "hisan": sz.book_now("03_troubled", "この先の話", bubble="ここでは扱わない"),
    "mikata": sz.memo_tag("02_point", "借りるのは見方だけ"),
    "konya": sz.bubble_locked("02_point", "何もしない時間"),
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
    # ---- 幕1 場面 → 判定(7)。**責める語を1つも置かない**(plan §11)
    U("toi", "風呂に入る前、自分のスマホを持ってくか一瞬まよわない?", cover=True, se="pop",
      speed=1.28, intonation=1.25, pad=0.06),
    U("minai", "スマホを持っていっても、たいして見ないんだけどね。"),
    U("ochitsukanai", "なのに置いていくと、なんか落ち着かないよね。"),
    U("sei", "落ち着かないのは、スマホのせいだと思ってる?"),
    U("jikan", "スマホのせいじゃなくて、何もしない時間のせいだよ。"),
    # **裸の一般論で山を打たない**(批評パネル high)。ここで出どころを言う
    U("taerarenai", "何もしない時間に、人はもともと耐えられない。", **_D),
    U("dareka", "何もしない時間のことを、350年前に書いた人がいるの。", **_S),
    U("hon1670", "その本が出たのが1670年。あなたのスマホの350年前ね。"),
    U("mae350", "1670年の本を書いたのは、パスカルってフランスの数学者。"),

    # ---- 幕2 誰が言った(8)
    U("pascal", "パスカルは、圧力の単位に名前が残ってる人ね。", **_S),
    U("atsuryoku", "天気予報で聞く単位のパスカル。あなたも耳にしてるの。", **_S),
    U("shinu", "パスカルは39歳で、本を書き終える前に死んじゃった。"),
    U("shihen", "パスカルが残したのは、書きかけの紙の束なの。", **_S),
    U("shihen2", "パスカルの紙の束が、いま読める『パンセ』なんだよ。", **_S),
    U("zairyou", "『パンセ』のもとは、キリスト教を守る本の材料。意外?"),
    U("kibarashi", "その紙の一枚に、あなたの今夜のことが書いてある。", **_S),
    U("imi", "今夜のまよいを、パスカルは「気晴らし」って呼ぶの。"),

    # ---- 幕3 引用(7)。**答えを2本立てない**(批評パネル high)。
    #      何もしない時間 → 自分のことを考えちゃう → 逃げる、の1本にする
    U("imi2", "気晴らしを探すのは、自分のことを考えたくないから。"),
    # ラフュマ136 の狩りの例は「ほしいのは獲物ではなく追いかけるほう」の一点のために置かれている
    U("kari", "気晴らしの例が、狩りなの。", **_S),
    U("kari2", "たとえば獲物をやるって言われても、受け取らないの。"),
    U("kari3", "ほしいのは獲物じゃなくて、追いかけるほうだから。", **_S),
    U("ima", "あなたがスマホでほしいのも、獲物じゃないのかもね。"),
    U("maeoki", "スマホのことも断章136にあるの。不幸の話ね。"),
    U("quote", "「人の不幸はみんな、部屋にじっとしていられないことから来る」。"),
    U("nigeru", "部屋にいられないから、あなたもスマホに逃げるの。", **_D),
    U("nigesaki", "スマホは逃げ先。原因じゃないの。", **_S),

    # ---- 幕4 なぜ残った(8)。**how ではなく why**。編んだ人の動機を言う(批評パネル high)。
    #      さらに「削った本」の直後にケアを置く。引用が削られた本のものに見えると、
    #      この動画の中身は引用ひとつに乗っているので全部が疑わしくなる(KGI)。
    #      ラフュマ版はパスカルの紙の並び(第一写本)から起こしているので、そこを言う
    U("naze", "その紙が、いまも読めるのはなんで?", **_S),
    U("shigo", "答えは、信仰を守る本にしたい人が編んだから。"),
    U("anda", "信仰の側の、おいっ子ペリエとポール・ロワイヤルの仲間。"),
    U("kezutta", "仲間たちが出したのが、ポール・ロワイヤル版。自分も見てない?"),
    U("kezutta2", "そのポール・ロワイヤル版、危ない言葉を削って出してるの。"),
    U("dake", "じゃあ、あの一行も削られてるの?", **_S),
    U("ima_ban", "でも、いまの『パンセ』は削る前の紙から起こしてるの。"),
    U("anshin", "だから、さっき読んだ一行も削られてない側だよ。", **_S),

    # ---- 幕5 誰が評価した(5)。plan §1.7 の上限は3。**2カット超える理由**:
    #      反論の中身を言わないと「有名人が一章ぶん反対した」だけの来歴の雑学になり、
    #      視聴者に「で、どっちが正しいの? 自分は借りていいの?」が残る(批評パネル high)
    U("voltaire2", "そのパスカルに噛みついたのは、誰だと思う?"),
    U("hanron", "答えはヴォルテール。1734年に、まるごと一章を反論に使うの。"),
    U("hanron2", "反論はこう。人間はそこまで惨めじゃない。", **_S),
    U("hanron3", "人間の気晴らしのどこが悪い、って。あなたも思わない?"),
    U("jinrui", "反論の最後は、「この人間ぎらいを相手に、人類の味方をする」。"),

    # ---- 幕6 正直 → 動作 → 締め(6)
    U("yomitsugu", "そこまで噛みつかれて、『パンセ』はいまも読まれてるの。"),
    U("hisan", "ただし、その本が行きつく結論は、自分の今夜より先なの。", **_S),
    U("hisan2", "結論は「神なき人間の悲惨」。そこまで行く話なの。", **_S),
    U("mikata", "悲惨は今夜のあなたには要らない。借りるのは見方だけ。", **_S),
    U("konya", "持っていく見方はひとつ。人は、何もしない時間に耐えられない。"),
    U("oku", "だから今夜、風呂に入る前に、スマホを脱衣所の棚に置く。", **_D),
    U("nanpun", "スマホを置いたあとは、何分がまんとか決めなくていいの。"),
    U("owari", "またスマホでまよったら、あなたのせいじゃないの。"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z003.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
