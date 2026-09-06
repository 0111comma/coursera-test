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
BADGE = "※ 出典はエピクテトス『提要』1・5、『自省録』1・8"
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
                           disclaimer="※ 出典はエピクテトス『提要』1・5、『自省録』1・8"),
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
    "dare": sz.who_silhouette("04_surprised"),
    "epi": sz.ancient_person("04_surprised", "エピクテトス", "奴隷だった"),
    "epi2": sz.owned("04_surprised"),
    "mochimono": sz.owned("03_troubled"),
    "kazoeru": sz.slave_sees("05_happy"),
    "sensei": sz.ancient_person("05_happy", "哲学の先生", "自由になったあと"),
    "kakanai": sz.book_cross("01_base"),
    "deshi": sz.memo_tag("02_point", "弟子のメモ"),
    "teiyou": sz.book_now("02_point", "提要"),
    "teiyou2": sz.book_now("02_point", "53の短い話", bubble="薄い本"),

    # ---- 幕5 なぜ残った・誰が評価した(皇帝 → 修道院 → いま)
    "naze": sz.book_now("03_troubled", "提要", bubble="なんで残った?"),
    "koutei": sz.emperor("04_surprised", "ローマ皇帝"),
    "jiseiroku": sz.emperor("02_point", "ローマ皇帝", bubble="ありがとう"),
    "jiseiroku2": sz.book_now("02_point", "貸してくれた本", bubble="先生に"),
    "ekibyou": sz.emperor("03_troubled", "ローマ皇帝", bubble="止められない"),
    "onaji": sz.lineage("01_base"),
    "shuudouin": sz.copyists("01_base"),
    "insatsu": sz.book_now("01_base", "1000年以上", bubble="写し続けた"),
    "ima": sz.counselor("02_point", "心の治療"),
    "cbt": sz.counselor("01_base", "考え方のクセを直す"),
    "quote": sz.quote_card("人を不安にするのは|出来事じゃない", "『提要』の5番目"),
    "quote2": sz.quote_card("出来事についての|自分の考えだ", "『提要』の5番目"),
    "atama": sz.train_think("03_troubled", "自分の頭のほう"),
    "naoseru": sz.counselor("05_happy", "頭の中なら直せる"),
    "abc": sz.memo_tag("02_point", "出来事→考え→気持ち"),
    "onaji2": sz.train_think("02_point", "明日の一言だけ"),

    # ---- 幕6 動作 → 締め
    "memo": sz.memo_write("05_happy"),
    "iwanami": sz.book_now("05_happy", "人生談義 下", bubble="岩波文庫"),
    "tana": sz.go_home("05_happy"),
    "cta": sf.cta("", "02_point", show_comment=True, bubble="なに書いた?"),
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
    Unit("sanko", "たとえば上司の機嫌とか、周りの評判とかもね。", anim=1.7,
         speed=1.15, intonation=1.15, pad=0.06, chara="none"),
    Unit("hyouka2", "上司の評価も、自分じゃ決められないし。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("q", "じゃあ、自分で変えられるものって何?", anim=1.7, speed=1.15,
         intonation=1.25, pad=0.08, chara="none"),
    Unit("hitokoto", "答えは、明日、上司になに言うか。それだけ。", anim=1.7,
         speed=1.13, intonation=1.25, pad=0.08, chara="none"),

    # ---- 誰が言ったか。入口は名前ではなく矛盾(体すら自分のものでない人が言った)
    Unit("dare", "で、これ最初に言った人、1900年前の奴隷なんだよ。", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("epi", "奴隷の名前はエピクテトス。聞いたことある?", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("epi2", "エピクテトスを買ったのは、ローマ皇帝ネロの秘書。", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("mochimono", "だから体も持ち物も、ぜんぶ秘書のもの。ひどくない?", anim=1.7,
         speed=1.15, pad=0.06, chara="none"),
    Unit("kazoeru", "なのに、どう思うかは取れない。頭の中にあるから。", anim=1.7,
         speed=1.13, intonation=1.25, pad=0.10, chara="none"),
    Unit("sensei", "そのあと自由になって、哲学の先生になったんだって。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("kakanai", "でも先生なのに、本は1冊も書いてない。なんでだと思う?", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("deshi", "で、本にしたのが弟子のアリアノス。授業のメモだよ。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("teiyou", "メモが『提要』っていう本になった。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("teiyou2", "『提要』は、短い話が53個だけの薄い本。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),

    # ---- なぜ残ったか・誰が評価したか
    Unit("naze", "で、なんで1900年も残ったと思う?", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("koutei", "まず、読んでたのがローマの皇帝。マルクス・アウレリウスって人。", anim=1.7,
         se="don", speed=1.13, intonation=1.25, pad=0.10, chara="none"),
    Unit("jiseiroku", "皇帝が自分のノートに、ありがとうって書いてる。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("jiseiroku2", "で、相手は本を貸してくれた先生。皇帝がね。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("ekibyou", "皇帝でも、病気も戦争も止められないでしょ?", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("onaji", "だから、何も動かせない奴隷と同じ答えになったんだって。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("shuudouin", "奴隷の本は、修道院が修行の本に書き直して残した。", anim=1.7,
         speed=1.15, intonation=1.15, pad=0.08, chara="none"),
    Unit("insatsu", "で、印刷ができるまで、1000年以上写し続けた。", anim=1.7,
         speed=1.15, intonation=1.15, pad=0.08, chara="none"),
    Unit("ima", "で、いまの心の治療の元にもなってるの、知ってた?", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("cbt", "認知行動療法って聞いたことある? 考え方のクセを直す治療。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("quote", "治療の元は、「人を不安にするのは出来事じゃない」って言葉。", anim=1.9,
         speed=1.13, intonation=1.25, pad=0.10, chara="none"),
    Unit("quote2", "「出来事についての、自分の考えだ」。", anim=1.7, se="don",
         speed=1.13, intonation=1.25, pad=0.12, chara="none"),
    Unit("atama", "つまり、出来事より、しんどいのは自分の頭のほう。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("naoseru", "で、頭の中なら直せるでしょ? だから治療になったんだって。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("abc", "治療では、出来事と気持ちのあいだの考えを、紙に書かせるの。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("onaji2", "で、電車のあなたも同じ。変えられるのは明日の一言だけ。", anim=1.7,
         speed=1.13, intonation=1.2, pad=0.08, chara="none"),

    # ---- 動作 → 締め
    Unit("memo", "だから今夜、なに言うかをメモに1行書いてみ?", anim=1.7, speed=1.15,
         intonation=1.25, pad=0.06, chara="none"),
    Unit("iwanami", "ちなみに『提要』は、岩波文庫『人生談義』の下巻で読めるよ。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("tana", "書けたら、もう上司のことは気にしないで帰ろ。", anim=1.7, speed=1.13,
         intonation=1.2, pad=0.08, chara="none"),
    Unit("cta", "で、なに書いたかコメントで教えて。", anim=1.7, speed=1.13,
         intonation=1.2, pad=0.06, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z001.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
