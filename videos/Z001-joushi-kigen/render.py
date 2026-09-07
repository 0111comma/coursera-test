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
    "naze2": sz.lineage("02_point"),
    "koutei": sz.emperor("04_surprised", "ずっとあとの皇帝"),
    "koutei2": sz.emperor("02_point", "マルクス・アウレリウス"),
    "koutei4": sz.emperor("02_point", "ローマ皇帝", bubble="先生へのお礼"),
    "koutei3": sz.book_now("02_point", "自省録", bubble="自分だけのノート"),
    "jiseiroku": sz.emperor("01_base", "ローマ皇帝", bubble="先生にありがとう"),
    "jiseiroku2": sz.book_now("02_point", "貸してくれた本", bubble="若いころの先生"),
    "jinchuu": sz.emperor("03_troubled", "ローマ皇帝", bubble="戦争の陣中で"),
    "ekibyou2": sz.emperor("04_surprised", "ローマ皇帝", bubble="止められない"),
    "onaji": sz.lineage("01_base"),
    "quote_k": sz.quote_card("出来事じゃなく|その判断だ", "『自省録』の8巻47"),
    "quote_k2": sz.quote_card("その判断は|いま消せる", "『自省録』の8巻47"),
    "moto5": sz.book_now("02_point", "提要の5番目", bubble="そっくり"),
    "kennai": sz.slave_sees("02_point"),
    "quote": sz.quote_card("出来事じゃなく|考えのほうだ", "『提要』の5番目"),
    "quote5a": sz.quote_card("習ってない人は|他人のせいにする", "『提要』の5番目"),
    "quote5b": sz.quote_card("習い終えた人は|人も自分も責めない", "『提要』の5番目"),
    "semenai": sz.train_think("03_troubled", "初心者"),
    "shuudouin": sz.copyists("01_base"),
    "shuudouin2": sz.book_now("01_base", "修行に使った", bubble="写し続けた"),
    "shugyou": sz.book_now("01_base", "修行の本", bubble="欲しがらない練習"),
    "shugyou2": sz.book_now("02_point", "欲しがるな", bubble="ぴったり"),
    "namae": sz.book_now("02_point", "名前を差し替え", bubble="ソクラテス"),
    "namae2": sz.book_now("02_point", "中身はほぼそのまま", bubble="聖パウロ"),
    "insatsu": sz.book_now("01_base", "1000年以上", bubble="手で写して残った"),
    "ima": sz.counselor("02_point", "心の治療"),
    "ellis": sz.counselor("02_point", "アルバート・エリス"),
    "kako": sz.counselor("03_troubled", "過去を掘る"),
    "kako2": sz.calendar_one("03_troubled", "過去", "×", bubble="良くならない"),
    "imakangae": sz.counselor("02_point", "いまの考えを直す"),
    "tehon": sz.book_now("02_point", "5番目の一文", bubble="エリスの手本"),
    "tehon2": sz.quote_card("出来事じゃなく|考え方だ", "『提要』の5番目"),
    "cbt": sz.counselor("01_base", "認知行動療法"),
    "cbt2": sz.counselor("05_happy", "考え方のクセを直す"),
    "onaji3": sz.counselor("05_happy", "エリスも同じ"),
    "abc0": sz.memo_tag("02_point", "A→B→C"),
    "abc": sz.memo_tag("02_point", "A・B・C"),
    "abc2": sz.memo_tag("02_point", "論駁"),
    "abc3": sz.memo_tag("02_point", "出来事→考え"),


    # ---- 幕6 動作 → 締め
    "memo": sz.memo_write("05_happy"),
    "rei": sz.memo_tag("05_happy", "もう一回話せますか"),
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
         se="pop", speed=1.28, intonation=1.25, pad=0.06, chara="none"),
    Unit("kangae", "上司にああ言えばよかったって、まだ考えてる?", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.06, chara="none"),
    Unit("yaku", "それ考えてて、明日、なにか変わる?", anim=1.7, speed=1.30,
         intonation=1.25, pad=0.05, chara="none"),
    Unit("tatanai", "いや、変わんないよね。", anim=1.5, speed=1.28,
         intonation=1.2, pad=0.05, chara="none"),
    Unit("batsu", "だって、もう言っちゃったことは変えられない。", anim=1.7,
         se="don", speed=1.28, intonation=1.3, pad=0.10, chara="none"),
    Unit("ugokanai", "なら、いくら考えてもしょうがなくない?", anim=1.7,
         speed=1.30, intonation=1.1, pad=0.06, chara="none"),
    Unit("sanko", "たとえば上司の機嫌も、周りの評判も同じ。", anim=1.7,
         speed=1.30, intonation=1.15, pad=0.06, chara="none"),
    Unit("hyouka2", "あなたへの評価も、決めるのは上司だし。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("q", "じゃあ、自分で変えられるものって何?", anim=1.7, speed=1.30,
         intonation=1.25, pad=0.05, chara="none"),
    Unit("hitokoto", "答えは、明日、上司になに言うか。それだけ。", anim=1.7,
         speed=1.28, intonation=1.25, pad=0.05, chara="none"),

    # ---- 誰が言ったか。考え方の一般文 → 元奴隷 → 名前 → 流派 → 持ち主 → 教え → 弟子の本
    Unit("kangaenai", "だから、変えられないことは放っておく。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("dare", "これ、1900年前のローマ帝国の元奴隷の言葉。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("epi", "エピクテトスは元奴隷。ストア派って聞いたことある?", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("stoa", "ストア派は「ストイック」の語源。中身は我慢じゃない。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("stoa2", "ストア派のエピクテトス。変えられるものを「権内」って呼んだの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("kennai", "明日あなたがなに言うかは権内にある。上司の機嫌は権内にない。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("epi2", "そのエピクテトスの主人はね、皇帝ネロの秘書だったの。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("mochimono", "エピクテトスは奴隷だから、体も持ち物もぜんぶ主人のもの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("kazoeru", "でも、何を考えるかは、主人にも決められないじゃん?", anim=1.7, speed=1.28, intonation=1.3, pad=0.12, se='don', chara="none"),
    Unit("jugyou", "主人も「解放奴隷」。エピクテトスを授業に通わせたの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("sensei", "エピクテトスも自由になって、哲学の先生に。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("hyouban", "そして体も持ち物も評判も権内にないって教えたの。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("kakanai", "でも本人は、1冊も書いてないの。意外でしょ?", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("deshi", "本人のかわりに、授業をメモしたのは弟子のアッリアノス。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("teiyou2", "そのメモが『語録』。要点だけ選んだ薄い本が『提要』で53章。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),

    # ---- なぜ残ったか(皇帝)
    Unit("utsusu", "『提要』みたいな昔の本は、だれかが「写本」を作らないと消えるの。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("naze", "なのに1900年も残ったのは、なんで?", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("koutei", "1900年残ったのは、皇帝マルクス・アウレリウスのおかげ。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("koutei3", "皇帝は読んで、自分だけのノートを書きためてた。名前は『自省録』。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("koutei4", "『自省録』の最初は、若い頃の先生へのお礼。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("jiseiroku2", "その先生が皇帝に、エピクテトスのメモを貸したの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("jinchuu", "皇帝は『自省録』を、戦争のまっただ中で書いてた。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("ekibyou2", "皇帝でも、戦争と流行り病は止められない。あなたの上司と同じ。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("onaji", "皇帝が書いてることは、エピクテトスと同じなんだよ。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("quote_k", "皇帝いわく「苦しめるのは出来事じゃなく、その判断だ」。", anim=1.9, speed=1.28, intonation=1.25, pad=0.1, chara="none"),
    Unit("quote_k2", "続けて「その判断は、いま消せる」って。できそう?", anim=1.7, speed=1.28, intonation=1.25, pad=0.1, chara="none"),

    # ---- 提要5(誰が評価した: 皇帝と同じ文)
    Unit("moto5", "「判断」って、受け取り方。『提要』の5番目もそっくり。", anim=1.7, speed=1.28, intonation=1.2, pad=0.05, chara="none"),
    Unit("quote", "5番目は「人を不安にするのは、出来事についての考え」。", anim=1.9, speed=1.28, intonation=1.25, pad=0.05, chara="none"),
    Unit("quote5a", "5番目の続きは「習ってない人は、他人のせいにする」。", anim=1.7, speed=1.28, intonation=1.2, pad=0.05, chara="none"),
    Unit("quote5b", "そして「習い始めは自分のせい。習い終えたら責めない」。", anim=1.7, speed=1.28, intonation=1.25, pad=0.12, se='don', chara="none"),
    Unit("semenai", "だから、いま自分を責めてるあなたは習い始め。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),

    # ---- 修道院
    Unit("shuudouin", "さて『提要』は、皇帝の時代より後も修道院が写し続けたの。", anim=1.7, speed=1.30, intonation=1.15, pad=0.05, chara="none"),
    Unit("shugyou", "修道院の「禁欲」も、自分の力が届かないものを欲しがらない練習。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("namae", "そのとき修道院が変えたのは、ソクラテスの名前くらい。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("namae2", "名前を聖パウロに替えて、中身はほぼそのまま。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("insatsu", "中身を書き替えてない本も、印刷まで1000年以上残った。", anim=1.7, speed=1.30, intonation=1.15, pad=0.05, chara="none"),

    # ---- エリス(誰がなぜ評価した)
    Unit("ima", "その本を、いまの心の治療の土台にした人がいるの。知ってる?", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("ellis", "土台にしたのは、アルバート・エリスって心理学者。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("kako", "エリスも昔はフロイトの「精神分析」。子どもの頃を掘る治療ね。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("imakangae", "精神分析じゃ、患者は良くならない。1955年、「論理療法」を始めた。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("tehon", "エリスは『提要』の5番目を、自分の論理療法の手本にしたの。", anim=1.9, se='don', speed=1.28, intonation=1.25, pad=0.10, chara="none"),
    Unit("cbt", "考え方のクセを直す「認知行動療法」。その始まりが論理療法なの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("abc", "論理療法のやり方をエリスが「ABC理論」にまとめたの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("abc0", "ABC理論では、出来事と考えと気持ちを分けて自分で書くの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("abc3", "Aの出来事は上司の一言。Bの考えが「もうダメだ」。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("abc2", "Bの「もうダメだ」に証拠ある? って問い返すのが「論駁」。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),

    # ---- 動作 → 締め
    Unit("memo", "そしたら今夜、明日なに言うかをメモに1行書いてみ?", anim=1.7, speed=1.30, intonation=1.25, pad=0.06, chara="none"),
    Unit("rei", "たとえば「昨日の件、もう一回話せますか」って書くの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("comment", "その1行が書けたら、コメントで教えて。", anim=1.7, speed=1.28, intonation=1.2, pad=0.06, chara="none"),
    Unit("tana", "今日のことは忘れて、明日の一言だけ持って帰ろ。", anim=1.7, speed=1.28, intonation=1.2, pad=0.05, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z001.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
