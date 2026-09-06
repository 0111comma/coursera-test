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
BADGE = "※ 出典はエピクテトス『提要』1(2世紀前半)"
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
                           disclaimer="※ 出典はエピクテトス『提要』1(2世紀前半)"),
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

    # ---- 幕4 出どころ: 誰が言ったか(エピクテトス)
    "dare": sz.who_silhouette("02_point"),
    "epi": sz.ancient_person("04_surprised", "エピクテトス", "生まれは奴隷"),
    "mochimono": sz.owned("04_surprised"),
    "kazoeru": sz.slave_sees("05_happy"),
    "sensei": sz.ancient_person("05_happy", "哲学の先生", "自由になったあと"),
    "kakanai": sz.book_cross("01_base"),
    "deshi": sz.memo_tag("02_point", "弟子のメモ"),
    "teiyou": sz.book_now("02_point", "提要"),

    # ---- 幕5 なぜ残ったか(皇帝 → 修道院 → いま)
    "naze": sz.book_now("03_troubled", "提要", bubble="なんで残った?"),
    "koutei": sz.emperor("04_surprised", "ローマ皇帝"),
    "jiseiroku": sz.emperor("02_point", "ローマ皇帝", bubble="感謝を書いた"),
    "jiseiroku2": sz.book_now("02_point", "元奴隷の本", bubble="読めてよかった"),
    "shuudouin": sz.copyists("01_base"),
    "ima": sz.counselor("02_point", "心理学"),
    "cbt": sz.counselor("01_base", "考え方のクセを直す"),
    "quote": sz.quote_card("人を不安にするのは|出来事じゃない", "『提要』の5番目"),
    "quote2": sz.quote_card("出来事についての|自分の考えだ", "『提要』の5番目"),
    "keifu": sz.lineage("05_happy"),

    # ---- 幕6 動作 → 締め
    "konya": sz.tonight("02_point"),
    "memo": sz.memo_write("05_happy"),
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
    Unit("hitokoto", "答えは、明日、上司になに言うか。それだけだよ。", anim=1.9, se="don",
         speed=1.13, intonation=1.3, pad=0.12, chara="none"),

    # ---- 誰が言ったか
    Unit("dare", "で、この考え方、言い出したの誰だと思う?", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("epi", "答えはエピクテトス。1900年くらい前のローマの人。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("mochimono", "エピクテトスは生まれつき奴隷。体も持ち物も主人のもの。", anim=1.7,
         speed=1.15, pad=0.06, chara="none"),
    Unit("kazoeru", "でも奴隷のとき、変えられることだけ見てたんだって。", anim=1.7,
         se="don", speed=1.13, intonation=1.25, pad=0.10, chara="none"),
    Unit("sensei", "奴隷が自由になって、哲学の先生になったの知ってた?", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("kakanai", "でも先生なのに、本は1冊も書いてない。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("deshi", "で、本にしたのは弟子のアリアノス。授業のメモなんだって。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("teiyou", "メモが『提要』っていう本になって、いまも読める。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),

    # ---- なぜ残ったか・誰が評価したか
    Unit("naze", "で、なんで1900年も本が残ってると思う?", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("koutei", "まず、読んでたのがローマの皇帝。マルクス・アウレリウスって人。", anim=1.7,
         se="don", speed=1.13, intonation=1.25, pad=0.10, chara="none"),
    Unit("jiseiroku", "皇帝が自分の日記に、感謝を書いてるんだよ。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("jiseiroku2", "元奴隷の本を読めてよかった、って皇帝が。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("shuudouin", "皇帝のあと、修道院の人たちが本を写して1000年つないだ。", anim=1.7,
         speed=1.15, intonation=1.15, pad=0.08, chara="none"),
    Unit("ima", "で、いまは心理学でも使われてるの、知ってた?", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("cbt", "心理学の認知行動療法、考え方のクセを直す治療の元なの。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("quote", "その一言が、「人を不安にするのは、出来事じゃない」。", anim=1.9,
         se="don", speed=1.13, intonation=1.25, pad=0.10, chara="none"),
    Unit("quote2", "「出来事についての、自分の考えだ」。", anim=1.7,
         speed=1.13, intonation=1.25, pad=0.12, chara="none"),
    Unit("keifu", "で、奴隷が言って皇帝が読んで、いま病院にある。すごくない?", anim=1.7,
         speed=1.15, intonation=1.3, pad=0.10, chara="none"),

    # ---- 動作 → 締め
    Unit("konya", "だから今夜、明日なに言うかを決めるだけでいい。", anim=1.7,
         speed=1.13, intonation=1.2, pad=0.08, chara="none"),
    Unit("memo", "で、なに言うか、メモに1行書いてみ?", anim=1.7, speed=1.15,
         intonation=1.25, pad=0.06, chara="none"),
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
