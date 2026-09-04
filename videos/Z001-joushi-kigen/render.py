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

OUTDIR = Path(__file__).resolve().parent / "output"

SCENES = {
    # ---- 幕1 場面 + 二択。**×はまだ付けない**
    "toi": sf.person("03_troubled", height=0.46),
    "toi__cover": sf.cover("上司の一言、帰りの電車でまだ引きずってる?",
                           "あの一言", "言えばよかった",
                           name="03_troubled", main_lab="いまのあなた",
                           alt_val="明日の一言", alt_lab="あなたはどっち?",
                           disclaimer="※ 出典はエピクテトス『提要』1(2世紀前半)"),
    "kangae": sf.person_bubble("03_troubled", "あの時…"),

    # ---- 幕2 判定。その考えは明日の役に立たない
    "yaku": sf.hero("明日の役に立つ?", "その考え", name=None,
                    role="neutral", count=False, size="reference"),
    "tatanai": sf.hero("立たない", "明日の役には", name=None, role="loss",
                       count=False, size="reference"),
    "batsu": sf.hero("変えられない", "もう言ったことは", name=None, role="loss",
                     count=False),
    # **図だけが持つ情報**: 帰り道の30分がそこに消えていること
    "ugokanai": sf.compare("考える", "動かない", "変えられないことを", "30分たっても",
                           title="帰り道", role="loss"),
    # **図だけが持つ情報**: 3つとも「他人が決める」側であること
    "sanko": sf.formula("上司の機嫌 + 評判 + 評価", name=None,
                        answer="他人が決める", title="変えられないもの"),

    "hyouka2": sf.hero("評価も", "上司がつける", name=None, role="loss",
                       count=False, size="reference"),

    # ---- 幕3 残るもの
    "q": sf.hero("じゃあ何が?", "残ってるのは", name=None,
                 role="neutral", count=False, size="reference"),
    "hitokoto": sf.hero("明日の一言", "それだけ", name=None, role="gain", count=False),

    # ---- 幕4 出どころ(奴隷)。**答えを出したあと**に置く
    "dare": sf.person_bubble("02_point", "誰?"),
    "dorei": sf.hero("奴隷", "言い出したのは", name=None, role="neutral",
                     count=False, size="reference"),
    # **図だけが持つ情報**: 『提要』が「自分のものではない」に挙げた3項目
    "mochimono": sf.formula("体 + 持ち物 + 役職", name=None,
                            answer="全部主人のもの", title="奴隷"),
    "kazoeru": sf.hero("変えられること", "だけ見て生きた", name=None,
                       role="gain", count=False, size="reference"),
    # **図だけが持つ情報**: 2世紀前半 → いまから1900年前 という引き算
    "hon": sf.arrow("2世紀前半", "いま", "奴隷の考え方", "本に残ってる",
                    title="1900年前から", role="neutral"),

    # ---- 幕5 動作 → 締め
    "konya": sf.hero("決めるだけ", "今夜やるのは", name=None,
                     role="gain", count=False),
    # **図だけが持つ情報**: いつまでにやるか(降りる前に)
    "memo": sf.formula("今夜 → 1行", name=None,
                       answer="降りる前に", title="メモ"),
    "tana": sf.compare("明日の一言", "上司の機嫌", "持ち帰る", "置いていく",
                       title="改札の前で", role="neutral"),
    "cta": sf.cta("", "02_point", show_comment=True, bubble="なに書いた?"),
}

for _k in ("toi", "kangae", "yaku"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# ナレーション = 字幕。19カット。
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
    Unit("dare", "で、この考え方、言い出したの誰だと思う?", anim=1.7,
         speed=1.15, intonation=1.25, pad=0.08, chara="none"),
    Unit("dorei", "実は、1900年くらい前の奴隷の人なんだって。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
    Unit("mochimono", "奴隷は、体も持ち物も、ぜんぶ主人のもの。", anim=1.7, speed=1.15,
         pad=0.06, chara="none"),
    Unit("kazoeru", "でも奴隷は、自分で変えられることだけ見てたんだって。", anim=1.7,
         se="don", speed=1.13, intonation=1.25, pad=0.10, chara="none"),
    Unit("hon", "それが今も本になって残ってるんだよ。", anim=1.7,
         speed=1.15, intonation=1.2, pad=0.08, chara="none"),
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
