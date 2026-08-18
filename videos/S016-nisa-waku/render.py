#!/usr/bin/env python3
"""S016: NISAは売っても、投資枠がその年には戻らない。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  NISAで売ったら、投資枠はいつ、いくら戻るのか。
答え:
  その年には戻らない。翌年に、買った値段のぶんだけ戻る。
  100万円で買って150万円で売っても、戻るのは100万円ぶん。

この人の欲求(yokkyu-map C: 無駄にしたくない):
  **NISAの投資枠を無駄にしたくない。売ったせいで減るなら、売り方を考えたい。**

ネタの根拠(demand-2026-08.md の実測):
  NISA系が検索流入の最大クラスタ。S003(NISAの投資枠1800万)は視聴率64.1%。
  上位3本の共通点は「視聴者がいま実際にやっていること」で、投資枠を埋めている途中の人に当たる。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・仮定の金額での計算"

BOKA, URINE = 1_000_000, 1_500_000
assert URINE - BOKA == 500_000

SCENES = {
    # 入口は日常語。「NISA」「投資信託」は2文目以降で出す
    # 「増えていた」と書かない。上がるのは株数ではなく値段(ループ71のユーザー指摘)
    "fueta": sc.card("買ったときより", "高くなった", "※ 金額はすべて仮定の例です",
                     BADGE, BRAND, main_size=118, head_fs=32),
    "fueta__cover": sc.cover("NISAで売ると、投資枠はいくら戻る?", "100万円",
                             "150万円で売っても、戻るのは買った値段", "2026年8月時点", BRAND),
    # 「枠」と略さない。画面でも音でも「投資枠」と呼び、意味をここで渡す
    "waku": sc.card("この動画で使う言葉", "投資枠", "※ 上限には毎年ぶんと一生ぶんがあります",
                    BADGE, BRAND, main_size=130, head_fs=32),
    "ne0": sc.bars2("その年に売った1本",
                    ("買ったとき", 10.0, "100万円"),
                    ("売ったとき", 15.0, "150万円"), BADGE, BRAND, ymax=17),
    "ne1": sc.bars2("戻る額を並べると",
                    ("売った値段", 15.0, "150万円"),
                    ("戻る投資枠", 10.0, "100万円"), BADGE, BRAND, ymax=17),
    "itsu": sc.card("投資枠が使えるのは", "翌年から", "※ 1月1日にまとめて空く",
                    BADGE, BRAND, main_size=118, head_fs=32,
                    ask="あなたは今年、売る予定がありますか?"),
    "son": sc.bars2("売値のほうが低い年",
                    ("売った値段", 8.0, "80万円"),
                    ("戻る投資枠", 10.0, "100万円"), BADGE, BRAND, ymax=13),
    "matome": sc.hayami("売る前に見る4つ",
                        [("売った値段", "関係しない"), ("買った値段", "この分が戻る"),
                         ("使えるのは", "翌年から"), ("毎年の上限", "360万円")],
                        "※ 2026年8月時点。取得価額(簿価)ベースで戻ります",
                        BADGE, BRAND, col1="見るところ", col2="どうなるか", focal=1),
    "shime": sc.chips("取得価額は、証券会社の画面で見られます",
                      ["すぐ言える", "調べれば分かる", "分からない", "まだ売らない"],
                      BADGE, BRAND),
}

UNITS = [
    # ユーザー指摘(ループ71):
    #   「株が増えるわけなくない? 株の単元数が増えるの? 株価が上がってるんだろ?」
    #   「枠ってなんだよ。一般的な用語じゃないだろ? 省略してんじゃん」
    # → (1) 値上がりを「株が増えた」と書かない。上がるのは**値段**
    #   (2)「枠」と略さない。「投資枠」と呼び、最初にその意味を言う
    Unit("fueta", "積み立てた株の値段が、上がったとする。", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.25),
    Unit("fueta", "その株はNISAで買っていたとするのだ。", anim=1.4,
         speed=1.05),
    Unit("waku", "NISAで買える金額の上限を、投資枠と呼ぶのだ。", anim=1.4,
         speed=1.05),
    Unit("ne0", "たとえば100万円ぶん買っていたとする。", anim=1.6, speed=1.05),
    Unit("ne0", "その値段が、150万円になったとする。", anim=0.0, speed=1.05),
    Unit("ne0", "そこで売っても、税金はかからないのだ。", anim=0.0, speed=1.1),
    Unit("ne1", "でもその投資枠が、思った額にならないのだ。", anim=1.6,
         face="troubled", speed=1.05),
    Unit("ne1", "まず戻るのは、売った150万円ではない。", anim=0.0, speed=1.05),
    Unit("ne1", "その投資枠は、買った100万円で戻るのだ。", anim=0.0,
         face="surprised", se="impact", se_at=0.32, speed=1.05, intonation=1.25),
    Unit("ne1", "だから差の50万円は、返ってこないのだ。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("itsu", "しかも使えるのは、売った年ではないのだ。", anim=1.4, speed=1.05),
    Unit("itsu", "その投資枠が空くのは、翌年からなのだ。", anim=0.0,
         speed=1.05),
    Unit("son", "ちなみに80万円に値下がりしても、", anim=1.6, speed=1.05),
    Unit("son", "その投資枠は100万円のまま戻るのだ。", anim=0.0, speed=1.05),
    Unit("matome", "つまり投資枠を決めるのは、買ったときの値段。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("matome", "そして使えるのは、いま年360万円までなのだ。", anim=0.0,
         speed=1.05),
    Unit("shime", "だから売る前に、買った値段を見てほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S016.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
