#!/usr/bin/env python3
"""S014 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

「銀行に100万円を1年置いたら、いくら増えるのか」を、
2026年8月の普通預金金利(3メガバンクが8月3日から年0.4%)で計算し、
同じ1年ぶんのコンビニATM手数料(時間外1回330円)と比べる。

税金の注記:
  利息には所得税15.315%+住民税5%=20.315%が源泉徴収される。
  実際は利息が年2回(2月・8月)に分けて支払われ、そのつど1円未満を切り捨てるため、
  年間の税額は下の単純計算と1円ほどずれることがある。
  動画では「およそ」の額しか出さないため、この差は表示に出ない。
"""
DEPOSIT = 1_000_000      # 預ける額
RATE = 0.4               # 普通預金の金利(年%・2026年8月・3メガバンク)
TAX_RATE = 0.20315       # 利息にかかる税(所得税15.315%+住民税5%)
ATM_FEE = 330            # コンビニATMの時間外手数料(1回・大手行の水準)
TIMES_PER_YEAR = 12      # 月に1回だけ使った場合


def main():
    gross = DEPOSIT * RATE / 100
    tax = round(gross * TAX_RATE)
    net = gross - tax
    fee_year = ATM_FEE * TIMES_PER_YEAR
    diff = fee_year - net

    assert gross == 4_000, gross
    assert tax == 813, tax
    assert net == 3_187, net
    assert fee_year == 3_960, fee_year
    assert diff == 773, diff
    # 図(積み上げ棒)の内訳が合計と合うこと
    assert net + tax == gross
    # 手数料のほうが多い、が結論。逆になっていないことを機械で押さえる
    assert fee_year > net, "この動画の結論が成り立っていない"

    print("S014 verify: ALL OK")
    print(f"  預金 {DEPOSIT:,}円 × 年{RATE}% = 利息 {gross:,.0f}円")
    print(f"  税金 {gross:,.0f} × {TAX_RATE:.5%} = {tax:,}円 → 手取り {net:,.0f}円")
    print(f"  ATM {ATM_FEE}円 × {TIMES_PER_YEAR}回 = {fee_year:,}円")
    print(f"  差  {fee_year:,} − {net:,.0f} = {diff:,.0f}円 手数料のほうが多い")
    print(f"  参考: 月2回なら {ATM_FEE * 24:,}円、"
          f"金利が0.001%だった頃の利息(税引前)は {DEPOSIT * 0.001 / 100:,.0f}円")


if __name__ == "__main__":
    main()
