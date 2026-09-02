#!/usr/bin/env python3
"""S034: 60代で年金をもらいながら働く人へ。減りはじめる額が今年4月に上がった。

2026-08-31 **4度目の全面書き直し**。知識ゼロ4人・7問の理解度テストで 5.5/6.0 まで
上がったのに、依頼主は3回続けて「何を言っているのか分からない」と言った。
点が上がって伝わらないのは、**問題が文の作りではなく台本の骨格にあった**から。
読者4人の生の言葉から出た骨格の欠陥は3つで、この版はその3つだけを直している。

1. **「厚生年金」が何かを、23文のどこでも言っていなかった。**
   4人全員が Q7(いちばん分からなかった点)にここを挙げた。
   前の版は「基礎年金は減らない」を声から外して図にだけ置いたが、そのせいで
   「年金のうち」の『うち』が何を指すのか耳では決まらなくなっていた。
   読者4「年金に何種類あるのか、自分のがどれなのかが分からず、
   ここでまず自分の話かどうか決められなかった」
   → **2文目で「年金は2つ。基礎年金と厚生年金。」と数と名前を声に出し、
     3文目で「会社で働いた分」という自己判定の手がかりを渡す。**
     図(futatsu)は足し算の形、図(kousei)は「基礎年金は減らない」を持つ

2. **すでに失効した旧基準51万円で仕組みを9カット教えてから撤回していた。**
   4人全員がここで止まり、Q4(この人はいくら減るか)で2人が落ちた。
   読者2「せっかく覚えた51万円が要らない数字だったのか」
   読者1「だったら最初から65万円で説明してほしかった。ここでいちばん止まった」
   → **仕組みも例も最初から65万円で通す。**51万円は8〜9文目の
     「実は今年4月、法律が変わった/51万円が65万円に上がった」の2カットにだけ出し、
     **教える数字ではなく捨てられた数字**に降格した。
     おかげで視聴者が覚える基準額は65万円ひとつになる

3. **「給料」の中身(税引き前・ボーナス込み)を、その語を使う計算の14カット後に
   明かしていた。**読者は自分の月給を例に重ねて聞いたあと、別物だったと知らされる。
   → **4文目「引かれる前の給料」を、例より前に置いた。**
     ボーナスを12で割って入れることは図(tashizan)が持つ

あわせて直した、読者が名指しした穴:
- 「減る」の主語をすべて明示した(7・14・18・22。前の版は金額が主語に読めた)
- 51万円・65万円の出どころを声に入れた(「法律が決めた」「法律で上がった」)。
  前の版は図の「国が決めた額」だけで、声から落ちていた
- 締めに条件と根拠を付けた(22「超えても減るのは半分だけ」→ 23「働いて増える分が多い」
  → 24「だから」)。前の版は条件つきの判定の次に無条件の行動指示を置いていた
- 手順の在りかを **ねんきん定期便 → 年金の振込通知書** に変えた。
  定期便は**受け取る前の人**に届く書類で、この動画の主対象(もう受給している人)の
  手元には来ない。最初の一歩が空振りすると手順が全部止まる。
  **焼く前に日本年金機構の資料でユーザー環境から確認すること**(plan §10)
- 幕5の立ち絵を 03_troubled → 01_base に変えた。声で「同じ人」と言いながら
  画面で人が入れ替わっていた

**捨てたもの**(60秒に入らない。足すのではなく捨てた):
- 旧基準での例題(4万円超え・月2万円減っていた)。この動画の判定には使わない数字で、
  ここが「撤回」の正体だった。改正前との差は概要欄に置いた
- 「では、あなたの厚生年金は?」の問いカット。情報量がゼロで、次のカットが同じことを
  言い直していた。二人称の自分ごと化は図(hantei)の見出しが担う
- 「手続きは要らない」「減った分は戻らない」「判定は毎月やり直す」。
  それぞれ概要欄と図(hanbun)に置いた

数の扱い:
- 「基本月額」「総報酬月額相当額」は使わない。「厚生年金」「給料」と言う
- 10万円・45万円・60万円は**この動画の中だけの仮定**。plan §10 の前提表に明記
- 声に出す数はすべて verify.py の出力か plan.md の前提表の中にある
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

# 常設ヘッダーは本編の問いを先出ししない(kotoba-rules K1)。主題の名乗りだけ。
# バッジは**本編で声に出す額**を指す言い方に揃える(前の版の「減りはじめる額」は
# 画面にしか無い呼び名だった)。
TITLE = "働くと減る年金"
BADGE = "※ 2026年8月時点。65万円は毎年4月に見直されます"
F.use_fp_theme(TITLE, speaker=108, badge=BADGE)      # 東北きりたん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

# 台本に出す値は verify.py と一致していること
assert V.LIMIT_OLD == 510_000 and V.LIMIT_NEW == 650_000
assert V.BASIC == 100_000 and V.SALARY == 450_000 and V.TOTAL == 550_000
assert V.STOP_NEW == 0
assert V.TOTAL_HIGH == 700_000 and V.OVER_HIGH == 50_000
assert V.suspended(V.BASIC, 600_000, V.LIMIT_NEW) == 25_000

# カバーの惹句。**本編では「減りはじめる額」という呼び名を声に出さない**ので、
# ここは1フレーム目の掴みとしてだけ使う(本編の呼び名は「法律が決めた65万円」)。
_COVER_HOOK = "年金が減りはじめる額が"

SCENES = {
    # ---- カバー(キャラ 1/4)
    # 1フレーム目で**誰の話か**を名乗る。
    # 赤=3月までの額(既知)/ 緑=いまの額(伏せる)の非対称は残す
    "toi": sf.person("03_troubled", height=0.46),
    "toi__cover": sf.cover("60代。会社で働くと年金が減る?", _COVER_HOOK, "51万円",
                           name="03_troubled",
                           main_lab="3月まで",
                           alt_val="6?万円", alt_lab="いまは",
                           disclaimer="※ 2026年8月時点。年金を受け取っている人の話です。"),

    # ---- 幕1: 年金は2つあって、減るのは会社で働いた分だけ
    # ここが今回いちばん厚くした区間。4人全員が「厚生年金とは何か」で止まった
    "futatsu": sf.formula("基礎年金 + 厚生年金", name=None,
                          answer="あなたの年金", title="年金は2つある"),
    # **図だけが持つ情報**: 減らないほうは1円も動かないこと
    "kousei": sf.hero("基礎年金", "こっちは減らない", name=None,
                      role="gain", count=False, size="reference"),

    # ---- 幕2: 仕組みの芯。足す → 法律の額と比べる → 超えた分の半分
    # **図だけが持つ情報**: 足す「給料」が税や保険料を引く前の額であること
    "tasu": sf.formula("厚生年金 + 給料", name=None,
                       answer="税を引く前", title="まず足す2つ"),
    "kijun": sf.hero("65万円", "法律が決めた額", name=None, role="loss"),
    # **図だけが持つ情報**: 止まらない月は満額もらえること、判定が毎月やり直しなこと
    "ika": sf.hero("全額もらえる", "判定は毎月やり直す", name=None,
                   role="gain", count=False, size="reference"),
    # **図だけが持つ情報**: 止まった分はあとで戻らないこと(声に入れる尺が無い)
    "hanbun": sf.hero("半分", "超えた分の。あとで戻らない", name=None,
                      role="loss", count=False, size="reference"),

    # ---- 幕3: 転回。**旧基準はここで1回だけ、捨てる数字として出す**
    # **図だけが持つ情報**: これから変わるのではなく、もう始まっていること
    "kaisei": sf.hero("今年4月", "もう始まっている", name=None,
                      role="neutral", count=False, size="reference"),
    "sa": sf.arrow("51万円", "65万円", "3月まで", "4月から",
                   title="法律が決めた額", role="gain"),

    # ---- 幕4: 例(キャラ 2/4)。**新しい65万円だけで解く**
    "rei": sf.person_bubble("01_base", "厚生年金10万円"),
    "rei_q": sf.formula("10万円 + 45万円", name=None,
                        answer="合計は?", title="この人で試す"),
    "rei_a": sf.hero("55万円", "足した合計", name=None,
                     role="neutral", size="reference"),
    "shita": sf.compare("55万円", "65万円", "この人の合計", "法律が決めた額",
                        title="どっちが大きい?", role="neutral"),
    "zero": sf.hero("0円", "この人が減る額", name=None,
                    role="gain", count=False),

    # ---- 幕5: 正直に言う(キャラ 3/4)。全員が0円になるわけではない
    # 立ち絵は幕4と**同じ01_base**にする。声が「おなじ人」と言うため
    # (「同じ人」と漢字で書くと VOICEVOX が「ドオジジン」と読む。check_yomi)
    "rei2": sf.person_bubble("01_base", "給料60万円"),
    "koeru2": sf.formula("10万円 + 60万円", name=None,
                         answer="70万円", title="同じ人の合計"),
    # 幕2で渡した規則を、同じ形の式でもう一度あてる
    "koeru3": sf.formula("70万円 − 65万円", name=None,
                         answer="5万円", title="超えている分"),
    "mada": sf.hero("月2万5000円", "5万円の半分", name=None, role="loss"),

    # ---- 幕6: 自分でやる(キャラ 4/4)。在りか → 足し方 → 判定
    "tsuchi": sf.hero("年金振込通知書", "毎年6月に届く", name=None,
                      role="neutral", count=False, size="reference"),
    # **図だけが持つ情報**: ボーナスは1年ぶんを12で割って足すこと
    "tashizan": sf.formula("月給 + ボーナス÷12", name=None,
                           answer="足すほうの給料", title="ボーナスも入れる"),
    # 比較そのものを絵にする(formula の2段組は着地後に動きが止まる。design M1)
    "hantei": sf.compare("厚生年金+給料", "65万円", "あなたの合計",
                         "この額以下?", title="あなたの合計は?", role="neutral"),

    # ---- 幕7: 締めの根拠。**条件つきの判定のあとに無条件の指示を置かない**
    "handan": sf.hero("半分だけ", "超えても減るのは", name=None,
                      role="loss", count=False, size="reference"),
    "tokushi": sf.compare("増える給料", "減る年金", "働いた分",
                          "超えた分の半分", title="どっちが大きい?", role="neutral"),
    "cta": sf.cta("", "02_point", show_comment=True, bubble="足すだけ"),
}

# 免責は、合計の話が画面に出るまで先頭の一文だけにする
for _k in ("toi", "futatsu", "kousei", "tasu"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

# ナレーション: 24ユニット。
# 幕の並びは「誰の話か → 年金は2つ → 仕組み → 額が上がった → 例 → 正直 → 自分でやる」。
#
# 工程E(段落ごと書き直す)で、24文すべて書き下ろしている。1行パッチはしていない。
# 前の版から残した方針は「動詞は最後まで減るで通す」「例を規則より後に置く」の2つだけ。
#
# **数字の並びを1本にした**: 覚える基準額は65万円ひとつ。51万円は9文目で
# 「上がる前の額」として一度だけ出て、そのあと二度と使わない。
UNITS = [
    # 1文目で**年齢・受給者であること**を名乗る。「もらってる」の5文字が、
    # いま振り込まれている年金の話だと確定させる(払っている保険料の話ではない)
    Unit("toi", "60代。もらってる年金、働くと減る?", anim=1.0, cover=True,
         se="pop", speed=1.03, intonation=1.3, pad=0.10, chara="none"),

    # --- 幕1 年金は2つ。減るほうを名指しし、自己判定の手がかりを渡す
    # 4人全員が Q7 で挙げた穴。数(2つ)と名前(基礎年金・厚生年金)と
    # 見分け方(会社で働いた分)を、声で2カットに分けて渡す
    Unit("futatsu", "年金は2つ。基礎年金と厚生年金。", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("kousei", "減るのは、会社で働いた厚生年金だけ。", anim=1.0, speed=1.13,
         pad=0.10, chara="none"),

    # --- 幕2 仕組みの芯。足す2つの中身を、例より先に決めておく
    Unit("tasu", "まず1か月の厚生年金と、引かれる前の給料を足す。", anim=1.0,
         speed=1.13, intonation=1.1, pad=0.10, chara="none"),
    Unit("kijun", "その合計は、法律の【65万円】以下?", anim=1.0, se="don",
         speed=1.13, intonation=1.2, pad=0.10, chara="none"),
    Unit("ika", "65万円以下なら、厚生年金は減らない。", anim=1.0, speed=1.03,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("hanbun", "厚生年金はいくら減る?超えた分の【半分】。", anim=1.0,
         speed=1.03, intonation=1.2, pad=0.10, chara="none"),

    # --- 幕3 転回。**51万円が声に出るのはここだけ**。上がった向きだけを渡す
    Unit("kaisei", "実は今年4月、法律が変わった。", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("sa", "法律で【51万円】が65万円に上がった。", anim=1.2, se="don",
         speed=1.03, intonation=1.25, pad=0.10, chara="none"),

    # --- 幕4 例。合計を出し、65万円と比べ、減る額まで一気に降ろす
    Unit("rei", "たとえば厚生年金が月【10万円】の人。", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("rei_q", "もし給料が月【45万円】なら?", anim=1.0, speed=1.13,
         intonation=1.25, pad=0.10, chara="none"),
    Unit("rei_a", "給料を足すと合計【55万円】。", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("shita", "これは65万円より少ない。", anim=1.0, speed=1.13,
         intonation=1.1, pad=0.10, chara="none"),
    Unit("zero", "だから、厚生年金が減る額は【0円】。", anim=1.2, se="don",
         speed=1.03, intonation=1.3, pad=0.30, chara="none"),

    # --- 幕5 正直に言う。全員が0円になるわけではない。幕4と同じ3手をあてる
    Unit("rei2", "では、おなじ人の給料が【60万円】なら?", anim=1.0, speed=1.13,
         intonation=1.25, pad=0.10, chara="none"),
    Unit("koeru2", "給料を足すと合計【70万円】。", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("koeru3", "合計は65万円を【5万円】超えた。", anim=1.0, speed=1.13,
         pad=0.10, chara="none"),
    Unit("mada", "その半分、厚生年金が【2万5000円】減る。", anim=1.0,
         speed=1.13, intonation=1.2, pad=0.20, chara="none"),

    # --- 幕6 自分でやる。**在りか → 足し方 → 判定**の3カット。
    # 在りかは「ねんきん定期便」ではなく「年金の振込通知書」。定期便は
    # 受け取る前の人に届く書類で、この動画の主対象の手元には来ない
    Unit("tsuchi", "あなたの厚生年金の額は、年金の振込通知書に載る。", anim=1.0,
         speed=1.13, pad=0.10, chara="none"),
    Unit("tashizan", "その額と給料を足して、合計を出す。", anim=1.0, speed=1.13,
         pad=0.10, chara="none"),
    Unit("hantei", "あなたの合計は、【65万円】以下?", anim=1.0, speed=1.13,
         intonation=1.15, pad=0.10, chara="none"),

    # --- 幕7 締め。**条件と根拠を先に置いてから「だから」で行動につなぐ**
    Unit("handan", "65万円を超えても、減るのは半分だけ。", anim=1.0, speed=1.03,
         intonation=1.15, pad=0.10, chara="none"),
    Unit("tokushi", "減る分より、働いて増える分が多い。", anim=1.0, speed=1.03,
         intonation=1.2, pad=0.10, chara="none"),
    Unit("cta", "だから、年金が減る心配で仕事を抑えなくていい。", anim=1.0, speed=1.03,
         intonation=1.2, pad=0.10, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S034.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
