#!/usr/bin/env python3
"""横型シーンの下見。台本を書く前にレイアウトを目で確かめるためのもの。

170ユニットを書いてからレイアウト崩れを見つけるのは高くつくので、
`scenes_long.py` の型を1枚ずつ書き出して先に見る。

    python3 production/preview_long.py [出力先ディレクトリ]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortlib as S  # noqa: E402

S.use_landscape()
import scenes_long as sl  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/long_preview")
BADGE = "2026年8月時点・仮定の計算"
BRAND = "数字で見るお金の教科書"

CASES = {
    "01_cover": (sl.cover("NISAで損したら、いくら損するのか", "40,630円",
                          "同じ年に課税口座で利益があると", "2026年8月時点の制度", BRAND),
                 "", False),
    "02_hero": (sl.hero("NISAで損しても、税金は1円も戻らない",
                        "課税口座なら戻る場合がある", BADGE, BRAND), "でも本当にそうなのだ。", True),
    "03_chapter": (sl.chapter(2, "NISAだと引けない", "NISAの損は、利益から引けるのか?",
                              BADGE, BRAND), "では第2章に行くのだ。", True),
    "04_card": (sl.card("この仕組みの名前", "損益通算", "(そんえきつうさん・同じ年の中で相殺する)",
                        BADGE, BRAND), "これを損益通算というのだ。", True),
    "05_barsN": (sl.barsN("上がる時期ごとの分かれ目",
                          [("直後", 3.14, "3.14%"), ("5年後", 3.83, "3.83%"),
                           ("10年後", 4.96, "4.96%"), ("15年後", 6.94, "6.94%"),
                           ("20年後", 11.04, "11.04%"), ("25年後", 21.90, "21.90%")],
                          BADGE, BRAND, highlight=3),
                 "15年逃げ切れば、6.94%まで耐えるのだ。", True),
    "06_compare2": (sl.compare2("同じ年に、損20万円と利益20万円",
                                ("全部 課税口座だったら",
                                 [("損20万", 20, S.MUTED_BAR), ("益20万", 20, S.GOLD)], "税 0円"),
                                ("NISAで損したら",
                                 [("損20万", 20, S.MUTED_BAR), ("益20万", 20, S.GOLD)],
                                 "税 40,630円"),
                                BADGE, BRAND,
                                note_l="損は利益から引ける", note_r="NISAの損は無かったことになる"),
                    "その差が、40630円なのだ。", True),
    "07_band": (sl.band("会社が出した460万円の中身", "会社が出す 460万円", 0.6856,
                        "手取り 315万円", "差 145万円", BADGE, BRAND,
                        show_rest=True, big="手元に残るのは 69%"),
                "会社が出した額の、69%しか残らない。", True),
    "08_curve": (sl.curve("上がる時期と、分かれ目の金利",
                          [0, 5, 10, 15, 20, 25], [3.14, 3.83, 4.96, 6.94, 11.04, 21.90],
                          BADGE, BRAND, xlabel="金利が上がる時期(年後)",
                          ylabel="分かれ目の金利(%)",
                          marks=[(5, 3.83, "3.83%"), (15, 6.94, "6.94%")],
                          hline=3.14, hline_label="固定金利 3.14%", yfmt="{:.0f}"),
                 "遅く上がるほど、分かれ目は高くなるのだ。", True),
    "09_timeline": (sl.timeline("損を来年の利益から引けるか",
                                [("1年目", "損 40万円", "税 0円", False),
                                 ("2年目", "利益 40万円", "税 81,260円", True)],
                                BADGE, BRAND, arrow=(0, 1),
                                note="課税口座なら、この矢印(繰越控除)が使える"),
                    "課税口座なら、3年ぶん繰り越せるのだ。", True),
    "10_table": (sl.table("3つの場合",
                          ["どんな年か", "課税口座だけ", "NISAを使うと", "差"],
                          [("損だけの年", "0円", "0円", "0円"),
                           ("利益だけの年", "40,630円", "0円", "得 40,630円"),
                           ("損と利益がある年", "0円", "40,630円", "損 40,630円")],
                          BADGE, BRAND, highlight=2),
                 "3つの場合をまとめると、こうなるのだ。", True),
}


def main():
    S.setup_fonts()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (painter, subtitle, with_chara) in CASES.items():
        fig = S.new_canvas()
        painter(fig, 1.0)
        if with_chara:
            S.draw_chara(fig, "br", 0, "open", "normal", 0.0)
        if subtitle:
            S.draw_subtitle(fig, subtitle)
        S.save_frame(fig, OUT / f"{name}.png")
        print(f"  {OUT / f'{name}.png'}")
    print(f"{len(CASES)}枚 書き出した({S.W}x{S.H})")


if __name__ == "__main__":
    main()
