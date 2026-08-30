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

# 常設ヘッダーは本編の転回(月額 → 30年)を先出ししない(2026-08-30 kousei/high)。
# 旧「サブスク3つ、30年でいくら?」は0秒目から8ユニット先の枠組みを答えていて、
# unit 8〜10 の「30年で114万円」の着地が、22ユニットずっと画面に出ていた語の
# 確認になっていた。投稿タイトル(script.md)は変えない。
TITLE = "サブスク3つ、いくら?"
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
# 1本の文字列を正にして、カバーと本編1カット目が同じ並び順を共有する
_SERVICES_LINE = "Netflix・Spotify・Amazonプライム"
_SERVICES = _SERVICES_LINE.split("・")
_HYO = [["Netflix", "1590円"],
        ["Spotify", "1080円"],
        ["Amazonプライム", "492円"],
        ["合計", "3162円"]]
_HYO_HEAD = ["サービス", "月額"]

SCENES = {
    # ---- カバー(キャラ 1/4)
    # 0秒目の立ち絵はカバーと同じ困り顔にし、3サービスのカードが積み上がる
    # 並び順・寸法・書体はカバーのチップと共有(service_chip)。0.0秒の継ぎ目で
    # ラベル・順序・位置・幅が同時に変わっていた(2026-08-30 thumbnail/medium)
    "namae": sf.person_cards("03_troubled", _SERVICES,
                             title="30代がよく持つ3つ"),
    # 2026-08-29 批評6周目(copy/thumbnail 統合):
    # - 問いは「やめずに30年払ったら?」→「あなたも30年払う?」(C案)。
    #   旧2行目は直下の114万円が答えになり、疑問符が指を止める仕事を
    #   していなかった。二人称なら問いの宛先が視聴者自身になり、疑問形が死なない
    # - サービス名は上帯のテキスト → **下帯の3チップ**(cover() 内のB案)。
    #   72pxタイルで字高5.7pxに潰れ、Shorts上部のアイコン帯にも刺さっていた
    # - 注記から「3162円×360か月の計算」を削除。01〜03が ?,???円 で作るタメと
    #   10_shiki1 の式の初出を、0秒目に配ってしまっていた
    # - 残しコピー入りバッジ等のAB案は script.md「サムネAB」を参照
    # 2026-08-30 厳格審査(thumbnail/copy):
    # - フックは**墨帯の上の白文字・2行**。1行では 1080px 幅で ink 120px に
    #   物理的に届かず、72pxタイルで字高5.7pxに潰れていた(縁取り依存の解消)
    # - サービス名は本編1カット目と**同じ部品・同じ並び順**のチップ3枚。
    #   略語「プライム」をやめ「Amazonプライム」に統一(check_goi の語の省略)
    # - 免責はプレートを廃してバッジ内の下段ストリップへ(画面のいちばん高い帯を
    #   コントラスト比1.16:1の死荷重が占めていた)
    # - 緑のティーザーを1枚足し、**伏せている側を絵で名指す**
    #   (赤=出ていく / 緑=まだ伏せている)
    "namae__cover": sf.cover(_SERVICES_LINE,
                             "この3つ、\n30年で?", "114万円",
                             name="03_troubled",
                             disclaimer="※ 料金は2026年8月時点。",
                             teaser="やめたら ?万円"),

    # ---- 表を出しっぱなしにして、**枠を1行ずつ下に動かす**(参考の主武器)
    # build=最初のカットだけ行を順に着地させる。
    # total_mode="dim": 「月いくら?」と問うている間、合計はまだ明かさない
    # 2026-08-29 批評6周目:
    # - 01・02 の行ハイライトは hl_role="neutral"(墨リング+ベージュ地)。
    #   単なる読み上げ位置に赤(損・警告)を使わない
    # - 01 の行の出現はナレーションの語位置に割り付ける(build_at)。
    #   枠の着地も第3行の発声後(hl_at=0.80)。声より先に強調しない
    # focus(パンチイン)は外した(2026-08-30 consistency/medium): 6カット中
    # 2カットだけカット内で12%リフレームし、しかもズームで文字の級数まで
    # 揺れていた。表は全カット同一グリッドに固定する
    "hyo_a": sf.table(_HYO_HEAD, _HYO, highlight=2, build=True,
                      title="30代がよく持つ3つ", total_mode="dim",
                      hl_role="neutral", build_at=(0.10, 0.40, 0.68, 0.82),
                      hl_at=0.80),
    "hyo_aru": sf.table(_HYO_HEAD, _HYO, highlight="sweep",
                        title="30代がよく持つ3つ", total_mode="dim",
                        hl_role="neutral"),
    "hyo_n": sf.table(_HYO_HEAD, _HYO, highlight="wave",
                      title="3つの月額", total_mode="dim"),
    "hyo_g": sf.table(_HYO_HEAD, _HYO, highlight=3,
                      title="30代がよく持つ3つ"),

    # 数式カード: 答え(=の右)をカード内に着地させる。注記は文脈見出しへ。
    # 2026-08-29 批評6周目: 旧7(hi)を削除して6に105円を吸収(105円が
    # 3カット連続で情報が前進しなかった)。formula の答え着地はそのまま
    # 見出しは事実(1日あたり)ではなく**機構**を言う(2026-08-30 copy/medium)。
    # 図の見出し=機構 / カード=計算 / 声=数、の3層に分ける
    "waru": sf.formula("3162円 ÷ 30日", name=None, answer="105円",
                       title="小さく見える理由"),
    # role="loss": 105円は05・06で赤=出ていく側だった。比較でも褪せ赤で
    # 同一性を保つ(缶コーヒーに価格は書かない=出典の無い数字を出さない)
    # 右箱の下ラベルに「より安い」を置いて不等号の意味を語で明示する
    # (2026-08-30 nihongo/medium: 金額と商品名を不等号で結んでいて、記号の
    #  左右が同じ種類の量になっていなかった。値段は書かない=出典が無いので)
    "hikaku": sf.compare("105円", "缶コーヒー1本", "1日あたり", "より安い",
                         title="くらべると", role="loss"),
    # 2026-08-29 批評5周目: 2箱+矢印の同型3連発を解消するため、期間は
    # timeline(帯の伸長)で見せる。旧ラベル「積むのをやめる」は後半のひねりの
    # ネタバレ+『積む』未導入の矛盾だったので「ここまで払う」に(nihongo/high)
    # fill_color は**満彩度の RED_FILL**(2026-08-30 artdirection/high:
    # 動画中で最も痛みを語るカットなのに、面が最も彩度の低い非強調段だった)
    "obi": sf.timeline(35, 65, 65, "ここまで払う", "", show_gap=False,
                       title="30年、つづけると", fill_color=sf.RED_FILL),
    # role="neutral": 360回は中立な回数。赤(損・警告)を便利色にしない。
    # 2026-08-29 批評6周目: 「360か月」→「360回」。9(期間)と10(回数×単価)で
    # 役割を分け、11 の式 3162×360 への掛け算予告にする(kousei/high)
    "kikan": sf.hero("360回", "月3162円を払う回数", name=None,
                     role="neutral"),
    "shiki1": sf.formula("3162円 × 360か月", name=None, answer="114万円",
                         title="30年で出ていく額"),

    # ---- 本編で唯一の立ち絵(キャラ 2/4)。いちばん刺す一行に置く
    "toi_oboe": sf.person_bubble("03_troubled", "114万円…?",
                                 title="30年で出ていく額"),

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
                     highlight=0, tease=1, title="もし積んでいたら",
                     ymax=2_631_602 * 1.22),
    # caption: 打消しの一文はカード内・数字の直下へ(注記帯を全ユニット1行に保つ)
    # 「仮定」を1画面に4回出さない(2026-08-30 nihongo/medium)。見出しは声の
    # 「増える」と語をそろえ、注記からは「仮定」の語を落とす(上帯とナレーションの2回に)
    "katei": sf.hero("年5%", "増えると仮定する率", name=None, stamp=True,
                     role="gain",
                     caption="元本保証ではなく、減る年もあります"),
    # prev_highlight=0: 強調が「貯める側」から「運用側」へクロスフェードで移る
    # gain=1: 増える側は緑(赤=損・警告と色で区別する)。
    # 既知の114万円棒は count=False(数え直さない。2026-08-29 批評6周目)
    "fueru": sf.bars([("ただ貯める", 1_138_320, "114万円", {"count": False}),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=1, prev_highlight=0, gain=1,
                     title="同じ3162円を積んだら"),
    # scale_right: 増える側の箱を1.15倍(級数は部品側で左の1.3倍になる)
    # 矢印の既定色は INK(部品側で統一。2026-08-29 批評5周目)
    # 下ラベルはナレーションの中心語と一語一致(出ていく側 / 積む側)。
    # scale_right は 1.15→1.0(2026-08-30 artdirection/medium: 右の優位は
    # 級数差 fs_r = fs_l*1.3 が既に語っている。器のサイズでは語らない)
    "yaji": sf.arrow("114万円", "263万円", "出ていく側", "積む側",
                     title="同じ3162円が", scale_right=1.0, role="gain"),

    # ---- 1つでいい
    # 2026-08-29 批評6周目(kousei): 撤回カットの絵と言葉を揃える。
    # 旧 wave_role="keep"(3行の緑=祝福)は「全部やめると良い」と見え、
    # 「現実的じゃない」のナレーションと喧嘩していた → 中立の sweep に。
    # 緑の祝福は hyo_1(1行だけ)から始める
    # ハイライトを外す(2026-08-30 kousei/high): sweep が Spotify 行に乗った
    # フレームがあり、次カットで初めて明かす「使っていない1つ」を一手先に
    # 指差していた。見出しを疑問形にすると台詞「現実的じゃない」が答えの側になる。
    # total_ink=INK: 「止める」文脈のカットで合計を「出ていく赤」のままにしない
    "hyo_x": sf.table(_HYO_HEAD, _HYO, highlight=None,
                      title="3つ全部を止める?", total_ink=sf.INK),
    # hl_role="keep": 「止めて積む側」に立つ1行は緑(以降 hitotsu・hitotsu2 も
    # 緑の系で通す)。title はナレーションの同義反復を避け、次カットの
    # hitotsu と同じ語でアンカーを継続させる(check_figure の「冗長」対応)
    "hyo_1": sf.table(_HYO_HEAD, _HYO, highlight=1, hl_role="keep",
                      title="使っていない1つ", total_ink=sf.INK),
    # count=False: 1080円は表で既出の参照値。カウントアップは水増しに見える。
    # 部品側で「表の行位置からのスライドイン→着地ポップ→鼓動」が付く。
    # role="gain": 止めて積む側に立った金額(hyo_1 の緑と同じ文法)
    "hitotsu": sf.hero("1080円", "使っていない1つ", name=None, count=False,
                       role="gain"),
    # ymax を fueru と同じ目盛(263万×1.22)に固定し、ghost で前カットの
    # 2本(114万・263万)を丸ドットの輪郭で残す(参照物が無いと
    # 「小さくてスカスカの図」に見えた。空いた高さが比較として意味を持つ)
    # ゴーストと 263万目盛を外す(2026-08-30 kousei/medium)。ここで言いたいのは
    # 「1つだけでも意味がある」なのに、90万が263万の1/3の高さにしか立たず、
    # 絵は「1つでは全然足りない」と読めていた。棒を枠いっぱいに立て、
    # 約39万→約90万の倍率を第2幕(114万→263万)と同じ絵の強さで見せる。
    # 棒ラベルは声の「積んだ」と一語一致(nihongo/high)
    "hitotsu2": sf.bars([("積んだお金", 388_800, "約39万円"),
                         ("年5%と仮定", 898_839, "約90万円")],
                        highlight=1, gain=1, title="止めた分を積んだら",
                        ymax=898_839 * 1.22),
    # 答え行は【】で赤の強調に(他の shiki の「答え=赤・大」と同じ視線誘導。
    # 表示の強調記法のみ。ナレーション・台本の文言は変えていない)
    # 持ち帰る式を、視聴者が決めた行動(使っていない1つを止める)に対応させる
    # (2026-08-30 kousei/medium)。答え側の強調は損の赤ではなく得の緑
    "shiki2": sf.formula("止める1つの月額 × 360か月", "= 【出さずに済む額】",
                         name=None, title="自分の額の求め方",
                         emph_color=sf.GREEN_DARK),

    # ---- 締め(キャラ 3/4・4/4)
    # rows: 明細アプリ風のミニカードを添える。立ち絵は 02_point(前向きの
    # 行動提案に困り顔は矛盾する。2026-08-29 批評5周目・plan §8)
    # 吹き出しは字幕と別の語にする(2026-08-30 copy/medium: 「明細」が同一画面で
    # 二度、しかも吹き出しは行動を「チェック」という抽象語で言い直すだけだった)
    "meisai": sf.person_bubble("02_point", "1つでいい", rows=_HYO[:3],
                               title="いま、できること"),
    # 吹き出しは締めの問いと呼応(「3つより多い?」は数えるだけで答えられ、
    # 比較アンカーがあるので反応型コメントが立つ。2026-08-29 批評6周目)
    # 吹き出しは字幕の完全な部分文字列にしない。「数えるだけ」でコメントの
    # 摩擦をゼロだと明示する(2026-08-30 copy/medium)
    "cta2": sf.cta("", "02_point", show_comment=True, bubble="数えるだけ",
                   title="あなたの番"),
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
    # 「?」は表示時に fmt_disp が全角へ直す。
    # cover_hold=0.30: 0.07秒(20fpsで1.4フレーム)は移行ではなく1フレームの
    # フラッシュとして知覚される。カバーと本編1カット目でチップの部品・順序・
    # 寸法を揃えたので、0.30秒の静止は「サムネが動き出す」導入として読める
    # (2026-08-30 retention/low)
    Unit("namae", "サブスク3つで、月いくら?", anim=1.0, cover=True,
         cover_hold=0.30, se="pop", speed=1.0, intonation=1.3, chara="none"),
    # 正式名を声でも一度言う(作文原則10。耳だけの視聴者は Amazon の語を
    # 受け取れなかった。2026-08-29 批評6周目)
    Unit("hyo_a", "NetflixにSpotify、Amazonプライム。", anim=1.0, speed=1.05,
         chara="none"),
    # 相槌(「ありますよね?」)を機構の名指しに置き換える(2026-08-30 kousei/medium)。
    # 「自動で続く」という中核機構が22ユニット一度も出ないまま終わっていた。
    # 二人称を入れて Shorts の最大離脱帯(4〜7秒)を自分ごとにする
    Unit("hyo_aru", "この3つも、止めるまであなたから引かれます。", anim=1.0,
         speed=1.05, chara="none"),
    # 表の並び順を声で一語だけ指し、金額とサービスの対応を耳に渡す(nihongo/medium)
    Unit("hyo_n", "上から1590円、1080円、492円。", anim=1.0, speed=1.05,
         chara="none"),
    # 図の合計が赤で立つカットは字幕の【】を外す(1画面で強調色を割らない)。
    # se_at_frac: 合計行の開示は**ナレーション進行度**(_prog)で動くので、
    # SEも尺の割合で置く(秒で書くと約0.9秒早く鳴っていた。retention/medium)
    Unit("hyo_g", "合わせて、月3162円。", anim=1.0, se="don", se_at_frac=0.70,
         speed=1.0, intonation=1.2, chara="none"),
    # 「1日たった105円」→「1日にすると、105円。」(nihongo/medium)。
    # 換算であることを声に入れ、7の評価語との重複を消す
    Unit("waru", "これを1日にすると、105円。", anim=1.0, speed=1.05,
         chara="none"),
    # 大小関係は図が担い、声は**なぜ止めないのか**という原因だけを言う
    # (2026-08-30 copy/medium)。「止める」が17〜18の「止めて」と鎖になる
    Unit("hikaku", "安すぎて、あなたも止めようと思わない。", anim=1.0, speed=1.05,
         chara="none"),
    # 65歳は図の右端とキャレットが担う。「あと」が残り時間のカウントダウンを立てる
    Unit("obi", "あなたが35歳なら、65歳まであと30年。", anim=1.2, speed=1.05,
         chara="none"),
    # 期間(8)と回数(図の360回)の同義反復を解消し、**第1のリビールの直前に
    # 問いと止め(pad)を置く**(2026-08-30 kousei/medium)。冒頭0〜20秒に間が
    # 一度も無く、114万円が助走なしで来ていた
    Unit("kikan", "30年で、合計いくら?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.4, chara="none"),
    # カードが額を、声が条件を担う(2026-08-30 copy/high)。以降の「止める」の伏線
    Unit("shiki1", "止めなければ、114万円。", anim=1.0, se="impact",
         se_at=sf.landing_sec("formula", 1.0), speed=0.95, intonation=1.3,
         chara="none"),
    # 114万円の再言を1回減らし、期間の側で痛みを言い直す(nihongo/high・K3)
    Unit("toi_oboe", "それでも、気づかないまま払いますか?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.6, chara="none"),

    # 元本114万円の一括運用に読める圧縮を解消する(2026-08-30 kousei/high)。
    # verify.py が計算しているのは**毎月3162円の積立**で、図の見出しも
    # 「同じ3,162円を積んだら」。声・絵・計算を三者一致させる。二人称+問い
    Unit("tsumu", "その3162円を毎月、あなたが積んだら?", anim=1.2, speed=1.05,
         chara="none"),
    # 「積んだ」の反復を解消し、5%=増え方の率だと耳だけで分かる形に(copy)
    Unit("katei", "年5%で増えると仮定します。", anim=1.0, speed=1.05,
         chara="none"),
    # sub_delay: 字幕の「263万円」がカウンタ着地より先に確定表示され、
    # リビールが字幕に殺されていた。se_at は bars の着地(WIN=0.90×anim)に合わせる
    Unit("fueru", "答えは、263万円。", anim=1.2, se="don",
         se_at=sf.landing_sec("bars", 1.2),
         speed=1.0, intonation=1.25, sub_delay=0.9, chara="none"),
    # 見出し「同じ3,162円が」との一字一句重複を解消し、主語を金額から人へ移す
    # (2026-08-30 copy/high)。図の2ラベル(出ていく側 / 積む側)と語が対応する。
    # se_at は矢先の到達(0.55×anim)に合わせる
    Unit("yaji", "あなたが払う側から、積む側に変わる。", anim=1.2, se="impact",
         se_at=sf.landing_sec("arrow", 1.2), speed=1.0, intonation=1.2,
         pad=0.35, chara="none"),

    # 逆接は16に1回だけ。目的語と動詞を入れ、動詞は18の「止めて」と統一する
    # (2026-08-30 nihongo/high・low。「とはいえ」は書き言葉寄りなので口語へ)
    Unit("hyo_x", "とはいっても、全部は止められない。", anim=1.0,
         speed=1.1, chara="none"),
    Unit("hyo_1", "止めるのは、使っていない1つでいい。", anim=1.0, speed=1.05,
         chara="none"),
    # 「止めて」の受け手となる動詞を入れる(2026-08-30 nihongo/high:
    # 「1080円を止めて、同じ360か月。」は述語が欠落し、次文の「出した」と矛盾していた)
    Unit("hitotsu", "1080円を止めて、360か月積む。", anim=1.0,
         speed=1.05, chara="none"),
    # 二人称+動詞。図の棒ラベル「積んだお金」と一語一致させる
    Unit("hitotsu2", "あなたが積む約39万円が、約90万円になる。", anim=1.2,
         se="don", se_at=sf.landing_sec("bars", 1.2), speed=1.0,
         intonation=1.25, pad=0.3, chara="none"),
    # 持ち帰る式を、視聴者が決めた行動(1つ止める)に対応させる。
    # 記号「×」を声に出す不自然さと名詞の圧縮も同時にほどく(nihongo/high)
    Unit("shiki2", "1つの月額に、360をかける。", anim=1.0, speed=1.05,
         chara="none"),
    # 【】は**行動語**に付ける(render.py 自身の規則。2026-08-30 nihongo/medium)。
    # 「今日」は plan §7 と一語一致し、行動の期限が入る。
    # plan §7 の決定(使っていない1つを止める)を締めで言い切る(kousei/high)
    Unit("meisai", "今日、明細を【開いて】、1つ止める。", anim=1.0,
         speed=1.0, intonation=1.2, chara="none"),
    # 数える質問は残すが、対象を「使っていないもの」にして行動の続きにする
    # (2026-08-30 kousei/high・copy/medium)。0個も8個も等しく投稿できる開いた問い
    Unit("cta2", "あなたのサブスク、使っていないのはいくつ?", anim=1.0,
         speed=1.0, intonation=1.3, chara="none"),
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
