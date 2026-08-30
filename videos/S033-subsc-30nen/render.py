#!/usr/bin/env python3
"""S033: Netflix・Spotify・Amazonプライム。3つで30年いくらか。

P-M(35歳・男性・会社員)の1本目。
**カットは1本ずつ変える。**S032は40.1秒で11カット(3.65秒/カット)で、
競合の1.6〜1.8秒に対して2倍遅かった。check_tempo が落とすようにしてある。

2026-08-30 厳格審査(構成・日本語・コピー・検事)での全面改稿:
- **問いを「合計はいくらか(既知)」から「どれを止めるか(未知・行動)」へ移した。**
  カバーが0秒目に114万円を出しているのに、旧 unit1 は「サブスク3つで、月いくら?」と
  別の問いから始まり、第1幕の10ユニット全部がサムネの答え合わせになっていた
- **表を4カット連続で出すのをやめた**(旧 01〜04 は同一グリッド・同一値で12.8秒)。
  表は3カットに減らし、あいだに構図の違う部品(hero)を挟む
- **缶コーヒーの比較カットを削除した。**「105円 < 缶コーヒー1本」は
  「缶コーヒーは105円より高い」という価格の主張なのに、plan §10 の前提表にも
  verify.py にも缶コーヒーの値が無かった。記号で言い換えても
  「説明していない数字を出さない」の違反は消えない(CLAUDE.md 最優先ゲート)
- **「止めるだけで確定する額」を声に出した**(約39万円)。この動画が求める行動は
  「止める」だけなのに、行動と直結する唯一の額が言葉になっていなかった
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

# 常設ヘッダーは本編の問いを先出ししない(2026-08-30 copy/high)。
# 旧「サブスク3つ、いくら?」は unit1 とほぼ同文で、0秒目に同じ問いが
# 画面に2つ出ていた(片方は完全な死荷重)。ここは主題の名乗りだけにする。
TITLE = "サブスクの30年"
BADGE = "※ 料金は2026年8月時点。運用は年5%と仮定した場合の計算です"
F.use_fp_theme(TITLE, speaker=108, badge=BADGE)      # 東北きりたん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

# 台本に出す値は verify.py と一致していること
assert V.MONTHLY == 3_162 and V.MONTHS == 360
assert V.PRINCIPAL == 1_138_320
assert round(V.DAILY) == 105
assert round(V.FV5 / 10_000) == 263
assert round(V.ONE_FV5 / 10_000) == 90 and round(V.ONE_PRINCIPAL / 10_000) == 39

# **立ち絵はカバーと締め、それに本編の1か所だけ。**(2026-08-24)
_SERVICES_LINE = "Netflix・Spotify・Amazonプライム"
_SERVICES = _SERVICES_LINE.split("・")
_HYO = [["Netflix", "1590円"],
        ["Spotify", "1080円"],
        ["Amazonプライム", "492円"],
        ["合計", "3162円"]]
_HYO_HEAD = ["サービス", "月額"]

SCENES = {
    # ---- カバー(キャラ 1/4)
    "namae": sf.person_cards("03_troubled", _SERVICES,
                             title="30代がよく持つ3つ"),
    # 2026-08-30 厳格審査(thumbnail/high×4・medium×5・low×2):
    # - **下段のチップ3枚とティーザーを削除。**72pxタイルでの実測 ink 高は
    #   2.6〜3.9px で、トップの下限8pxの半分以下。画面高の32%を占めながら
    #   「開く理由」を一切運んでいなかった
    # - 代わりに **既知(赤=114万円)と未知(緑=2??万円)の2ブロック**にする。
    #   旧カバーは問いと答えが同じ画面にあって好奇心の穴がゼロだった
    # - フックから指示語「この」を外す(チップが消えるので先行詞が無くなる。
    #   同時に本編の中核動詞「止める」を0秒目に立てる)
    # - 立ち絵は 03_troubled(頬に手・視線が画面外)→ **04_surprised**。
    #   赤い114万円が要求する衝撃の振幅に困り顔は届かない
    # - 免責はバッジの外の最下部ストリップへ(戦略§6-5 の時点表記は保つ)
    "namae__cover": sf.cover(_SERVICES_LINE,
                             "止めない3つ\n30年で?", "114万円",
                             name="04_surprised",
                             main_lab="止めなければ",
                             alt_val="2??万円", alt_lab="積んでいたら",
                             disclaimer="※ 料金は2026年8月時点。"),

    # ---- 表は**3カットまで**(2026-08-30 retention/high)。
    # 旧 01〜04 は同一グリッド・同一値の表4カット連続(12.8秒)で、カット境界の
    # 図の変化画素が 4.21%/6.02%/3.93%=視聴者には1カットだった。しかも問いの
    # 答え(合計3,162円)が13.0秒まで出なかった。
    # いまは 表(内訳)→ hero(合計)→ 表(合計行の赤)の3カットで、**構図が
    # 1カットおきに変わる**。合計は6秒以内に出る。
    "hyo_a": sf.table(_HYO_HEAD, _HYO, highlight="wave",
                      title="30代がよく持つ3つ", total_mode="dim"),
    # 構図の変更(表 → ヒーロー)。合計をここで初めて開示する
    "goukei": sf.hero("3162円", "3つの合計", name=None, role="loss"),
    # 合計行に赤リング。機構(止めるまで引かれ続ける)を絵でも言う
    "hyo_g": sf.table(_HYO_HEAD, _HYO, highlight=3, title="止めるまで、毎月"),

    # 数式カード: 答え(=の右)をカード内に着地させる
    "waru": sf.formula("3162円 ÷ 30日", name=None, answer="105円",
                       title="小さく見える理由"),
    # **旧 hikaku(缶コーヒーとの比較)を削除した**(2026-08-30 nihongo/high)。
    # 不等号そのものが「缶コーヒーは105円より高い」という価格の主張を担って
    # いたのに、plan §10 にも verify.py にも缶コーヒーの値が無かった。
    # 代わりに、なぜ30年止めなかったのかを**行動**で言うカットにする
    # (視聴者の内心を断定で代弁しない。2026-08-30 copy/medium)
    "hi": sf.hero("105円", "1日あたり", name=None, role="loss", count=False,
                  size="reference"),
    "obi": sf.timeline(35, 65, 65, "ここまで払う", "", show_gap=False,
                       title="30年、つづけると", fill_color=sf.RED_FILL),
    # role="neutral": 360回は中立な回数。size="reference": 参照値は結論より小さく
    # (2026-08-30 artdirection/medium: 二次的な参照値が結論の2〜3倍で描かれていた)
    "kikan": sf.hero("360回", "月3162円を払う回数", name=None,
                     role="neutral", size="reference"),
    "shiki1": sf.formula("3162円 × 360か月", name=None, answer="114万円",
                         title="30年で出ていく額"),

    # ---- 本編で唯一の立ち絵(キャラ 2/4)。いちばん刺す一行に置く
    "toi_oboe": sf.person_bubble("03_troubled", "114万円…?",
                                 title="30年で出ていく額"),

    # tease=1: 答えの棒は**高さを往復させて**予告する(2026-08-30 retention/medium)。
    # 旧実装は114万円棒と同じ高さで止めていたので、カード内の上側79%が3.15秒
    # ずっと空白で、動いているのは緑の「?」1文字だけだった。
    # ymax は 114万×1.9(往復の上端 0.92 でも 1.75倍までしか行かないので、
    # 実際の 2.31倍=263万円を絵で先に漏らさない)
    "tsumu": sf.bars([("積み立てるだけ", 1_138_320, "114万円", {"count": False}),
                      ("年5%と仮定", 1_138_320, "")],
                     highlight=0, tease=1, title="もう一つの使い道",
                     ymax=1_138_320 * 1.9),
    "katei": sf.hero("年5%", "増えると仮定する率", name=None, stamp=True,
                     role="gain",
                     caption="元本保証ではなく、減る年もあります"),
    "fueru": sf.bars([("積み立てるだけ", 1_138_320, "114万円", {"count": False}),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=1, prev_highlight=0, gain=1,
                     title="30年後のちがい"),
    # 見出しは声の「行き先」と一語一致(2026-08-30 copy/high:
    # 図の見出し+箱ラベル2つ+字幕で同じ内容を3層で言っていた)
    "yaji": sf.arrow("114万円", "263万円", "出ていく側", "積み立てる側",
                     title="毎月3162円の行き先", scale_right=1.0, role="gain"),

    # ---- 1つでいい
    # 合計は「止められない=依然として出ていく額」なので RED のまま
    # (2026-08-30 consistency/medium: 15/16 で墨に落ちていた)
    "hyo_x": sf.table(_HYO_HEAD, _HYO, highlight=None,
                      title="3つ全部を止める?"),
    # **特定の行を緑で単独強調しない**(2026-08-30 kousei/high)。
    # 旧 hyo_1 は「使っていない1つ」の見出しの下で Spotify 行だけを緑で
    # 強調していて、声が選択権を視聴者に渡しているのに絵が断定していた
    # (plan §13.3 違反)。表をもう1カット足さず、例示の額は hero で出す
    "hitotsu": sf.hero("1080円", "止める1つの例", name=None, count=False,
                       role="gain", size="reference"),
    # 左=止めれば出ていかない額(確定)/ 右=積んだ場合(予告)。
    # ymax は 39万×1.9(往復の上端でも 1.75倍。実際の 2.31倍は漏らさない)
    "hitotsu2": sf.bars([("出ていかない額", 388_800, "約39万円"),
                         ("年5%で積んだら", 898_839, "")],
                        highlight=0, gain=0, tease=1, title="1つ止めると",
                        ymax=388_800 * 1.9),
    "kyuuju": sf.hero("約90万円", "年5%で積んだ場合", name=None, role="gain"),
    "shiki2": sf.formula("止める1つの月額 × 360か月", "= 【出さずに済む額】",
                         name=None, title="自分の額の求め方",
                         emph_color=sf.GREEN_DARK),

    # ---- 締め(キャラ 3/4・4/4)
    # 時間表現は字幕の「今日」1つに集約する(2026-08-30 copy/medium)
    "meisai": sf.person_bubble("02_point", "1つでいい", rows=_HYO[:3],
                               title="むずかしくない"),
    "cta2": sf.cta("", "02_point", show_comment=True, bubble="決めるだけ",
                   title="あなたの番"),
}

# 「運用は年5%と仮定」の免責は、運用の話が画面に出るまで先頭の一文だけにする
for _k in ("namae", "hyo_a", "goukei", "hyo_g", "waru", "hi", "obi",
           "kikan", "shiki1", "toi_oboe"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

UNITS = [
    # 1文目は plan §4 の問いをそのまま口に出す(check_toi)。
    # **カバーの114万円を1秒目で引き取る**(2026-08-30 kousei/high)。
    # 動画全体の問いを「合計はいくらか(既知)」から
    # 「どれを止めるか(未知・行動)」へ移す。以降の内訳提示は、この問いに
    # 答えるための材料として順接になる。締めの「あなたが止めるサブスク」と
    # 語のループを作る(check_hold H3)
    Unit("namae", "サブスクに払う114万円、どれを止める?", anim=1.0, cover=True,
         cover_hold=0.30, se="pop", speed=1.0, intonation=1.3, chara="none"),
    # 旧3・4を1文に畳んだ(2026-08-30 kousei/medium)。同一グリッドの表4カットで
    # 情報の前進が実質2つしか無く、Shorts の最大離脱帯がここに丸ごと乗っていた
    Unit("hyo_a", "1590円、1080円、492円。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("goukei", "合計、月3162円。", anim=1.0, se="don",
         se_at=sf.landing_sec("hero", 1.0), speed=1.0, intonation=1.2,
         chara="none"),
    # 機構を名指す(2026-08-30 copy/medium)。「毎月」+「続ける」で自動継続が入る
    Unit("hyo_g", "3162円が、あなたから毎月引かれる。", anim=1.0, speed=1.05,
         chara="none"),
    # 画面の式「3162円 ÷ 30日」と動詞で一語一致させる(2026-08-30 nihongo/low:
    # 「1日にする」は「一日に変える」と読める非文だった)
    Unit("waru", "これを30日で割ると、1日105円。", anim=1.0, speed=1.05,
         chara="none"),
    # 断定で視聴者の内心を代弁しない(2026-08-30 copy/medium)。
    # 「開かない」が unit20 の「開いて」と対になる
    Unit("hi", "105円では、わざわざ解約しない。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("obi", "35歳なら、65歳まであと30年。", anim=1.2, speed=1.05,
         chara="none"),
    # 画面の「360回」を声が引き取る(2026-08-30 nihongo/high・kousei/medium:
    # 声は「30年で、合計いくら?」と言い、画面は「360回」と別のことを言っていた)
    Unit("kikan", "360回で、合計いくら?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.4, chara="none"),
    Unit("shiki1", "止めなければ114万円。", anim=1.0, se="impact",
         se_at=sf.landing_sec("formula", 1.0), speed=0.95, intonation=1.3,
         chara="none"),
    # 逆接「それでも」は受けるものが無かった(2026-08-30 kousei/low・nihongo/high:
    # 直前で額を明かした相手に「気づかないまま」と続けるのは自己矛盾)。
    # 残り期間を主語に立てる
    Unit("toi_oboe", "114万円を、気づかないまま払う?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.6, chara="none"),

    # 「積む」は「積み立てる」の省略で、金融文脈のこの用法は一般語ではない
    # (2026-08-30 nihongo/medium)。初出で正式な形を渡す。読点は修飾の境界に置く
    Unit("tsumu", "3162円を、毎月あなたが積み立てたら?", anim=1.2, speed=1.05,
         chara="none"),
    # 「〜と仮定します」は論文の定型(2026-08-30 nihongo/medium)。中止形で話し言葉に
    Unit("katei", "では、年5%と仮定します。", anim=1.0, speed=1.05,
         chara="none"),
    # 「答えは」は進行の合図で、数字に温度が乗らない(2026-08-30 copy/medium)
    Unit("fueru", "同じ額なのに、263万円。", anim=1.2, se="don",
         se_at=sf.landing_sec("bars", 1.2),
         speed=1.0, intonation=1.25, sub_delay=0.9, chara="none"),
    # 図のラベルを音読しない(2026-08-30 copy/high)。「だけ」が unit16 への橋になる
    Unit("yaji", "あなたが決めるのは、3162円の行き先だけ。", anim=1.2,
         se="impact", se_at=sf.landing_sec("arrow", 1.2), speed=1.0,
         intonation=1.2, pad=0.35, chara="none"),

    # 263万円が「3つ全部を止めた話」であることを、撤回の入口で回収する
    # (2026-08-30 kousei/high: 動画の最大値が条件不明のまま宙に浮いていた)
    Unit("hyo_x", "263万円は3つ全部を止めた話。", anim=1.0,
         speed=1.1, chara="none"),
    # 決定に**判定基準**を入れる(2026-08-30 kousei/high)。
    # 「使っていない1つ」では、どれが使っていないかを既に知っている前提になる
    Unit("hitotsu", "でも、先月ひらかなかった1つだけ。", anim=1.0, speed=1.05,
         chara="none"),
    # 「止めるだけで確定する額」を声に出す(2026-08-30 kousei/high)。
    # この動画が求める行動は「止める」だけで、「積む」は求めていない
    Unit("hitotsu2", "1つ止めれば、あなたの約39万円が残る。", anim=1.0,
         speed=1.05, chara="none"),
    Unit("kyuuju", "それを積めば、年5%で約90万円。", anim=1.2,
         se="don", se_at=sf.landing_sec("hero", 1.2), speed=1.0,
         intonation=1.25, pad=0.3, chara="none"),
    # 画面のカードの左辺と一字一句そろえ、360 の単位を耳に渡す(nihongo/medium)
    Unit("shiki2", "月額に360か月をかける。", anim=1.0, speed=1.05,
         chara="none"),
    # 【】は**決定語**に付ける(2026-08-30 nihongo/medium・copy/medium:
    # 緑の強調が1手前の準備動作「開いて」に乗っていた)。
    # 明細の場所を plan §2 と一語一致させる(kousei/medium)
    Unit("meisai", "今日、カードの明細を開いて、1つ【止める】。", anim=1.0,
         speed=1.0, intonation=1.2, chara="none"),
    # 最後の残像を行動側に残す(2026-08-30 kousei/medium)。
    # 冒頭の「サブスク」へ戻ってループする(check_hold H3)
    Unit("cta2", "止めるサブスクは、どれ?", anim=1.0,
         speed=1.0, intonation=1.3, chara="none"),
]

# 字幕の級数は**動画内で1つに固定**する
F.lock_sub_fs([u.subtitle for u in UNITS])


def render_thumbnail():
    """output/thumbnail.png だけ即時更新する(`render.py --thumb`)。"""
    S.setup_fonts()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    fig = S.new_canvas(0.0)
    SCENES["namae__cover"](fig, 1.0)
    out = OUTDIR / "thumbnail.png"
    S.save_frame(fig, out)
    print(f"thumbnail: {out}")


if __name__ == "__main__":
    if "--thumb" in sys.argv[1:]:
        render_thumbnail()
        sys.exit(0)
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S033.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
