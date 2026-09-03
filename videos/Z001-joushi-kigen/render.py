#!/usr/bin/env python3
"""Z001「上司の機嫌は、あなたの仕事じゃない」

チャンネル「ヤケに心理学に詳しいずんだもん」の1本目。企画書は plan.md。
型は docs/channel-zunda/strategy.md:

- 1コマ目 = **場面1行 + 二択**(×はまだ付けない)
- **5秒以内に判定**(二択の片方に×)
- 判定の直後に**根拠の見出し**を1行(人名・書名はその後)
- 締めは**手が動く動作**(明日の一文をメモに1行)

**計算が無い回なので verify.py は無い**(strategy §5.3)。
声に出す数は「1900年前」の1つだけで、plan.md の前提表に根拠と出典がある。

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

TITLE = "自分次第のもの"
BADGE = "※ 出典はエピクテトス『提要』1(2世紀前半)"
F.use_fp_theme(TITLE, speaker=3, badge=BADGE)      # 3 = ずんだもん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

SCENES = {
    # ---- 幕1 場面 + 二択。**×はまだ付けない**(片方は視聴者がいまやっている側)
    "toi": sf.person("03_troubled", height=0.46),
    # line1 = 問い(check_toi はここを見る)/ line2 = 墨帯のフック /
    # line3 = 赤ブロック(いまやっている側)/ alt_val = 緑ブロック(もう片方)
    #
    # **フックは6字まで。**scenes_fp の墨帯は高さ 0.135 に対して行送りが 0.081 で、
    # 2行になると 0.162 で帯からはみ出す(実測。2026-09-02)
    "toi__cover": sf.cover("上司の一言、まだ考えてる?",
                           "上司の一言", "考える",
                           name="03_troubled",
                           main_lab="いまのあなた",
                           alt_val="考えない", alt_lab="どっち?",
                           disclaimer="※ 出典はエピクテトス『提要』1(2世紀前半)"),

    # ---- 幕2 判定(5秒以内)
    "hantei": sf.compare("考える", "考えない", "いまのあなた", "こっち?",
                         title="帰り道でやること", role="neutral"),
    # **図だけが持つ情報**: ×が付いても「気にするな」ではないこと
    "batsu": sf.hero("考える", "やめろ、ではないのだ", name=None, role="loss",
                     count=False),

    # ---- 幕3 根拠の見出し(数字も人名も書名もまだ出さない)
    "mukashi": sf.hero("同じ答え", "ずっと昔の本にも", name=None,
                       role="neutral", count=False, size="reference"),

    # ---- 幕4 仕組み。世の中を2つに分ける
    "wakeru": sf.formula("自分次第のもの + そうでないもの", name=None,
                         answer="世の中", title="まず2つに分ける"),
    "jibun1": sf.hero("自分次第のもの", "1つ目", name=None,
                      role="gain", count=False, size="reference"),
    "jibun2": sf.formula("自分の言い方 + 出す物", name=None,
                         answer="自分次第のもの", title="1つ目の中身"),
    "hoka1": sf.hero("そうでないもの", "2つ目", name=None,
                     role="loss", count=False, size="reference"),
    "hoka2": sf.formula("天気 + 他人の機嫌", name=None,
                        answer="自分次第じゃない", title="2つ目の中身"),
    "kigen": sf.hero("上司の機嫌", "入るのはこっち", name=None, role="loss",
                     count=False),
    "ugokanai": sf.hero("動かせない", "考えても", name=None,
                        role="loss", count=False, size="reference"),

    # ---- 幕5 正直の幕。困るのは本当だと認める
    "hyouka_q": sf.person_bubble("03_troubled", "じゃあ評価は?"),
    "hyouka_a": sf.hero("上司が決める", "評価を", name=None,
                        role="loss", count=False, size="reference"),
    "komaru": sf.hero("そのとおり", "だから困るのだ", name=None,
                      role="loss", count=False, size="reference"),

    # ---- 幕6 根拠の実年(**数字はここで初めて出す**)
    "hon": sf.person_bubble("02_point", "本に書いてあるのだ"),
    "seiki": sf.hero("2世紀前半", "本が書かれたのは", name=None,
                     role="neutral", count=False, size="reference"),
    "nen": sf.arrow("2世紀前半", "1900年前", "書かれた", "いまから",
                    title="この分け方の出どころ", role="neutral"),

    # ---- 幕7 残るもの
    "kawaranai": sf.hero("変わっていない", "1900年前から分け方は", name=None,
                         role="neutral", count=False, size="reference"),
    "nokoru": sf.compare("明日の一文", "上司の機嫌", "動かせる",
                         "動かせない", title="帰り道で考えるなら?", role="neutral"),
    "hitokoto": sf.hero("一文だけ", "明日いちばん最初に言う", name=None,
                        role="gain", count=False),

    # ---- 幕8 動作
    # **図だけが持つ情報**: いつまでにやるか(乗り換えまで)
    "memo": sf.formula("明日の一文 → メモ", name=None,
                       answer="乗り換えまでに", title="今日やること"),
    "ichigyo": sf.hero("1行", "書くのはこれだけ", name=None,
                       role="gain", count=False, size="reference"),
    "kyou": sf.hero("もう考えない", "書けたら、今日は", name=None,
                    role="gain", count=False, size="reference"),
    "hikaku": sf.compare("明日の一文", "上司の一言", "考えるのは",
                         "考えないのは", title="帰り道の持ち物", role="neutral"),
    "cta": sf.cta("", "02_point", show_comment=True, bubble="決まったのだ?"),
}

# 免責は先頭の数カットだけ(根拠が画面に出るまで)
for _k in ("toi", "hantei", "batsu"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# ナレーション = 字幕。24ユニット。
# **1カット2.4秒以下**(check_tempo)。1カットに2つのことを言わせない。
# 図が主役なので立ち絵は none(person / person_bubble のカットは図の中に居る)。
UNITS = [
    # --- 幕1 場面 + 二択(0〜3秒)
    Unit("toi", "上司の一言、まだ考えてる?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.25, pad=0.06, chara="none"),

    # --- 幕2 判定(5秒以内に片方へ×)
    Unit("hantei", "その一言、考える?考えない?", anim=1.0, speed=1.10,
         intonation=1.25, pad=0.06, chara="none"),
    Unit("batsu", "実は、ばつが付くのは【考える】。", anim=1.0, se="don",
         speed=1.08, intonation=1.3, pad=0.10, chara="none"),

    # --- 幕3 根拠の見出し(数字はまだ出さない)
    Unit("mukashi", "答えは、昔の本に書いてあるのだ。", anim=1.0,
         speed=1.10, intonation=1.15, pad=0.06, chara="none"),

    # --- 幕4 仕組み
    Unit("wakeru", "まず、世の中を2つに分けるのだ。", anim=1.0, speed=1.10,
         intonation=1.1, pad=0.06, chara="none"),
    Unit("jibun1", "では1つ目、自分次第のもの。", anim=1.0, speed=1.10,
         pad=0.06, chara="none"),
    Unit("jibun2", "それは、言い方と、出す物。", anim=1.0, speed=1.10,
         pad=0.06, chara="none"),
    Unit("hoka1", "一方、自分次第じゃないもの。", anim=1.0, speed=1.10,
         pad=0.06, chara="none"),
    Unit("hoka2", "たとえば、天気や他人の機嫌。", anim=1.0, speed=1.10,
         pad=0.06, chara="none"),
    Unit("kigen", "上司の機嫌も、こっちなのだ。", anim=1.0, se="don",
         speed=1.08, intonation=1.2, pad=0.10, chara="none"),
    Unit("ugokanai", "上司の機嫌は、動かせないのだ。", anim=1.0, speed=1.05,
         intonation=1.15, pad=0.10, chara="none"),

    # --- 幕5 正直の幕
    Unit("hyouka_q", "じゃあ、評価はどうなるのだ?", anim=1.0, speed=1.10,
         intonation=1.25, pad=0.06, chara="none"),
    Unit("hyouka_a", "評価を決めるのは上司。", anim=1.0, speed=1.08,
         pad=0.06, chara="none"),
    Unit("komaru", "だから困りごとが残るのだ。", anim=1.0, speed=1.05,
         intonation=1.15, pad=0.12, chara="none"),

    # --- 幕6 根拠の実年。**数字はここで初めて出す**
    Unit("hon", "答えは、やっぱり本にあるのだ。", anim=1.0, speed=1.10,
         intonation=1.15, pad=0.06, chara="none"),
    Unit("seiki", "その本が書かれたのは、2世紀前半。", anim=1.0, speed=1.08,
         pad=0.06, chara="none"),
    Unit("nen", "2世紀前半は、いまから【1900年前】。", anim=1.2, se="don",
         speed=1.05, intonation=1.3, pad=0.12, chara="none"),

    # --- 幕7 残るもの
    Unit("kawaranai", "分け方は、1900年前から変わらない。", anim=1.0,
         speed=1.08, intonation=1.15, pad=0.06, chara="none"),
    Unit("nokoru", "その分け方で動かせるのは、1つだけ。", anim=1.0, speed=1.08,
         intonation=1.2, pad=0.06, chara="none"),
    Unit("hitokoto", "動かせる1つが、明日の【一文】。", anim=1.2,
         se="don", speed=1.05, intonation=1.3, pad=0.12, chara="none"),

    # --- 幕8 動作
    Unit("memo", "一文が決まったら、メモに1行。", anim=1.0, speed=1.08,
         intonation=1.15, pad=0.06, chara="none"),
    Unit("ichigyo", "書くのは1行だけなのだ。", anim=1.0, speed=1.10,
         pad=0.06, chara="none"),
    Unit("kyou", "1行書けたら、今日は終わりなのだ。", anim=1.0, speed=1.08,
         pad=0.06, chara="none"),
    Unit("hikaku", "上司の一言より、明日の一文なのだ。", anim=1.0, speed=1.05,
         intonation=1.2, pad=0.06, chara="none"),
    Unit("cta", "上司の一言、まだ考えてるならコメントで教えてなのだ。", anim=1.0, speed=1.05,
         intonation=1.2, pad=0.06, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z001.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
