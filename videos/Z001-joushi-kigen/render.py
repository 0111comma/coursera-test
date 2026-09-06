#!/usr/bin/env python3
"""Z001「上司の一言、帰りの電車でまだ引きずってる?」

チャンネル「ヤケに心理学に詳しいずんだもん」の1本目。企画書は plan.md。
型は docs/channel-zunda/strategy.md。

**2026-09-04 の5巡目で「表」という仕掛けを捨てた。**ユーザー「ガチで何言ってんの?」
(『変えられることと変えられないこと、分けてみない?』『これ、考えたの1900年前の奴隷なんだって』)。
前情報ゼロの読者に5周直しても、表・分ける・奴隷が考えた、の3語は視聴者の場面から飛んでいた。
いまの骨(plan.md §8):

- 幕1 場面: 上司の一言を帰りの電車で引きずっている(1〜2)
- 幕2 判定: その考えは明日の役に立たない。言っちゃったこと・上司の機嫌・評判・評価は変えられない(3〜8)
- 幕3 残るもの: 自分で変えられるのは、明日、上司になに言うかだけ(9〜10)
- 幕4 出どころ: 実はこれ、1900年前の奴隷の考え方(11〜15)。**仕掛けではなく由来として最後に置く**
- 幕5 動作: 今夜、明日の一言をメモに1行(16〜19)

**画面は scenes_zunda の場面の絵**(2026-09-04 ユーザー「もっとイラストつかって。よくわからん画面に出てる図」)。
赤い鍵=自分で変えられない、緑のチェック=自分で変えられる。ずんだもんは全カットで左に立つ。

**計算が無い回なので verify.py の役目は年の引き算だけ**(strategy §5.3)。
声に出す数は「1900年前」(11)と「1行」(17)で、plan.md の前提表に根拠と出典がある。
「2世紀前半」は図(arrow)と常設バッジが持つ(前情報ゼロの読者に年として通らなかった)。

立ち絵は **ずんだもん**(`assets/character-zunda/`)。fplib の POSE_DIR を
このチャンネル用に差し替えている。表情は 01_base(normal)/ 02_point(smug)/
03_troubled(troubled)/ 04_surprised / 05_happy。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

# --- このチャンネルの立ち絵はずんだもん(fp の意匠はそのまま使う)
F.POSE_DIR = ROOT / "assets" / "character-zunda"

# 常設ラベルは**分類名ではなく、この動画が判定する問い**にする
TITLE = "動かせるのはどっち?"
BADGE = "※ 出典: エピクテトス『提要』1・5 / マルクス・アウレリウス『自省録』1・8"
F.use_fp_theme(TITLE, speaker=3, badge=BADGE)      # 3 = ずんだもん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402
import scenes_zunda as sz  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

SCENES = {
    # ---- 幕1 場面 + 二択。**×はまだ付けない**
    "toi": sf.person("03_troubled", height=0.46),
    "toi__cover": sf.cover("上司の一言、帰りの電車でまだ引きずってる?",
                           "あの一言", "言えばよかった",
                           name="03_troubled", main_lab="いまのあなた",
                           alt_val="明日の一言", alt_lab="あなたはどっち?",
                           disclaimer="※ 出典: エピクテトス『提要』1・5 / マルクス・アウレリウス『自省録』1・8"),
    # 2026-09-04 ユーザー「もっとイラストつかって。よくわからん画面に出てる図」
    # → 数の図(compare / formula / arrow / hero)をやめ、場面の絵(scenes_zunda)にした
    "kangae": sz.train_think("03_troubled", "あの時…"),

    # ---- 幕2 判定
    "yaku": sz.calendar_pair("03_troubled", ("今日", "×"), ("明日", "?")),
    "tatanai": sz.calendar_one("03_troubled", "明日", "×", bubble="変わらない"),
    "batsu": sz.bubble_locked("03_troubled", "……"),
    "ugokanai": sz.thinking_loop("03_troubled"),
    "sanko": sz.boss_crowd("03_troubled"),
    "hyouka2": sz.boss_sheet("03_troubled", "評価"),

    # ---- 幕3 残るもの
    "q": sz.ask_what("01_base"),
    "hitokoto": sz.tomorrow_line("02_point"),

    # ---- 幕4 誰が言ったか(エピクテトス)
    "kangaenai": sz.train_think("02_point", "考えない"),
    "dare": sz.who_silhouette("04_surprised"),
    "epi": sz.ancient_person("04_surprised", "エピクテトス", "ストア派"),
    "stoa": sz.ancient_person("02_point", "ストア派", "ストイックの元"),
    "stoa2": sz.train_think("02_point", "我慢じゃない"),
    "epi2": sz.owned("04_surprised"),
    "mochimono": sz.owned("03_troubled"),
    "kazoeru": sz.slave_sees("05_happy"),
    "jugyou": sz.ancient_person("01_base", "哲学の授業", "ご主人も元奴隷"),
    "sensei": sz.ancient_person("05_happy", "先生の教え", "自由になったあと"),
    "hyouban": sz.boss_crowd("01_base"),
    "hyouban2": sz.slave_sees("02_point"),
    "kakanai": sz.book_cross("01_base"),
    "deshi": sz.memo_tag("02_point", "弟子のメモ"),
    "teiyou2": sz.book_now("02_point", "53の教え", bubble="薄い本"),

    # ---- 幕5 なぜ残った(皇帝)→ 提要5 → 修道院 → エリス
    "utsusu": sz.book_now("03_troubled", "手で写す", bubble="写さないと消える"),
    "naze": sz.book_now("03_troubled", "提要", bubble="なんで残った?"),
    "koutei": sz.emperor("04_surprised", "ずっとあとの皇帝"),
    "koutei2": sz.emperor("02_point", "マルクス・アウレリウス", bubble="自分だけのノート"),
    "jiseiroku": sz.emperor("02_point", "ローマ皇帝", bubble="恩人の名前"),
    "jiseiroku2": sz.book_now("02_point", "貸してくれた本", bubble="若いころの先生"),
    "jinchuu": sz.emperor("03_troubled", "ローマ皇帝", bubble="戦争の陣中で"),
    "ekibyou2": sz.emperor("03_troubled", "ローマ皇帝", bubble="止められない"),
    "onaji": sz.lineage("01_base"),
    "quote_k": sz.quote_card("つらいのは出来事じゃなくて|受け取り方だ", "『自省録』の8巻"),
    "quote_k2": sz.quote_card("その受け取り方は|今すぐやめられる", "『自省録』の8巻"),
    "moto5": sz.book_now("02_point", "提要の5番目", bubble="そっくり"),
    "quote": sz.quote_card("不安にするのは出来事じゃなく|考え方だ", "『提要』の5番目"),
    "quote5a": sz.quote_card("知らない人は人のせい|習いたては自分のせい", "『提要』の5番目"),
    "quote5b": sz.quote_card("ちゃんと習った人は|どっちも責めない", "『提要』の5番目"),
    "semenai": sz.train_think("03_troubled", "初心者"),
    "semenai2": sz.train_think("05_happy", "責めない側へ"),
    "shuudouin": sz.copyists("01_base"),
    "shugyou": sz.book_now("01_base", "修行の本", bubble="欲しがらない練習"),
    "shugyou2": sz.book_now("02_point", "欲しがるな", bubble="ぴったり"),
    "namae": sz.book_now("02_point", "名前を差し替え", bubble="ソクラテス"),
    "namae2": sz.book_now("02_point", "中身はほぼそのまま", bubble="聖パウロ"),
    "insatsu": sz.book_now("01_base", "1000年以上", bubble="手で写して残った"),
    "ima": sz.counselor("02_point", "心の治療"),
    "ellis": sz.counselor("02_point", "アルバート・エリス"),
    "kako": sz.counselor("03_troubled", "過去を掘る"),
    "kako2": sz.calendar_one("02_point", "過去", "×", bubble="変えられない"),
    "imakangae": sz.counselor("02_point", "いまの考えを直す"),
    "tehon": sz.book_now("02_point", "5番目の一文", bubble="手本"),
    "tehon2": sz.quote_card("出来事じゃなく|考え方だ", "『提要』の5番目"),
    "cbt": sz.counselor("01_base", "認知行動療法"),
    "cbt2": sz.counselor("05_happy", "考え方のクセを直す"),
    "onaji3": sz.counselor("05_happy", "エリスも同じ"),
    "abc": sz.memo_tag("02_point", "もうダメだ、を書く"),
    "abc2": sz.memo_tag("02_point", "本当?"),
    "abc3": sz.memo_tag("02_point", "証拠は?"),

    # ---- 幕6 動作 → 締め
    "memo": sz.memo_write("05_happy"),
    "rei": sz.memo_tag("05_happy", "昨日の件、直します"),
    "iwanami": sz.book_now("05_happy", "人生談義 下", bubble="岩波文庫"),
    "youroku": sz.book_now("02_point", "要録", bubble="後ろのほう"),
    "comment": sf.cta("", "02_point", show_comment=True, bubble="なに書いた?"),
    "tana": sz.go_home("05_happy"),
}

for _k in ("toi", "kangae", "yaku"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# ナレーション = 字幕。30カット(2026-09-05 ユーザー「学びがほぼない」→ 誰が・なぜ残った・誰が評価した、を足した)。
# 2026-09-04 ユーザー「ガチで何言ってんの?」(『変えられることと変えられないこと、分けてみない?』
# 『これ、考えたの1900年前の奴隷なんだって』)。**「表」という仕掛けは、前情報ゼロの人には
# 5周直しても通らなかった**ので捨てた。考え方を視聴者の場面の言葉で先に言い切り、
# 奴隷は**出どころ**として最後に置く(「実はこの考え方、〜が言い出したんだって」)。
UNITS = [
    Unit("toi", "上司の一言、帰りの電車でまだ引きずってる?", anim=1.7, cover=True,
         se="pop", speed=1.13, intonation=1.25, pad=0.06, chara="none"),
    Unit("kangae", "上司にああ言えばよかったって、まだ考えてる?", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.06, chara="none"),
    Unit("yaku", "それ考えてて、明日なんか変わる?", anim=1.7, speed=1.15,
         intonation=1.25, pad=0.08, chara="none"),
    Unit("tatanai", "いや、ないよね。", anim=1.5, speed=1.13,
         intonation=1.2, pad=0.08, chara="none"),
    Unit("batsu", "だって、もう言っちゃったことは変えられない。", anim=1.7,
         se="don", speed=1.13, intonation=1.3, pad=0.10, chara="none"),
    Unit("ugokanai", "で、変えられないなら、考えてもしょうがなくない?", anim=1.7,
         speed=1.15, intonation=1.1, pad=0.06, chara="none"),
    Unit("sanko", "たとえば上司の機嫌とか、周りがどう思うかもそう。", anim=1.7,
         speed=1.15, intonation=1.15, pad=0.06, chara="none"),
    Unit("hyouka2", "上司の評価も、自分じゃ決められないし。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("q", "じゃあ、自分で変えられるものって何?", anim=1.7, speed=1.15,
         intonation=1.25, pad=0.08, chara="none"),
    Unit("hitokoto", "答えは、明日、上司になに言うか。それだけ。", anim=1.7,
         speed=1.13, intonation=1.25, pad=0.08, chara="none"),

    # ---- 誰が言ったか。考え方の一般文 → 元奴隷 → 名前 → 流派 → 持ち主 → 教え → 弟子の本
    Unit("kangaenai", "だから、変えられないことは考えない。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("dare", "これ、1900年前のローマの元奴隷が言ってたことなんだよ。", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("epi", "エピクテトスって元奴隷の人。ストア派って聞いたことある?", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("stoa", "ストア派は『ストイック』の元だけど、中身は我慢じゃないの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("stoa2", "中身は、変えられないものは欲しがるな、って教えなの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("epi2", "で、エピクテトスのご主人、誰だと思う? 皇帝ネロの秘書。", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("mochimono", "奴隷だから、体も持ち物も、ぜんぶご主人のもの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("kazoeru", "でも、何を考えるかまでは、ご主人にも決められないじゃん?", anim=1.7, speed=1.13, intonation=1.3, pad=0.12, se='don', chara="none"),
    Unit("jugyou", "で、ご主人も元奴隷で、哲学の授業に行かせてくれたんだって。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("sensei", "自由になって哲学の先生になった。教えたのは、これ。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("hyouban", "先生の教えは、体も持ち物も評判も自分のものじゃない、って。", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("hyouban2", "で、自分のものは、どう思うかだけ。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("kakanai", "でも先生なのに、本は1冊も書いてない。意外でしょ?", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("deshi", "で、弟子のアリアノスって人が授業のメモを本にしたの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("teiyou2", "そのメモが『提要』って薄い本で、教えが53個。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),

    # ---- なぜ残ったか(皇帝)
    Unit("utsusu", "で、昔の本って、誰かが手で写さないと消えるでしょ?", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("naze", "なのに、なんで1900年も残ったと思う? 読んだ人と写した人がいたから。", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("koutei", "で、ネロよりずっと後のローマ皇帝も読んでたんだよ。", anim=1.7, speed=1.13, intonation=1.25, pad=0.1, se='don', chara="none"),
    Unit("koutei2", "マルクス・アウレリウスって皇帝。『自省録』って、自分だけのノートを書いてて。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("jiseiroku", "そのノートに、若い頃の先生にありがとう、って書いてるの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("jiseiroku2", "で、先生はエピクテトスの本を貸してくれた人なんだって。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("jinchuu", "しかもそのノート、戦争に行ってる最中に書いてるの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("ekibyou2", "戦争も流行り病も皇帝でも止められない。上司の機嫌と同じでしょ?", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("onaji", "で、皇帝もエピクテトスとそっくりなこと書いてて。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("quote_k", "皇帝は「つらいのは出来事より受け取り方だ」って。", anim=1.9, speed=1.13, intonation=1.25, pad=0.1, chara="none"),
    Unit("quote_k2", "で、「その受け取り方は今すぐやめられる」って。できそう?", anim=1.7, speed=1.13, intonation=1.25, pad=0.1, chara="none"),

    # ---- 提要5(誰が評価した: 皇帝と同じ文)
    Unit("quote", "そして『提要』の5番目も「不安にするのは出来事じゃなく、考え方だ」。", anim=1.9, speed=1.13, intonation=1.25, pad=0.08, chara="none"),
    Unit("quote5a", "で、「知らない人は人のせい、習いたては自分のせい」って。", anim=1.7, speed=1.13, intonation=1.2, pad=0.08, chara="none"),
    Unit("quote5b", "で、「ちゃんと習った人はどっちも責めない」って。", anim=1.7, speed=1.13, intonation=1.25, pad=0.12, se='don', chara="none"),
    Unit("semenai", "だから、いま自分を責めてるあなたは初心者。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("semenai2", "で、明日から、どっちも責めない側に行こ。", anim=1.7, speed=1.15, intonation=1.25, pad=0.10, chara="none"),

    # ---- 修道院
    Unit("shuudouin", "で、写したのは修道院。皇帝のあと、この本を修行に使って写し続けたの。", anim=1.7, speed=1.15, intonation=1.15, pad=0.08, chara="none"),
    Unit("shugyou", "修行って、自分のじゃないものを欲しがらない練習なんだって。", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("shugyou2", "欲しがるな、って本だから、練習にぴったりでしょ?", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("namae", "で、変えたのは中に出てくるソクラテスって人の名前くらい。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("namae2", "名前をキリスト教の聖人パウロに替えて、中身はそのまま。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("insatsu", "で、元の本も印刷の時代まで1000年以上、修道院が写して残ったの。", anim=1.7, speed=1.15, intonation=1.15, pad=0.08, chara="none"),

    # ---- エリス(誰がなぜ評価した)
    Unit("ima", "しかも、いまの心の治療の元の一つでもあるんだよ。知ってた?", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("ellis", "治療の元にした人が、アルバート・エリスって心理学者。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("kako", "エリスも前は、子どもの頃の話を何年も掘り返す治療してたの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("kako2", "でも過去は変えられないでしょ?", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("imakangae", "だからエリスは1955年、いまの考えを直す治療に変えたの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("tehon", "治療の手本の一つが『提要』5番目「出来事じゃなく考え方」。", anim=1.9, se='don', speed=1.13, intonation=1.25, pad=0.10, chara="none"),
    Unit("cbt", "で、エリスの治療が、いまの認知行動療法の元の一つなの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("cbt2", "考え方のクセを直す治療。あなたも聞いたことない?", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("abc", "治療だと「上司の一言でもうダメ」って考えを紙に書くの。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("abc2", "で、それ本当? って確かめるの。", anim=1.7, speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("abc3", "いや、本当じゃないよね。一言でぜんぶダメになった証拠、無いでしょ?", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),

    # ---- 動作 → 締め
    Unit("memo", "だからあなたも、明日なに言うかをメモに1行書いてみ?", anim=1.7, speed=1.15, intonation=1.25, pad=0.06, chara="none"),
    Unit("rei", "たとえば上司に『昨日の件、もう一回話せますか』だけでいいよ。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("comment", "で、書けたら、なに書いたかコメントで教えて。", anim=1.7, speed=1.13, intonation=1.2, pad=0.06, chara="none"),
    Unit("iwanami", "ちなみに『提要』は、岩波文庫『人生談義』の下巻にあるよ。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("youroku", "下巻の後ろのほうに『要録』って名前で入ってるよ。", anim=1.7, speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("tana", "で、あなたは今日のことは忘れて、明日の一言だけ持って帰ろ。", anim=1.7, speed=1.13, intonation=1.2, pad=0.08, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z001.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
