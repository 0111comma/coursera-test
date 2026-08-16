#!/usr/bin/env python3
"""S011 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

「年金は、何歳まで生きたら払った分を取り返せるのか」を国民年金で計算する。
2026年度(令和8年度)の保険料と年金額が、そのまま続いた場合の単純計算。
実際は毎年改定されるので、この前提はバッジと概要欄で明示する。
"""
PREMIUM = 17_920        # 国民年金の保険料(月額・2026年度)
YEARS_PAY = 40          # 20歳から60歳まで
PENSION = 70_608        # 老齢基礎年金 満額(月額・2026年度)
START_AGE = 65          # 受け取り開始
LIFE_M = 81.35          # 平均寿命 男性(2025年 簡易生命表)
LIFE_F = 87.33          # 平均寿命 女性(同上)


def main():
    paid = PREMIUM * 12 * YEARS_PAY
    per_year = PENSION * 12
    break_even_years = paid / per_year
    break_even_age = START_AGE + break_even_years
    plus_years_m = LIFE_M - break_even_age
    plus_m = plus_years_m * per_year

    assert paid == 8_601_600, paid
    assert round(paid / 10_000) == 860, "画面表示の860万円と不一致"
    assert per_year == 847_296, per_year
    assert round(per_year / 10_000) == 85, "画面表示の85万円と不一致"
    assert round(break_even_years, 1) == 10.2, round(break_even_years, 2)
    assert int(break_even_age) == 75, break_even_age
    assert round(plus_years_m) == 6, plus_years_m
    assert round(plus_m / 10_000) == 525, round(plus_m / 10_000)
    assert round(plus_m / 10_000 / 10) * 10 == 530, "画面表示の約530万円と不一致"

    print("S011 verify: ALL OK")
    print(f"  保険料 月{PREMIUM:,}円 × 12ヶ月 × {YEARS_PAY}年 = {paid:,}円"
          f"(画面は約{paid / 10_000:.0f}万円)")
    print(f"  年金   月{PENSION:,}円 × 12ヶ月 = {per_year:,}円"
          f"(画面は約{per_year / 10_000:.0f}万円)")
    print(f"  元が取れるまで: {paid:,} ÷ {per_year:,} = {break_even_years:.2f}年")
    print(f"  → {START_AGE}歳 + {break_even_years:.1f}年 = {break_even_age:.1f}歳(画面は75歳)")
    print(f"  男性の平均寿命 {LIFE_M}歳まで生きた場合:"
          f" {plus_years_m:.1f}年ぶん = {plus_m:,.0f}円(画面は約{plus_m / 10_000:.0f}万円)")
    print(f"  女性の平均寿命 {LIFE_F}歳なら:"
          f" {(LIFE_F - break_even_age) * per_year:,.0f}円")


if __name__ == "__main__":
    main()
