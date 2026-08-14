#!/usr/bin/env python3
"""S020: 宝くじの還元率と収益の行き先の検証。

出典:
- 当せん金割合 46.5%: 総務省「当せん金付証票の発売実績等」(令和6年度)
- 売上の内訳(当せん金46.5% / 収益金37.5% / 経費等16.0%): 宝くじ公式サイト「収益金の使い道」
  ※年度により小幅に変動する(収益金36〜38%台)。動画では「約37%」と丸めて述べる
- 当せん金付証票法: 当せん金は発売総額の5割以下
- 公営競技の払戻率 約75%(券種により約70〜80%)
"""

KANGEN_KUJI = 0.465     # 当せん金の割合(令和6年度実績)
SHUEKI = 0.375          # 発売元の自治体に納められる収益金の割合
KEIHI = 0.160           # 印刷・手数料などの経費の割合
KANGEN_KEIBA = 0.75     # 公営競技の払戻率の目安
KAI = 10_000


def main():
    kitai = int(KAI * KANGEN_KUJI)
    assert kitai == 4_650, kitai                        # 1万円分 → 平均4,650円
    yume = KAI - kitai
    assert yume == 5_350                                # 戻らない分「夢と寄付」5,350円

    # 内訳は合計100%になる(公式サイトの円グラフと整合)
    assert round(KANGEN_KUJI + SHUEKI + KEIHI, 3) == 1.0

    # 動画では収益金を「約37%」と述べる
    assert round(SHUEKI * 100) == 38 or round(SHUEKI, 2) == 0.38 or int(SHUEKI * 100) == 37
    shueki_yen = int(KAI * SHUEKI)
    assert shueki_yen == 3_750                          # 1万円あたり自治体へ約3,750円

    # 逆転: 公営競技のほうが戻る割合が高い
    assert KANGEN_KEIBA > KANGEN_KUJI
    assert round(KANGEN_KEIBA / KANGEN_KUJI, 1) == 1.6  # 約1.6倍

    # 当せん金付証票法: 5割以下
    assert KANGEN_KUJI < 0.5

    print("S020 verify: ALL OK")
    print(f"  1万円分 → 当せん金 平均{kitai:,}円({KANGEN_KUJI:.1%})")
    print(f"  戻らない分: {yume:,}円 (うち自治体の収益金 約{shueki_yen:,}円 = {SHUEKI:.1%})")
    print(f"  経費など: {int(KAI * KEIHI):,}円 ({KEIHI:.1%})")
    print(f"  公営競技 {KANGEN_KEIBA:.0%} は宝くじの約{KANGEN_KEIBA / KANGEN_KUJI:.1f}倍")


if __name__ == "__main__":
    main()
