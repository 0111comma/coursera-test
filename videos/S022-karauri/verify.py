#!/usr/bin/env python3
"""S022: 空売りの損益の検証。

前提: 100万円分を空売り(信用取引)。手数料・貸株料・金利は考慮しない単純化した例。
出典: 日本取引所グループ/日本証券業協会の信用取引の説明(plan.md参照)。
"""

MOTO = 1_000_000        # 空売りした時点の株の値段(100万円分)


def karauri_soneki(bairitsu: float) -> int:
    """空売りの損益。株価が bairitsu 倍になったときの損益(プラス=もうけ)。"""
    kaimodoshi = MOTO * bairitsu       # 買い戻しに必要な金額
    return int(MOTO - kaimodoshi)      # 売った額 − 買い戻した額


def kai_soneki(bairitsu: float) -> int:
    """普通に買った場合の損益。"""
    return int(MOTO * bairitsu - MOTO)


def main():
    # 下がったとき: 2割下がれば20万円のもうけ
    assert karauri_soneki(0.8) == 200_000

    # 上がったとき: 3倍になれば200万円の損(出した額を超える)
    assert karauri_soneki(3.0) == -2_000_000
    assert abs(karauri_soneki(3.0)) == MOTO * 2

    # 買いの損失は、株価が0になっても投資額が上限
    assert kai_soneki(0.0) == -MOTO
    for b in (0.0, 0.1, 0.5):
        assert kai_soneki(b) >= -MOTO

    # 空売りの損は株価の上昇に比例して増え続ける(理論上の上限がない)
    for b in (2.0, 5.0, 10.0, 100.0):
        assert karauri_soneki(b) == int(MOTO * (1 - b))
    assert karauri_soneki(10.0) == -9_000_000      # 10倍なら900万円の損
    assert karauri_soneki(3.0) < kai_soneki(0.0)   # 3倍で既に「買いの最大損失」を超える

    print("S022 verify: ALL OK")
    print(f"  100万円分を空売り → 2割下がると +{karauri_soneki(0.8):,}円")
    print(f"  同 → 株価3倍で {karauri_soneki(3.0):,}円(出した100万円を超える損)")
    print(f"  同 → 株価10倍で {karauri_soneki(10.0):,}円")
    print(f"  普通に買った場合の最大損失: {kai_soneki(0.0):,}円(株価0でも投資額まで)")


if __name__ == "__main__":
    main()
