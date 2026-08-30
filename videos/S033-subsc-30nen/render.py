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
    # 2026-08-29 批評6周目(copy/thumbnail 統合):
    # - 問いは「やめずに30年払ったら?」→「あなたも30年払う?」(C案)。
    #   旧2行目は直下の114万円が答えになり、疑問符が指を止める仕事を
    #   していなかった。二人称なら問いの宛先が視聴者自身になり、疑問形が死なない
    # - サービス名は上帯のテキスト → **下帯の3チップ**(cover() 内のB案)。
    #   72pxタイルで字高5.7pxに潰れ、Shorts上部のアイコン帯にも刺さっていた
    # - 注記から「3162円×360か月の計算」を削除。01〜03が ?,???円 で作るタメと
    #   10_shiki1 の式の初出を、0秒目に配ってしまっていた
    # - 残しコピー入りバッジ等のAB案は script.md「サムネAB」を参照
    "namae__cover": sf.cover("Netflix・Spotify・プライム",
                             "あなたも30年払う?", "114万円",
                             name="03_troubled",
                             disclaimer="※ 料金は2026年8月時点。"),

    # ---- 表を出しっぱなしにして、**枠を1行ずつ下に動かす**(参考の主武器)
    # build=最初のカットだけ行を順に着地させる。
    # total_mode="dim": 「月いくら?」と問うている間、合計はまだ明かさない
    # 2026-08-29 批評6周目:
    # - 01・02 の行ハイライトは hl_role="neutral"(墨リング+ベージュ地)。
    #   単なる読み上げ位置に赤(損・警告)を使わない
    # - 01 の行の出現はナレーションの語位置に割り付ける(build_at)。
    #   枠の着地も第3行の発声後(hl_at=0.80)。声より先に強調しない
    "hyo_a": sf.table(_HYO_HEAD, _HYO, highlight=2, build=True, focus=2,
                      title="30代がよく持つ3つ", total_mode="dim",
                      hl_role="neutral", build_at=(0.10, 0.40, 0.68, 0.82),
                      hl_at=0.80),
    "hyo_aru": sf.table(_HYO_HEAD, _HYO, highlight="sweep",
                        title="30代がよく持つ3つ", total_mode="dim",
                        hl_role="neutral"),
    "hyo_n": sf.table(_HYO_HEAD, _HYO, highlight="wave",
                      title="3つの月額", total_mode="dim"),
    "hyo_g": sf.table(_HYO_HEAD, _HYO, highlight=3, focus=3,
                      title="30代がよく持つ3つ"),

    # 数式カード: 答え(=の右)をカード内に着地させる。注記は文脈見出しへ。
    # 2026-08-29 批評6周目: 旧7(hi)を削除して6に105円を吸収(105円が
    # 3カット連続で情報が前進しなかった)。formula の答え着地はそのまま
    "waru": sf.formula("3162円 ÷ 30日", name=None, answer="105円",
                       title="1日あたりにすると"),
    # role="loss": 105円は05・06で赤=出ていく側だった。比較でも褪せ赤で
    # 同一性を保つ(缶コーヒーに価格は書かない=出典の無い数字を出さない)
    "hikaku": sf.compare("105円", "缶コーヒー", "1日あたり", "",
                         title="くらべると", role="loss"),
    # 2026-08-29 批評5周目: 2箱+矢印の同型3連発を解消するため、期間は
    # timeline(帯の伸長)で見せる。旧ラベル「積むのをやめる」は後半のひねりの
    # ネタバレ+『積む』未導入の矛盾だったので「ここまで払う」に(nihongo/high)
    "obi": sf.timeline(35, 65, 65, "ここまで払う", "", show_gap=False,
                       title="30年、つづけると", fill_color=sf.RED_FADE),
    # role="neutral": 360回は中立な回数。赤(損・警告)を便利色にしない。
    # 2026-08-29 批評6周目: 「360か月」→「360回」。9(期間)と10(回数×単価)で
    # 役割を分け、11 の式 3162×360 への掛け算予告にする(kousei/high)
    "kikan": sf.hero("360回", "月3162円を払う回数", name=None,
                     role="neutral"),
    "shiki1": sf.formula("3162円 × 360か月", name=None, answer="114万円",
                         title="30年で出ていく額"),

    # ---- 本編で唯一の立ち絵(キャラ 2/4)。いちばん刺す一行に置く
    "toi_oboe": sf.person_bubble("03_troubled", "114万円…?"),

    # tease=1: 「積んだらどうなるか」と問うカットでは答えの棒を
    # 丸ドットの輪郭+「?」で予告に留める(開示は fueru で初めて)。
    # 2026-08-29 批評6周目:
    # - 既知の114万円棒は count=False で即置き(4ユニット連続の数え直し禁止)。
    #   空いたアニメ窓は破線?棒のドローオン→?ポップ→鼓動に回す
    # - **ティーザー棒の高さは114万円棒と同じに固定**(kousei)。答えと同じ高さで
    #   立てると倍率が視覚でネタバレし、fueru のリビールが「高さの確認」になる。
    #   「同じ額なら同じ高さのはず」という誤前提を絵で置いてから、263万へ伸ばす
    # - ymax は fueru と同じ目盛に固定(カットまたぎでグリッドを跳ねさせない)
    "tsumu": sf.bars([("ただ貯める", 1_138_320, "114万円", {"count": False}),
                      ("年5%と仮定", 1_138_320, "")],
                     highlight=0, tease=1, title="同じ3162円を積んだら",
                     ymax=2_631_602 * 1.22),
    # caption: 打消しの一文はカード内・数字の直下へ(注記帯を全ユニット1行に保つ)
    "katei": sf.hero("年5%", "運用の前提", name=None, stamp=True, role="gain",
                     caption="あくまで仮定。元本保証ではありません"),
    # prev_highlight=0: 強調が「貯める側」から「運用側」へクロスフェードで移る
    # gain=1: 増える側は緑(赤=損・警告と色で区別する)。
    # 既知の114万円棒は count=False(数え直さない。2026-08-29 批評6周目)
    "fueru": sf.bars([("ただ貯める", 1_138_320, "114万円", {"count": False}),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=1, prev_highlight=0, gain=1,
                     title="同じ3162円を積んだら"),
    # scale_right: 増える側の箱を1.15倍(級数は部品側で左の1.3倍になる)
    # 矢印の既定色は INK(部品側で統一。2026-08-29 批評5周目)
    "yaji": sf.arrow("114万円", "263万円", "出ていく", "積んだら",
                     title="同じ3162円が", scale_right=1.15, role="gain"),

    # ---- 1つでいい
    # 2026-08-29 批評6周目(kousei): 撤回カットの絵と言葉を揃える。
    # 旧 wave_role="keep"(3行の緑=祝福)は「全部やめると良い」と見え、
    # 「現実的じゃない」のナレーションと喧嘩していた → 中立の sweep に。
    # 緑の祝福は hyo_1(1行だけ)から始める
    "hyo_x": sf.table(_HYO_HEAD, _HYO, highlight="sweep", hl_role="neutral",
                      title="3つ全部やめた場合"),
    # hl_role="keep": 「止めて積む側」に立つ1行は緑(以降 hitotsu・hitotsu2 も
    # 緑の系で通す)。title はナレーションの同義反復を避け、次カットの
    # hitotsu と同じ語でアンカーを継続させる(check_figure の「冗長」対応)
    "hyo_1": sf.table(_HYO_HEAD, _HYO, highlight=1, hl_role="keep",
                      title="使っていない1つ"),
    # count=False: 1080円は表で既出の参照値。カウントアップは水増しに見える。
    # 部品側で「表の行位置からのスライドイン→着地ポップ→鼓動」が付く。
    # role="gain": 止めて積む側に立った金額(hyo_1 の緑と同じ文法)
    "hitotsu": sf.hero("1080円", "使っていない1つ", name=None, count=False,
                       role="gain"),
    # ymax を fueru と同じ目盛(263万×1.22)に固定し、ghost で前カットの
    # 2本(114万・263万)を丸ドットの輪郭で残す(参照物が無いと
    # 「小さくてスカスカの図」に見えた。空いた高さが比較として意味を持つ)
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
    # 吹き出しは締めの問いと呼応(「3つより多い?」は数えるだけで答えられ、
    # 比較アンカーがあるので反応型コメントが立つ。2026-08-29 批評6周目)
    "cta2": sf.cta("", "02_point", show_comment=True, bubble="3つより多い?"),
}

# 「運用は年5%と仮定」の免責は、運用の話が画面に出るまで先頭の一文だけにする
# (0秒目から出すと後半のひねりを自分でネタバレする)。
# tsumu(年5%の棒が出る)以降は全文のまま。
for _k in ("namae", "hyo_a", "hyo_aru", "hyo_n", "hyo_g",
           "waru", "hikaku", "obi", "kikan", "shiki1", "toi_oboe"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# SE は**着地の時刻**に合わせる(数字の着地は big_number が 0.55×anim 秒、
# 棒とカウントは bars が 0.72×anim 秒。音だけ先に鳴って絵が素通りしていた)
#
# **字幕の強調規則**(2026-08-29 批評6周目で全ユニットに適用):
# 図側に赤/緑の強調数字が立つカットでは、字幕の【】を使わない
# (1画面で強調色を割らない)。shiki1・hitotsu の【】はこの規則違反だったので
# 外した。逆に図が語だけのカット(meisai)は【】で行動語を立てる
UNITS = [
    # 1文目は plan §4 の問いをそのまま口に出す(check_toi。欲求の名指し)。
    # 「?」は表示時に fmt_disp が全角へ直す
    Unit("namae", "サブスク3つで、月いくら?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),
    # 正式名を声でも一度言う(作文原則10。耳だけの視聴者は Amazon の語を
    # 受け取れなかった。2026-08-29 批評6周目)
    Unit("hyo_a", "NetflixにSpotify、Amazonプライム。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hyo_aru", "この3つ、ありますよね?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("hyo_n", "1590円、1080円、492円。", anim=1.0, speed=1.05, chara="none"),
    # 図の合計が赤で立つカットは字幕の【】を外す(1画面で強調色を割らない)。
    # SEで着地する最初のリビール。読点でタメて体言止め(リビール語尾の統一)
    Unit("hyo_g", "合わせて、月3162円。", anim=1.0, se="don", se_at=0.55,
         speed=1.0, intonation=1.2, chara="none"),
    # 旧7(hi「たった105円。」)を削除し、105円をここへ吸収(3カット連続の
    # 再掲で情報が止まっていた。2026-08-29 批評6周目)
    Unit("waru", "月3162円は、1日たった105円。", anim=1.0, speed=1.05,
         chara="none"),
    # 「安い」の事実提示ではなく、中核機構の第一因(安いから気づかない)を名指す
    Unit("hikaku", "缶コーヒーより安いから、気づかない。", anim=1.0, speed=1.05,
         chara="none"),
    # 35歳は plan 前提表の仮定値(P-M)。痛みを積む区間に唯一の「あなた」を置く
    Unit("obi", "あなたが35歳なら、65歳まで30年。", anim=1.2, speed=1.05,
         chara="none"),
    # 9(期間)との同義反復を解消: 10 は回数×単価の掛け算予告(kousei/high)
    Unit("kikan", "月3162円を、360回。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("shiki1", "出ていくお金は114万円。", anim=1.0, se="impact",
         se_at=0.6, speed=0.95, intonation=1.3, chara="none"),
    Unit("toi_oboe", "気づかないまま、114万円払いますか?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.6, chara="none"),

    Unit("tsumu", "その114万円、積んだらどうなるか。", anim=1.2, speed=1.05,
         chara="none"),
    # 「積んだ」の反復を解消し、5%=増え方の率だと耳だけで分かる形に(copy)
    Unit("katei", "年5%で増えると仮定します。", anim=1.0, speed=1.05,
         chara="none"),
    # sub_delay: 字幕の「263万円」がカウンタ着地(0.72×1.2秒)より先に
    # 確定表示され、リビールが字幕に殺されていた(2026-08-29 批評6周目)。
    # 字幕は着地後に出す(音声・尺は変えない)
    Unit("fueru", "答えは、263万円。", anim=1.2, se="don", se_at=0.85,
         speed=1.0, intonation=1.25, sub_delay=0.9, chara="none"),
    # 図の箱ラベルと同じ語(積む側)+動詞「変わる」で着地する。
    # 「入ってくる」は積んだ残高の説明として不正確だった(kousei/nihongo/copy
    # の一致指摘)。「出ていく側から」は図(矢印)が担う=画面は道標、文はナレーション
    Unit("yaji", "同じ3162円が、積む側に変わる。", anim=1.2, se="impact",
         se_at=0.35, speed=1.0, intonation=1.2, pad=0.35, chara="none"),

    # 逆接は17に1回だけ(旧17・18の「でも」系2連発を吸収)
    Unit("hyo_x", "とはいえ、3つ全部は現実的じゃない。", anim=1.0, speed=1.1,
         chara="none"),
    Unit("hyo_1", "使っていない1つだけでいい。", anim=1.0, speed=1.05,
         chara="none"),
    # 1080円→360か月→39万→90万の鎖を全て声でつなぐ(kousei/high)。
    # 図の緑の1080円が立つので【】は使わない(強調規則)
    Unit("hitotsu", "1080円を止めて、同じ360か月。", anim=1.0, speed=1.05,
         chara="none"),
    # 「出した」は画面の棒ラベル「出したお金」と一語一致。
    # 「止めた約39万円」(39万円を止めた?)という不正確な圧縮を解消
    Unit("hitotsu2", "出した約39万円が、約90万円に。", anim=1.2, se="don",
         se_at=0.85, speed=1.0, intonation=1.25, pad=0.3, chara="none"),
    # 「あなたの額は」→「あなたの場合は」(ガク×2の音の反響と名詞の圧縮を解消。
    # 「=30年で出ていく額」は画面の式カードが答えの側を担う)
    Unit("shiki2", "あなたの場合は、月額×360か月。", anim=1.0, speed=1.05,
         chara="none"),
    # どの明細かを一語で特定(plan §2 の場面=カードの明細と一語一致)
    Unit("meisai", "【カードの明細】を開いてみませんか?", anim=1.0,
         speed=1.0, intonation=1.2, chara="none"),
    # 比較アンカー「3つ」を与える(「数えてから書く」の1段を消し、
    # 「5個あった…」の反応型コメントが立つ形に。copy)
    Unit("cta2", "あなたのサブスク、3つより多い?", anim=1.0, speed=1.0,
         intonation=1.3, chara="none"),
]

# 字幕の級数は**動画内で1つに固定**する(2026-08-29 批評5周目:
# ユニットごとの自動縮小で、同じ役割の字幕がカットまたぎで約4割揺れていた)
F.lock_sub_fs([u.subtitle for u in UNITS])


def render_thumbnail():
    """output/thumbnail.png だけ即時更新する(`render.py --thumb`)。

    2026-08-29 批評6周目: 前回、カバーを直したのに再レンダリングせず、
    旧デザインの thumbnail.png がそのまま出荷物に残っていた。フル焼き
    2〜3時間を待たずにサムネを差し替え・AB検証できる経路を常設する。
    (本焼きでも render_video が同じ painter の t=1.0 を thumbnail.png に
    コピーするので、両経路の絵は一致する)"""
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
