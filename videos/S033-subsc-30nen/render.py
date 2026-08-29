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
    # 2026-08-29 批評2周目: 最大文字が商品名でAmazonの広告に見えていた。
    # **最大要素はペイオフの金額(263万円)**、商品名は最小の行に落とす。
    # 263万円は年5%仮定の導出値なので、カバーにも打消し表示を出す(戦略§6-2)。
    # 0秒目の立ち絵もカバーと同じ困り顔にし、3サービスのカードが積み上がる
    "namae": sf.person_cards("03_troubled",
                             ["Netflix", "Spotify", "Amazonプライム"]),
    # 2026-08-29 批評4周目(hook/high):
    # - 「30年でこの差 263万円」は本編の2本棒(114万vs263万=差149万)と矛盾し、
    #   KGIルール(1つの嘘で信用が切れる)に反していた。263万円は**到達額**の
    #   主張(「やめて積んだら」)に変える
    # - 1行目は読点で宙吊りだったので完結形に(サムネは1行ごとに独立して読まれる)
    # - count_from: カウントは114万→263万(0からだと途中の「169万円」など
    #   動画のどこにも無い数字が最初の1秒に立つ)。窓は cover 側で t=0.30 着地
    # - 免責はバッジ外・画面最下部へ(cover 側)。削除はしない: カバーは
    #   hide_chrome で注記帯が無く、年5%仮定の導出値には打消し表示が要る(戦略§6-2)
    "namae__cover": sf.cover("サブスク3つ、やめられない人へ",
                             "やめて積んだら?", "263万円",
                             name="03_troubled",
                             disclaimer="※ 年5%と仮定した場合の計算です",
                             count_from="114万円"),

    # ---- 表を出しっぱなしにして、**赤枠を1行ずつ下に動かす**(参考の主武器)
    # build=最初のカットだけ行を順に着地させる。from_row=赤枠がすべってくる出発点。
    # total_mode="dim": 「月いくら?」と問うている間、合計はまだ明かさない
    # (hyo_g の開示で初めて赤にする。2026-08-29 批評2周目)
    "hyo_n": sf.table(_HYO_HEAD, _HYO, highlight=0, from_row=3,
                      title="30代がよく持つ3つ", total_mode="dim"),
    "hyo_s": sf.table(_HYO_HEAD, _HYO, highlight=1, from_row=0,
                      title="30代がよく持つ3つ", total_mode="dim"),
    # 2026-08-29 批評4周目: sweep をやめ、赤枠を前カット(hyo_a=Amazon行)から
    # **合計行(?,???円)へ滑らせる**。問いの対象は合計なのに、強調が無関係な
    # 1行に残留して見えていた。合計は total_mode="dim" のままなのでマスクは保たれる
    "hyo_q": sf.table(_HYO_HEAD, _HYO, highlight=3, from_row=2,
                      title="3つで月いくら?", total_mode="dim"),
    "hyo_a": sf.table(_HYO_HEAD, _HYO, highlight=2, build=True,
                      title="30代がよく持つ3つ", total_mode="dim"),
    "hyo_g": sf.table(_HYO_HEAD, _HYO, highlight=3, from_row=0,
                      title="30代がよく持つ3つ"),

    # 数式カード: 答え(=の右)をカード内に着地させる。注記は文脈見出しへ
    "waru": sf.formula("3162円 ÷ 30日", name=None, answer="105円",
                       title="1日あたりにすると"),
    "hi": sf.hero("105円", "1日あたり", name=None),
    # accent="arrow": 期間の終端(65歳)に結論色の赤を使わない。強調は矢印だけ
    # (赤=お金の結論、の意味体系を薄めない。2026-08-29 批評3周目)
    "obi": sf.arrow("35歳", "65歳", "いま", "積むのをやめる",
                    title="30年、つづけると", accent="arrow"),
    # role="neutral": 360か月は中立な期間。赤(損・警告)を便利色にしない
    "kikan": sf.hero("360か月", "35歳から65歳までの30年", name=None,
                     role="neutral"),
    "shiki1": sf.formula("3162円 × 360か月", name=None, answer="114万円",
                         title="30年で出ていく額"),

    # ---- 本編で唯一の立ち絵(キャラ 2/4)。いちばん刺す一行に置く
    "toi_oboe": sf.person_bubble("03_troubled", "114万円…?"),

    "hondai": sf.hero("114万円", "これを、積んだら?", name=None),
    # tease=1: 「積んだらどうなるか」と問うカットでは答えの263万円棒を
    # 破線の輪郭+「?」で予告に留める(開示は fueru で初めて。2026-08-29 批評3周目)
    "tsumu": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=0, tease=1, title="同じ3162円を積んだら"),
    # caption: 打消しの一文はカード内・数字の直下へ(注記帯を全ユニット1行に保つ)
    # role="gain": 年5%は増える側の仮定。前後の緑(tsumu の予告→fueru の緑棒)の
    # 真ん中に警告色の巨大な赤が割り込んで、色の文法を折っていた
    "katei": sf.hero("年5%", name=None, stamp=True, role="gain",
                     caption="あくまで仮定。元本保証ではありません"),
    # prev_highlight=0: 強調が「貯める側」から「運用側」へクロスフェードで移る
    # gain=1: 増える側は緑(赤=損・警告と色で区別する。2026-08-29 批評3周目)
    "fueru": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=1, prev_highlight=0, gain=1,
                     title="同じ3162円を積んだら"),
    # scale_right: 増える側の箱を1.15倍(級数は部品側で左の1.3倍になる)
    # arrow_color=INK: 方向記号を無彩色に(赤い矢印が緑の「入ってくる」箱へ
    # 刺さり、損へ向かうようにも読めた。赤=損の文法を濁らせない)
    "yaji": sf.arrow("114万円", "263万円", "出ていく", "積んだら",
                     title="同じ3162円が", scale_right=1.15, role="gain",
                     arrow_color=sf.INK),
    "gyaku": sf.arrow("出ていく", "入ってくる", "いままで", "これから",
                      title="お金の向きが変わる", role="gain",
                      arrow_color=sf.INK),

    # ---- 1つでいい
    # wave_role="keep": 「全部やめなくていい」の3行は緑(残してよい)の点灯。
    # 警告ピンクだと画面の色が「全行が危険」と言い、文言と正反対だった
    "hyo_x": sf.table(_HYO_HEAD, _HYO, highlight="wave", wave_role="keep",
                      title="全部やめなくていい"),
    "hyo_1": sf.table(_HYO_HEAD, _HYO, highlight=1, from_row=3,
                      title="使っていない1つだけ"),
    "hitotsu": sf.hero("1080円", "使っていない1つ", name=None),
    # ymax を fueru と同じ目盛(263万×1.22)に固定(2026-08-29 批評4周目:
    # 39万→90万の棒が 114万→263万とピクセル単位で同一の構図になり、
    # 「さっきと同じ図の使い回し」に見えて金額の量感が伝わらなかった。
    # 目盛を揃えれば 1/3 に減ったことが棒の高さで見える)
    "hitotsu2": sf.bars([("出したお金", 388_800, "約39万円"),
                         ("年5%と仮定", 898_839, "約90万円")],
                        highlight=1, gain=1, title="1つ止めたら",
                        ymax=2_631_602 * 1.22),
    # 答え行は【】で赤の強調に(他の shiki の「答え=赤・大」と同じ視線誘導。
    # 表示の強調記法のみ。ナレーション・台本の文言は変えていない)
    "shiki2": sf.formula("月額 × 360か月", "= 30年で【出ていく額】", name=None,
                         title="自分の額の求め方"),

    # ---- 締め(キャラ 3/4・4/4)
    # rows: 明細アプリ風のミニカードを添える(「明細を開け」と言うのに明細の
    # 絵が無く、下22%が無人だった。値は表と同じ、文言は足さない)
    "meisai": sf.person_bubble("03_troubled", "明細チェック", rows=_HYO[:3]),
    "cta2": sf.cta("", "02_point", show_comment=True),
}

# 「運用は年5%と仮定」の免責は、運用の話が画面に出るまで先頭の一文だけにする
# (0秒目から出すと後半のひねりを自分でネタバレする。2026-08-29 批評ループ)。
# tsumu(年5%の棒が出る)以降は全文のまま。
for _k in ("namae", "hyo_n", "hyo_s", "hyo_q", "hyo_a", "hyo_g",
           "waru", "hi", "obi", "kikan", "shiki1", "toi_oboe", "hondai"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

UNITS = [
    Unit("namae", "NetflixにSpotify、", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),
    Unit("hyo_a", "Amazonプライムですね。", anim=1.0, speed=1.05, chara="none"),
    Unit("hyo_q", "この3つ、月いくら払ってますか?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("hyo_n", "1590円、1080円、492円。", anim=1.0, speed=1.05, chara="none"),
    Unit("hyo_g", "合わせて月【3162円】です。", anim=1.0, se="don", speed=1.0,
         intonation=1.2, chara="none"),
    Unit("waru", "1日にするとたった【105円】。", anim=1.0, speed=1.05, chara="none"),
    Unit("hi", "缶コーヒーより安い金額です。", anim=1.0, speed=1.1, chara="none"),
    Unit("obi", "これを35歳から65歳まで。", anim=1.2, speed=1.05, chara="none"),
    Unit("kikan", "30年、【360か月】続けると。", anim=1.0, speed=1.05, chara="none"),
    Unit("shiki1", "出ていくお金は【114万円】。", anim=1.0, se="impact", se_at=0.1,
         speed=0.95, intonation=1.3, chara="none"),
    Unit("toi_oboe", "無意識に114万、払いますか?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.35, chara="none"),

    Unit("hondai", "ここからが今日の本題です。", anim=1.0, speed=1.1, chara="none"),
    Unit("tsumu", "このお金を積んだらどうなるか。", anim=1.2, speed=1.05, chara="none"),
    Unit("katei", "年5%で運用できたと仮定します。", anim=1.0, speed=1.05, chara="none"),
    Unit("fueru", "すると【263万円】になります。", anim=1.2, se="don",
         speed=1.0, intonation=1.25, chara="none"),
    Unit("yaji", "【114万円】が【263万円】に。", anim=1.2, speed=1.0,
         intonation=1.2, chara="none"),
    Unit("gyaku", "出ていくお金が、入ってくる側に。", anim=1.2, se="impact",
         se_at=0.2, speed=1.0, intonation=1.2, pad=0.35, chara="none"),

    Unit("hyo_x", "3つ全部やめなくていいんです。", anim=1.0, speed=1.1, chara="none"),
    Unit("hyo_1", "使ってないものを【1つ】だけ。", anim=1.0, speed=1.05, chara="none"),
    Unit("hitotsu", "【1080円】のものを1つ止めれば。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hitotsu2", "30年で【約90万円】になります。", anim=1.2, se="don",
         speed=1.0, intonation=1.25, pad=0.3, chara="none"),
    Unit("shiki2", "自分の額は月額×360ですよ。", anim=1.0, speed=1.05, chara="none"),
    # CTAも本編と同じ強調文法(行動語だけ【】)。読み上げの文字は変えていない
    Unit("meisai", "まずは【明細】を開いてみませんか?", anim=1.0, speed=1.0,
         intonation=1.2, chara="none"),
    Unit("cta2", "あなたのサブスク、【月いくら】?", anim=1.0, speed=1.0,
         intonation=1.3, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S033.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
