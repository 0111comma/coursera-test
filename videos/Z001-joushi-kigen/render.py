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
BADGE = "※ 出典: 『提要』第1章・第5章 /『自省録』第8巻47節 / 論理療法(1955)"
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
                           disclaimer="※ 出典: 『提要』第1章・第5章 /『自省録』第8巻47節 / 論理療法(1955)"),
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
    "stoa": sz.train_think("02_point", "力が及ぶ範囲"),
    "stoa2": sz.train_think("02_point", "権内"),
    "epi2": sz.owned("04_surprised"),
    "mochimono": sz.owned("03_troubled"),
    "kazoeru": sz.slave_sees("05_happy"),
    "jugyou": sz.ancient_person("01_base", "哲学の授業", "ご主人も元奴隷"),
    "sensei": sz.ancient_person("05_happy", "エピクテトス", "ストア派"),
    "hyouban": sz.boss_crowd("01_base"),
    "hyouban2": sz.slave_sees("02_point"),
    "kakanai": sz.book_cross("01_base"),
    "deshi": sz.memo_tag("02_point", "弟子のメモ"),
    "goroku": sz.book_now("02_point", "『語録』", bubble="授業のメモ"),
    "teiyou2": sz.book_now("02_point", "53章", bubble="薄い本"),

    # ---- 幕5 なぜ残った(皇帝)→ 提要5 → 修道院 → エリス
    "utsusu": sz.book_now("03_troubled", "手で写す", bubble="写さないと消える"),
    "naze": sz.book_now("03_troubled", "『提要』", bubble="なんで残った?"),
    "naze2": sz.lineage("02_point"),
    "koutei": sz.emperor("04_surprised", "ずっとあとの皇帝"),
    "koutei2": sz.emperor("02_point", "マルクス・アウレリウス"),
    "koutei4": sz.emperor("02_point", "ローマ皇帝", bubble="先生へのお礼"),
    "koutei3": sz.book_now("02_point", "『自省録』", bubble="自分だけのノート"),
    "jiseiroku": sz.emperor("01_base", "ローマ皇帝", bubble="先生にありがとう"),
    "jiseiroku2": sz.book_now("02_point", "『語録』", bubble="若いころの先生"),
    "jinchuu": sz.emperor("03_troubled", "ローマ皇帝", bubble="戦争の陣中で"),
    "ekibyou2": sz.emperor("04_surprised", "ローマ皇帝", bubble="止められない"),
    "onaji": sz.lineage("01_base"),
    "quote_k": sz.quote_card("出来事じゃなく|その判断だ", "『自省録』第8巻47"),
    "quote_k2": sz.quote_card("消すのは|権内にある", "『自省録』第8巻47"),
    "moto5": sz.book_now("02_point", "『提要』第5章", bubble="そっくり"),
    "kennai": sz.slave_sees("02_point"),
    "quote": sz.quote_card("出来事じゃなく|その考えだ", "『提要』第5章"),
    "quote5a": sz.quote_card("習ってない人は|他人のせい", "『提要』第5章"),
    "quote5b0": sz.quote_card("習い始めの人は|自分のせい", "『提要』第5章"),
    "quote5b": sz.quote_card("習い終えた人は|人も自分も責めない", "『提要』第5章"),
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
    "tehon": sz.book_now("02_point", "第5章の一文", bubble="エリスの手本"),
    "tehon2": sz.quote_card("出来事じゃなく|考え方だ", "『提要』第5章"),
    "cbt": sz.counselor("01_base", "認知行動療法"),
    "cbt2": sz.counselor("05_happy", "考え方のクセを直す"),
    "onaji3": sz.counselor("05_happy", "エリスも同じ"),
    "abc0": sz.memo_tag("02_point", "A→B→C"),
    "abc": sz.memo_tag("02_point", "A・B・C"),
    "abc2": sz.memo_tag("02_point", "論駁"),
    "abc3": sz.memo_tag("02_point", "出来事→考え"),


    # ---- 幕6 動作 → 締め
    "memo": sz.memo_write("05_happy"),
    "rei": sz.memo_tag("05_happy", "昨日の件"),
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
    # ---- 幕1 場面 → 判定 → 答え(8)
    Unit("toi", "上司の一言、帰りの電車でまだ引きずってる?", anim=1.7, cover=True,
         se="pop", speed=1.28, intonation=1.25, pad=0.06, chara="none"),
    Unit("kangae", "しかも家に着いてから、言い返す用のセリフまで考えてるやつ。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.06, chara="none"),
    Unit("yaku", "セリフをいくら考えたって、明日なにか変わる?", anim=1.7, speed=1.30,
         intonation=1.25, pad=0.05, chara="none"),
    Unit("tatanai", "変わんないよね。明日になっても、言われたことは動かせない。", anim=1.7, speed=1.28,
         intonation=1.2, pad=0.08, chara="none"),
    Unit("hyouka2", "たとえば上司の機嫌も、あなたの評価も、決めるのは相手でしょ。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("q", "じゃあ、自分で変えられるものって何?", anim=1.7, speed=1.30,
         intonation=1.3, pad=0.12, chara="none"),
    Unit("hitokoto", "答えは、明日、上司になに言うかだけ。", anim=1.9,
         se="don", speed=1.28, intonation=1.3, pad=0.12, chara="none"),
    Unit("kangaenai", "上司の機嫌みたいな、自分で変えられないものは放っとこ。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),

    # ---- 幕2 その分け方に名前がある(7)。**定訳は名乗ったら必ず崩す**
    Unit("epi", "この考え方を言い出したのが、1900年前の元奴隷、エピクテトス。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("sensei", "エピクテトスは「ストイック」の語源、ストア派の先生ね。", anim=1.5, speed=1.28, intonation=1.2, pad=0.05, chara="none"),
    Unit("stoa2", "ストア派では、変えられるものを「権内にある」って言うの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("stoa", "権内は、自分の力が及ぶ範囲ってことね。", anim=1.5, speed=1.28, intonation=1.2, pad=0.05, chara="none"),
    Unit("hyouban", "権内にないって並べたのは、体・持ち物・評判・地位。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("kennai", "上司の機嫌も、あなたの評価も、権内にない側なの。", anim=1.7, speed=1.30, intonation=1.25, pad=0.06, chara="none"),

    # ---- 幕3 なぜこの人がこの分け方にたどりついたか(3)
    Unit("mochimono", "その体も持ち物も、奴隷のころは自分のものじゃなかった。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("kazoeru", "でも、頭の中の考えだけは、主人にも取り上げられない。", anim=1.7, speed=1.28, intonation=1.3, pad=0.10, chara="none"),
    Unit("hyouban2", "だから権内の側だけ相手にしろ、って教えたの。", anim=1.9, speed=1.28, intonation=1.25, se='don', pad=0.12, chara="none"),

    # ---- 幕4 なぜ残ったか。**書き取ったのは『語録』**(4)
    Unit("naze", "権内の教え方が、1900年たったいまも残ってる。なんでだと思う?", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("kakanai", "実はエピクテトス、自分では1冊も書いてないの。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("deshi", "その授業を書き取った弟子のアッリアノス。本の名は『語録』。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("shuudouin", "『語録』は、キリスト教の修道院が1000年以上写し続けたの。", anim=1.9, speed=1.28, intonation=1.25, se='don', pad=0.08, chara="none"),

    # ---- 幕5 読んだ人(5)。**戦争は皇帝が指揮した側なので使わない。疫病にする**
    Unit("koutei", "『語録』を読んだひとりが、ローマ皇帝、マルクス・アウレリウス。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("ekibyou2", "皇帝でも、国じゅうの流行り病は権内にないでしょ?", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("jinchuu", "権内にないのは、あなたが上司の機嫌を変えられないのと同じ。", anim=1.7, speed=1.30, intonation=1.25, pad=0.06, chara="none"),
    Unit("koutei3", "だから皇帝は、自分だけのノート『自省録』に書いた。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("quote_k", "その一文。「悩ませるのは出来事じゃなく、それへの判断だ」。", anim=1.9, speed=1.28, intonation=1.25, se='don', pad=0.12, chara="none"),

    # ---- 幕6 『提要』5 → エリス(5)。**この一文が現代の治療の土台**
    Unit("moto5", "判断って言葉の元は、『提要』の5番目。自分でも読める本ね。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("quote", "その5番目。「不安にするのは出来事じゃなく、どう考えるかだ」。", anim=1.7, speed=1.28, intonation=1.25, pad=0.05, chara="none"),
    Unit("ima", "5番目を1955年、治療に持ちこんだのがアルバート・エリス。", anim=1.7, speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("cbt2", "エリスは出来事じゃなく、あなたの考え方のクセを直したの。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("cbt", "これが「論理療法」。いまの「認知行動療法」の源流の一つ。", anim=1.9, speed=1.28, intonation=1.25, se='don', pad=0.10, chara="none"),

    # ---- 幕7 束ね → 動作 → 締め(5)。**答えは1つ。#7 と同じ言葉で閉じる**
    Unit("onaji", "この一文が、エピクテトスから皇帝を通っていまの治療になった。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("onaji3", "治療になっても、動かせるのは、あなたが明日なに言うかだけ。", anim=1.7, speed=1.30, intonation=1.25, pad=0.06, chara="none"),
    Unit("memo", "だから今夜のうちに、メモに1行だけ書いてみて。", anim=1.7, speed=1.30, intonation=1.25, pad=0.06, chara="none"),
    Unit("rei", "明日の一言を書くの。「昨日の件、話せますか」。", anim=1.7, speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("tana", "上司の一言は電車に置いてこ。明日の一言だけ持って帰ろ。", anim=1.7, speed=1.28, intonation=1.2, pad=0.05, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z001.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
