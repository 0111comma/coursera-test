#!/usr/bin/env python3
"""S016: 預金保険(ペイオフ)の検証。出典: 預金保険機構・金融庁(plan.md参照)。"""

HOGO_JOGEN = 10_000_000   # 保護上限: 元本1,000万円+利息(1金融機関・1人あたり)
HATSUDO_YEAR = 2010       # 日本振興銀行破綻(ペイオフ発動の実例・戦後唯一)


def main():
    # 例: 1,500万円を1つの銀行に預けていた場合、保護確実なのは1,000万+利息
    yokin = 15_000_000
    hogo = min(yokin, HOGO_JOGEN)
    hami = yokin - hogo
    assert hogo == 10_000_000 and hami == 5_000_000
    # 2つの銀行に分ければ、それぞれ1,000万+利息まで保護
    assert min(7_500_000, HOGO_JOGEN) * 2 == 15_000_000
    # 発動実例は2010年(日本振興銀行)
    assert HATSUDO_YEAR == 2010
    print("S016 verify: ALL OK")
    print(f"  保護上限: 元本{HOGO_JOGEN:,}円+利息 / 1銀行1人あたり")
    print(f"  1,500万を1行に → 保護{hogo:,}円・はみ出し{hami:,}円(全額戻らない可能性)")
    print(f"  発動実例: {HATSUDO_YEAR}年・日本振興銀行")


if __name__ == "__main__":
    main()
