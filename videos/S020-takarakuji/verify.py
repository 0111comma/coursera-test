#!/usr/bin/env python3
"""S020: 宝くじ還元率の検証。出典: 総務省(当せん金付証票の発売実績等)・plan.md参照。"""

KANGEN_KUJI = 0.465    # 宝くじの当せん金割合(令和6年度実績)
KANGEN_KEIBA = 0.75    # 競馬など公営競技の払戻率の目安(券種により約70〜80%)
KAI = 10_000


def main():
    kitai = int(KAI * KANGEN_KUJI)
    assert kitai == 4_650, kitai              # 1万円分 → 平均4,650円
    yume = KAI - kitai
    assert yume == 5_350                      # 「夢の値段」5,350円
    assert round(KANGEN_KEIBA / KANGEN_KUJI, 1) == 1.6  # 競馬は宝くじの約1.6倍戻る
    # 当せん金付証票法: 当せん金は発売総額の5割以下
    assert KANGEN_KUJI < 0.5
    print("S020 verify: ALL OK")
    print(f"  宝くじ1万円分 → 平均{kitai:,}円(還元率{KANGEN_KUJI:.1%})")
    print(f"  夢の値段: {yume:,}円 / 競馬などとの比: 約{KANGEN_KEIBA/KANGEN_KUJI:.1f}倍")


if __name__ == "__main__":
    main()
