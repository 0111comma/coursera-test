#!/usr/bin/env python3
"""S013 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

「3000万円の家を、変動金利と固定金利で借りたらどうちがうか」を計算し、
**どちらが得だったのか**まで数字で答える(ループ62のユーザー指摘)。

金利は2026年8月時点の実勢:
  - 変動金利  年1.025%(大手行の店頭からの引き下げ後・最優遇の水準)
  - 全期間固定 年3.140%(フラット35の最頻金利。借入21〜35年・融資率9割以下・団信付き)

元利均等返済の毎月返済額 m は、借入額P・月利i・回数n に対して
    m = P * i / (1 - (1+i)^-n)
変動金利は途中で金利が変わると、その時点の残高と残り回数で計算し直す。
(5年ルール・125%ルールは毎月の額の変わり方を抑えるだけで、総額は変えない)
"""
PRINCIPAL = 30_000_000     # 借入額
YEARS = 35                 # 返済期間
RATE_VAR = 1.025           # 変動金利(年%・2026年8月)
RATE_FIX = 3.140           # 全期間固定(年%・2026年7月のフラット35最頻金利)
STEP_AFTER_YEARS = 5       # 変動が上がると仮定する時点


def monthly(principal: float, rate_pct: float, n: int) -> float:
    """元利均等返済の毎月返済額。"""
    i = rate_pct / 100 / 12
    return principal * i / (1 - (1 + i) ** -n)


def balance_after(principal: float, rate_pct: float, n: int, k: int) -> float:
    """元利均等で k 回返した時点の残高。"""
    i = rate_pct / 100 / 12
    m = monthly(principal, rate_pct, n)
    b = principal
    for _ in range(k):
        b = b * (1 + i) - m
    return b


def total_if_steps_up(rate_after: float) -> float:
    """最初の5年は1.025%、そのあと rate_after が最後まで続いた場合の総返済額。"""
    n = YEARS * 12
    k = STEP_AFTER_YEARS * 12
    m_low = monthly(PRINCIPAL, RATE_VAR, n)
    b = balance_after(PRINCIPAL, RATE_VAR, n, k)
    return m_low * k + monthly(b, rate_after, n - k) * (n - k)


def solve_break_even() -> float:
    """5年後に何%まで上がって続いたら、全期間固定と総返済額が並ぶか。"""
    target = monthly(PRINCIPAL, RATE_FIX, YEARS * 12) * YEARS * 12
    lo, hi = RATE_VAR, 20.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if total_if_steps_up(mid) < target:
            lo = mid
        else:
            hi = mid
    return round(lo, 2)


def main():
    n = YEARS * 12
    m_var = monthly(PRINCIPAL, RATE_VAR, n)
    m_fix = monthly(PRINCIPAL, RATE_FIX, n)
    total_var, total_fix = m_var * n, m_fix * n
    diff = total_fix - total_var
    # 変動が1%上がったときの毎月の増え方(借り入れ直後に上がった場合)
    m_var_up = monthly(PRINCIPAL, RATE_VAR + 1.0, n)
    monthly_up = m_var_up - m_var
    break_even = solve_break_even()

    assert n == 420, n
    assert round(m_var) == 85_036, round(m_var)
    assert round(total_var / 10_000) == 3_571, round(total_var / 10_000)
    assert round(m_fix) == 117_812, round(m_fix)
    assert round(total_fix / 10_000) == 4_948, round(total_fix / 10_000)
    assert round(diff / 10_000) == 1_377, round(diff / 10_000)
    # 画面「1万4728円」
    assert round(monthly_up) == 14_728, round(monthly_up)
    # 画面「3.83%」。並ぶ点なので、その金利での総額が固定とほぼ一致すること。
    # 金利0.01%は総額およそ5万4千円に相当するので、小数2桁の表示ではこれ以上は寄せられない
    assert break_even == 3.83, break_even
    gap = abs(total_if_steps_up(break_even) - total_fix)
    assert gap < 60_000, f"分岐点がずれている({gap:,.0f}円)"
    assert total_if_steps_up(3.82) < total_fix < total_if_steps_up(3.84), "並ぶ点を挟めていない"
    # 分岐点は固定金利より高い。つまり「固定と同じ率まで上がる」では固定に届かない
    # (変動は最初の5年ぶん、安い金利で返しているため)
    assert break_even > RATE_FIX, "変動が先に安く返した分が効いていない"
    # 積み上げ棒の内訳が総額と合うこと
    assert 3_000 + 571 == 3_571 and 3_000 + 1_948 == 4_948

    print("S013 verify: ALL OK")
    print(f"  借入 {PRINCIPAL:,}円 / {YEARS}年 = {n}回(元利均等)")
    print(f"  変動 {RATE_VAR}%: 毎月{m_var:,.0f}円 → 総返済{total_var:,.0f}円"
          f"(画面は{total_var / 10_000:.0f}万円)")
    print(f"  固定 {RATE_FIX}%: 毎月{m_fix:,.0f}円 → 総返済{total_fix:,.0f}円"
          f"(画面は{total_fix / 10_000:.0f}万円)")
    print(f"  差   {diff:,.0f}円(画面は{diff / 10_000:.0f}万円)")
    print(f"  変動が1%上がると 毎月 {m_var:,.0f} → {m_var_up:,.0f}円"
          f"(+{monthly_up:,.0f}円/月・年+{monthly_up * 12:,.0f}円)")
    print(f"  分岐点: 5年後に {break_even}% まで上がってそのまま続くと"
          f" 総返済{total_if_steps_up(break_even):,.0f}円 ≒ 固定と同じ")
    print(f"  (0.01%の差は総額およそ54,000円。表示は小数2桁なので"
          f" 固定との差は{abs(total_if_steps_up(break_even) - total_fix):,.0f}円残る)")


if __name__ == "__main__":
    main()
