#!/usr/bin/env python3
"""S016 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

「給料から引かれている住民税は、去年の所得で決まっている」を金額で示す。
年収400万円・独身・扶養なし・東京都・介護保険なし(40歳未満)を前提にした概算。

住民税(所得割+均等割)の組み立て:
  給与所得   = 年収 − 給与所得控除
  課税所得   = 給与所得 − 社会保険料控除 − 基礎控除(住民税は43万円)
  所得割     = 課税所得(千円未満切捨) × 10% − 調整控除
  均等割     = 5,000円(市町村3,000 + 道府県1,000 + 森林環境税1,000)

前提の注記:
  - 給与所得控除は年収3,600,001〜6,600,000円で「収入×20%+44万円」
    (2025年の改正で引き上げられたのは年収190万円以下の最低保障額。ここは変更なし)
  - 住民税の基礎控除は令和8年度も43万円で据え置き(所得税側だけが引き上げられた)
  - 調整控除は課税所得200万円以下なので「人的控除の差の合計 × 5%」。
    基礎控除の差は地方税法上5万円で固定なので 50,000 × 5% = 2,500円
  - 社会保険料は S012 と同じ料率(厚生年金9.15%+健康保険4.925%+子ども子育て0.115%
    +雇用0.5% = 14.69%)で概算する。実額は健保組合や自治体で変わる
"""
INCOME = 4_000_000        # 年収
SOCIAL_RATE = 0.1469      # 社会保険料の本人負担(概算・S012と同じ料率)
BASIC_DEDUCTION = 430_000  # 住民税の基礎控除(令和8年度も据え置き)
RATE = 0.10               # 所得割(市町村6%+道府県4%)
ADJUST = 2_500            # 調整控除(課税所得200万円以下・基礎控除差5万円 × 5%)
FLAT = 5_000              # 均等割(森林環境税1,000円を含む)


def salary_deduction(income: int) -> int:
    """給与所得控除(年収3,600,001〜6,600,000円の区分)。"""
    assert 3_600_001 <= income <= 6_600_000, "この関数はこの年収帯のみ"
    return int(income * 0.20) + 440_000


def main():
    ded = salary_deduction(INCOME)
    salary_income = INCOME - ded
    social = int(INCOME * SOCIAL_RATE)
    taxable = salary_income - social - BASIC_DEDUCTION
    taxable = taxable // 1000 * 1000            # 千円未満切捨
    income_levy = int(taxable * RATE) - ADJUST
    total = income_levy + FLAT
    monthly = total / 12
    quarterly = total / 4

    assert ded == 1_240_000, ded
    assert salary_income == 2_760_000, salary_income
    assert social == 587_600, social
    assert taxable == 1_742_000, taxable
    assert income_levy == 171_700, income_levy
    assert total == 176_700, total
    # 画面表示の丸め
    assert round(total / 10_000) == 18 and int(total / 10_000) == 17, total
    assert round(monthly / 100) * 100 == 14_700, monthly     # 画面「約1万4700円」
    assert round(quarterly / 1000) * 1000 == 44_000, quarterly  # 画面「およそ4万4千円」
    # 所得割は課税所得の10%。均等割は所得と無関係な定額
    assert income_levy + ADJUST == int(taxable * RATE)

    print("S016 verify: ALL OK")
    print(f"  年収 {INCOME:,}円 − 給与所得控除 {ded:,}円 = 給与所得 {salary_income:,}円")
    print(f"  − 社会保険料 {social:,}円 − 基礎控除 {BASIC_DEDUCTION:,}円"
          f" = 課税所得 {taxable:,}円")
    print(f"  所得割 {taxable:,} × {RATE:.0%} − 調整控除 {ADJUST:,} = {income_levy:,}円")
    print(f"  + 均等割 {FLAT:,}円 = 年 {total:,}円(画面は約17万円)")
    print(f"  毎月の天引き {monthly:,.0f}円(画面は約1万4700円)")
    print(f"  自分で払う場合は4期 {quarterly:,.0f}円/回(画面はおよそ4万4千円)")
    print(f"  年収に対する割合 {total / INCOME:.1%}")


if __name__ == "__main__":
    main()
