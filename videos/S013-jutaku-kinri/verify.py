#!/usr/bin/env python3
"""S013 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

「3000万円の家を買うと、いくら払うのか」を住宅ローンの元利均等返済で計算する。
金利は2026年8月時点の実勢:
  - 変動金利  年1.025%(大手行の店頭からの引き下げ後・最優遇の水準)
  - 全期間固定 年3.140%(フラット35の最頻金利。借入21〜35年・融資率9割以下・団信付き)

元利均等返済の毎月返済額 m は、借入額P・月利i・回数n に対して
    m = P * i / (1 - (1+i)^-n)
実際の返済は円未満を丸めるので、総額はこの計算より数百円ずれることがある。
動画では万円単位までしか出さないため、丸めの影響は表示に出ない。
"""
PRINCIPAL = 30_000_000     # 借入額
YEARS = 35                 # 返済期間
RATE_VAR = 1.025           # 変動金利(年%・2026年8月)
RATE_FIX = 3.140           # 全期間固定(年%・2026年7月のフラット35最頻金利)


def monthly(principal: float, rate_pct: float, years: int):
    """元利均等返済の毎月返済額と総返済額。"""
    n = years * 12
    i = rate_pct / 100 / 12
    m = principal * i / (1 - (1 + i) ** -n)
    return m, m * n, n


def main():
    m_var, total_var, n = monthly(PRINCIPAL, RATE_VAR, YEARS)
    m_fix, total_fix, _ = monthly(PRINCIPAL, RATE_FIX, YEARS)
    int_var = total_var - PRINCIPAL
    int_fix = total_fix - PRINCIPAL
    diff = total_fix - total_var

    assert n == 420, n
    # 変動1.025%
    assert round(m_var) == 85_036, round(m_var)
    assert round(total_var / 10_000) == 3_571, round(total_var / 10_000)
    assert round(int_var / 10_000) == 571, round(int_var / 10_000)
    # 固定3.14%
    assert round(m_fix) == 117_812, round(m_fix)
    assert round(total_fix / 10_000) == 4_948, round(total_fix / 10_000)
    assert round(int_fix / 10_000) == 1_948, round(int_fix / 10_000)
    # 差
    assert round(diff / 10_000) == 1_377, round(diff / 10_000)
    # 図の内訳(積み上げ棒)が総額と合うこと
    assert 3_000 + 571 == 3_571 and 3_000 + 1_948 == 4_948

    print("S013 verify: ALL OK")
    print(f"  借入 {PRINCIPAL:,}円 / {YEARS}年 = {n}回(元利均等)")
    print(f"  金利 {RATE_VAR}%: 毎月{m_var:,.0f}円 × {n}回 = {total_var:,.0f}円"
          f"(画面は{total_var / 10_000:.0f}万円)")
    print(f"       うち利息 {int_var:,.0f}円(画面は{int_var / 10_000:.0f}万円)")
    print(f"  金利 {RATE_FIX}%: 毎月{m_fix:,.0f}円 × {n}回 = {total_fix:,.0f}円"
          f"(画面は{total_fix / 10_000:.0f}万円)")
    print(f"       うち利息 {int_fix:,.0f}円(画面は{int_fix / 10_000:.0f}万円)")
    print(f"  差   {diff:,.0f}円(画面は{diff / 10_000:.0f}万円)")


if __name__ == "__main__":
    main()
