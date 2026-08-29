#!/usr/bin/env python3
"""S033: Netflix・Spotify・Amazonプライム。3つで30年いくらか。

P-M(35歳・男性・会社員)の1本目。
**カットは1本ずつ変える。**S032は40.1秒で11カット(3.65秒/カット)で、
競合の1.6〜1.8秒に対して2倍遅かった。check_tempo が落とすようにしてある。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

TITLE = "サブスク3つ、30年でいくら?"
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
# ユーザー指摘:「この女の人出しすぎだね。参考のペンギンは3、4回しか出てない」
# 参考(BANK ACADEMY)の実測: 本編19フレーム中、キャラは1フレームだけ。
# 直前の版は 24カット中17カット(71%)がキャラだった。本編は図で埋める。
# 表は5カットで共通(値・行とも変えない)
_HYO = [["Netflix", "1590円"],
        ["Spotify", "1080円"],
        ["Amazonプライム", "492円"],
        ["合計", "3162円"]]
_HYO_HEAD = ["サービス", "月額"]

SCENES = {
    # ---- カバー(キャラ 1/4)
    # 0秒目の立ち絵はカバーと同じ困り顔にし、3サービスのカードが積み上がる
    "namae": sf.person_cards("03_troubled",
                             ["Netflix", "Spotify", "Amazonプライム"]),
    # 2026-08-29 批評5周目(copy/thumbnail/kousei 統合。B案を採用):
    # - 「やめられない人へ/やめて積んだら?」は宛先と提案が矛盾し、読んだ瞬間に
    #   『自分には無理』と閉じられていた。**固有名詞3つ+損失枠**に差し替え
    #   (plan §5「カバーにサービス名」にも初めて適合する)
    # - 263万円のカバー開示をやめる → 動画内の裏切り(263万・90万)が復活し、
    #   赤バッジ+不安顔と感情設計が一致する(損=赤の色文法どおり)
    # - 114万円は 0%(3162円×360か月)の導出値なので年5%の免責が不要になり、
    #   count_from も不要。打消しは料金の時点表記だけをクリームのプレートで出す
    "namae__cover": sf.cover("Netflix・Spotify・プライム",
                             "やめずに30年払ったら?", "114万円",
                             name="03_troubled",
                             disclaimer="※ 料金は2026年8月時点。3162円×360か月の計算"),

    # ---- 表を出しっぱなしにして、**赤枠を1行ずつ下に動かす**(参考の主武器)
    # build=最初のカットだけ行を順に着地させる。
    # total_mode="dim": 「月いくら?」と問うている間、合計はまだ明かさない
    # 2026-08-29 批評5周目: 並びを hyo_a(build)→ hyo_aru(赤枠が行を巡る=
    # 「ありますよね?」)→ hyo_n(単価がwaveで順に点灯)→ hyo_g(開示)に変更。
    # focus= で行へのパンチインを入れ、冒頭4カットの同一構図を崩す
    "hyo_a": sf.table(_HYO_HEAD, _HYO, highlight=2, build=True, focus=2,
                      title="30代がよく持つ3つ", total_mode="dim"),
    "hyo_aru": sf.table(_HYO_HEAD, _HYO, highlight="sweep",
                        title="30代がよく持つ3つ", total_mode="dim"),
    "hyo_n": sf.table(_HYO_HEAD, _HYO, highlight="wave",
                      title="3つの月額", total_mode="dim"),
    "hyo_g": sf.table(_HYO_HEAD, _HYO, highlight=3, focus=3,
                      title="30代がよく持つ3つ"),

    # 数式カード: 答え(=の右)をカード内に着地させる。注記は文脈見出しへ
    "waru": sf.formula("3162円 ÷ 30日", name=None, answer="105円",
                       title="1日あたりにすると"),
    # count=False: 105円は waru で開示済み。数え直さない(2026-08-29 批評5周目)
    "hi": sf.hero("105円", "1日あたり", name=None, count=False),
    # 缶コーヒーとの並置比較(「より安い」の比較対象を絵に出す。
    # 缶コーヒーに価格は書かない=出典の無い数字を画面に出さない)
    "hikaku": sf.compare("105円", "缶コーヒー", "1日あたり", "",
                         title="くらべると"),
    # 2026-08-29 批評5周目: 2箱+矢印の同型3連発を解消するため、期間は
    # timeline(帯の伸長)で見せる。旧ラベル「積むのをやめる」は後半のひねりの
    # ネタバレ+『積む』未導入の矛盾だったので「ここまで払う」に(nihongo/high)
    "obi": sf.timeline(35, 65, 65, "ここまで払う", "", show_gap=False,
                       title="30年、つづけると", fill_color=sf.RED_FADE),
    # role="neutral": 360か月は中立な期間。赤(損・警告)を便利色にしない
    "kikan": sf.hero("360か月", "35歳から65歳までの30年", name=None,
                     role="neutral"),
    "shiki1": sf.formula("3162円 × 360か月", name=None, answer="114万円",
                         title="30年で出ていく額"),

    # ---- 本編で唯一の立ち絵(キャラ 2/4)。いちばん刺す一行に置く
    "toi_oboe": sf.person_bubble("03_troubled", "114万円…?"),

    # tease=1: 「積んだらどうなるか」と問うカットでは答えの263万円棒を
    # 破線の輪郭+「?」で予告に留める(開示は fueru で初めて)
    "tsumu": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=0, tease=1, title="同じ3162円を積んだら"),
    # caption: 打消しの一文はカード内・数字の直下へ(注記帯を全ユニット1行に保つ)
    # sub="運用の前提": 上部の視線アンカー(head_title)を隣接カットと揃える
    # (2026-08-29 批評5周目: 12・14に見出しがあり13だけ消えて帯が点滅していた)
    "katei": sf.hero("年5%", "運用の前提", name=None, stamp=True, role="gain",
                     caption="あくまで仮定。元本保証ではありません"),
    # prev_highlight=0: 強調が「貯める側」から「運用側」へクロスフェードで移る
    # gain=1: 増える側は緑(赤=損・警告と色で区別する)
    "fueru": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=1, prev_highlight=0, gain=1,
                     title="同じ3162円を積んだら"),
    # scale_right: 増える側の箱を1.15倍(級数は部品側で左の1.3倍になる)
    # 矢印の既定色は INK(部品側で統一。2026-08-29 批評5周目)
    "yaji": sf.arrow("114万円", "263万円", "出ていく", "積んだら",
                     title="同じ3162円が", scale_right=1.15, role="gain"),

    # ---- 1つでいい
    # wave_role="keep": 緑の点灯=「やめて積んだ」側に立った3行(band+frame の
    # 文法は赤側と同じ。色だけ緑。2026-08-29 批評5周目)
    "hyo_x": sf.table(_HYO_HEAD, _HYO, highlight="wave", wave_role="keep",
                      title="3つ全部やめた場合"),
    # title はナレーションの同義反復を避け、次カットの hitotsu と同じ語で
    # アンカーを継続させる(check_figure の「冗長」対応)
    "hyo_1": sf.table(_HYO_HEAD, _HYO, highlight=1,
                      title="使っていない1つ"),
    # count=False: 1080円は表で既出の参照値。カウントアップは水増しに見える
    "hitotsu": sf.hero("1080円", "使っていない1つ", name=None, count=False),
    # ymax を fueru と同じ目盛(263万×1.22)に固定し、ghost で前カットの
    # 2本(114万・263万)を破線の輪郭で残す(2026-08-29 批評5周目:
    # 参照物が無いと「小さくてスカスカの図」に見えた。空いた高さが
    # 「さっきの263万円との比較」として意味を持つ)
    "hitotsu2": sf.bars([("出したお金", 388_800, "約39万円"),
                         ("年5%と仮定", 898_839, "約90万円")],
                        highlight=1, gain=1, title="止めた分を積んだら",
                        ymax=2_631_602 * 1.22,
                        ghost=[(1_138_320, "114万円"), (2_631_602, "263万円")]),
    # 答え行は【】で赤の強調に(他の shiki の「答え=赤・大」と同じ視線誘導。
    # 表示の強調記法のみ。ナレーション・台本の文言は変えていない)
    "shiki2": sf.formula("月額 × 360か月", "= 30年で【出ていく額】", name=None,
                         title="自分の額の求め方"),

    # ---- 締め(キャラ 3/4・4/4)
    # rows: 明細アプリ風のミニカードを添える。立ち絵は 02_point(前向きの
    # 行動提案に困り顔は矛盾する。2026-08-29 批評5周目・plan §8)
    "meisai": sf.person_bubble("02_point", "明細チェック", rows=_HYO[:3]),
    # 吹き出しは締めの問いと呼応(「いくつある?」は計算ゼロで答えられる)
    "cta2": sf.cta("", "02_point", show_comment=True, bubble="いくつある?"),
}

# 「運用は年5%と仮定」の免責は、運用の話が画面に出るまで先頭の一文だけにする
# (0秒目から出すと後半のひねりを自分でネタバレする)。
# tsumu(年5%の棒が出る)以降は全文のまま。
for _k in ("namae", "hyo_a", "hyo_aru", "hyo_n", "hyo_g",
           "waru", "hi", "hikaku", "obi", "kikan", "shiki1", "toi_oboe"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# SE は**着地の時刻**に合わせる(2026-08-29 批評5周目: 数字の着地は
# big_number が 0.55×anim 秒、棒とカウントは bars が 0.72×anim 秒。
# 音だけ先に鳴って絵が素通りしていた)
UNITS = [
    # 1文目は plan §4 の問いをそのまま口に出す(check_toi。欲求の名指し)。
    # 「?」は表示時に fmt_disp が全角へ直す
    Unit("namae", "サブスク3つで、月いくら?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),
    # 名指しは「プライム」に短縮(正式名 Amazonプライム は画面の表にある。
    # check_figure の「図の Amazonプライム と字幕が同義」対応)
    Unit("hyo_a", "NetflixにSpotify、プライム。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hyo_aru", "この3つ、ありますよね?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("hyo_n", "1590円、1080円、492円。", anim=1.0, speed=1.05, chara="none"),
    # 図の合計が赤で立つカットは字幕の【】を外す(1画面で強調色を割らない)
    Unit("hyo_g", "合わせて月3162円です。", anim=1.0, se="don", se_at=0.55,
         speed=1.0, intonation=1.2, chara="none"),
    Unit("waru", "月3162円を、1日に直すと。", anim=1.0, speed=1.05, chara="none"),
    Unit("hi", "たった105円。", anim=1.0, speed=1.0, intonation=1.25,
         chara="none"),
    Unit("hikaku", "105円は、缶コーヒーより安い。", anim=1.0, speed=1.05,
         chara="none"),
    # 「30年」は画面(obi の見出し・shiki の題)に出るので声でも言う(check_figure)
    Unit("obi", "これを35歳から65歳まで、30年。", anim=1.2, speed=1.05,
         chara="none"),
    Unit("kikan", "360か月、お金を払い続けると。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("shiki1", "出ていくお金は【114万円】。", anim=1.0, se="impact",
         se_at=0.6, speed=0.95, intonation=1.3, chara="none"),
    Unit("toi_oboe", "気づかないまま、114万円払いますか?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.6, chara="none"),

    Unit("tsumu", "その114万円、積んだらどうなるか。", anim=1.2, speed=1.05,
         chara="none"),
    Unit("katei", "積んだ場合、年5%と仮定します。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("fueru", "答えは、263万円。", anim=1.2, se="don", se_at=0.85,
         speed=1.0, intonation=1.25, chara="none"),
    Unit("yaji", "これで、あなたのお金が入ってくる側に。", anim=1.2, se="impact",
         se_at=0.35, speed=1.0, intonation=1.2, pad=0.35, chara="none"),

    Unit("hyo_x", "いまのは、3つ全部やめた場合。", anim=1.0, speed=1.1,
         chara="none"),
    Unit("hyo_1", "でも、現実は使ってない1つだけでいい。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hitotsu", "【1080円】のものを1つ止めれば。", anim=1.0, speed=1.05,
         chara="none"),
    # 「止めるだけで90万円もらえる」と聞こえた断絶の修正(nihongo/high)。
    # 図の左棒(約39万円)も声で言う(check_figure「数字が無言」対応)
    Unit("hitotsu2", "止めた約39万円を積めば、約90万円。", anim=1.2, se="don",
         se_at=0.85, speed=1.0, intonation=1.25, pad=0.3, chara="none"),
    Unit("shiki2", "あなたの額は、月額×360か月。", anim=1.0, speed=1.05,
         chara="none"),
    # CTAも本編と同じ強調文法(行動語だけ【】)。読み上げの文字は変えていない
    Unit("meisai", "まずは【明細】を開いてみませんか?", anim=1.0, speed=1.0,
         intonation=1.2, chara="none"),
    Unit("cta2", "あなたのサブスク、いくつある?", anim=1.0, speed=1.0,
         intonation=1.3, chara="none"),
]

# 字幕の級数は**動画内で1つに固定**する(2026-08-29 批評5周目:
# ユニットごとの自動縮小で、同じ役割の字幕がカットまたぎで約4割揺れていた)
F.lock_sub_fs([u.subtitle for u in UNITS])

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S033.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
