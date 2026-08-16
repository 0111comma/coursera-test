#!/usr/bin/env python3
"""L002 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

この動画が答える問い:
  **変動金利は、いつ・何%まで上がったら、固定金利に負けるのか。**

S013(ショート)は「5年後なら3.83%」まで答えた。長尺では**上がる時期を動かす**。
上がるのが遅いほど、変動金利は安く返した期間が長いので、
**分かれ目の金利は高くなる**。この曲線がこの動画の主役。

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


def total_fixed() -> float:
    return monthly(PRINCIPAL, RATE_FIX, YEARS * 12) * YEARS * 12


def total_if_steps_up(rate_after: float, after_years: int,
                      prepay: int = 0, prepay_at_years: int = 0) -> float:
    """after_years 年後に rate_after まで上がり、そのまま最後まで続いた場合の総返済額。

    prepay を渡すと prepay_at_years 年の時点で、その額を繰上返済する
    (期間短縮ではなく返済額軽減。残りの回数はそのままで毎月の額が下がる形)。
    """
    n = YEARS * 12
    k = after_years * 12
    m_low = monthly(PRINCIPAL, RATE_VAR, n)
    paid = 0.0
    b = PRINCIPAL

    # 上がるまで(必要なら途中で繰上返済)
    events = sorted({k, prepay_at_years * 12 if prepay else None} - {None})
    cur_rate, cur_m, pos = RATE_VAR, m_low, 0
    for e in events:
        i = cur_rate / 100 / 12
        for _ in range(e - pos):
            b = b * (1 + i) - cur_m
        paid += cur_m * (e - pos)
        pos = e
        if prepay and e == prepay_at_years * 12:
            b -= prepay
            paid += prepay
            cur_m = monthly(b, cur_rate, n - pos)
        if e == k:
            cur_rate = rate_after
            cur_m = monthly(b, cur_rate, n - pos)
    paid += cur_m * (n - pos)
    return paid


def solve_break_even(after_years: int, **kw) -> float:
    """after_years 年後に何%まで上がって続いたら、固定金利と総返済額が並ぶか。"""
    target = total_fixed()
    lo, hi = RATE_VAR, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if total_if_steps_up(mid, after_years, **kw) < target:
            lo = mid
        else:
            hi = mid
    return round(lo, 2)


def main():
    n = YEARS * 12
    m_var = monthly(PRINCIPAL, RATE_VAR, n)
    m_fix = monthly(PRINCIPAL, RATE_FIX, n)
    total_var, tf = m_var * n, total_fixed()
    diff = tf - total_var
    m_var_up = monthly(PRINCIPAL, RATE_VAR + 1.0, n)
    monthly_up = m_var_up - m_var

    # --- 章1: 上がらなかった場合の差 ---
    assert n == 420
    assert round(m_var) == 85_036, round(m_var)
    assert round(total_var / 10_000) == 3_571, round(total_var / 10_000)
    assert round(m_fix) == 117_812, round(m_fix)
    assert round(tf / 10_000) == 4_948, round(tf / 10_000)
    assert round(diff / 10_000) == 1_377, round(diff / 10_000)

    # --- 章2: 1%上がったときの毎月の増え方 ---
    assert round(monthly_up) == 14_728, round(monthly_up)
    # 画面には「毎月1万4728円 × 12ヶ月 = 年17万6736円」と出す。
    # 端数を丸める前の値を12倍すると176,742円で6円ずれるが、
    # **見ている人が画面の数字を自分で掛け算して合う**ほうを採る(鎖が切れないため)。
    assert round(monthly_up) * 12 == 176_736
    assert abs(round(monthly_up * 12) - 176_736) <= 10, round(monthly_up * 12)

    # --- 章3: 上がる時期ごとの分かれ目(この動画の主役) ---
    table = {y: solve_break_even(y) for y in (0, 5, 10, 15, 20, 25)}
    for y, r in table.items():
        # 分かれ目の総額が固定とほぼ並ぶこと(0.01%刻みの表示限界ぶんは残る)
        gap = abs(total_if_steps_up(r, y) - tf)
        assert gap < 200_000, (y, r, gap)
        assert total_if_steps_up(r - 0.01, y) < tf < total_if_steps_up(r + 0.01, y), (y, r)
    # 上がるのが遅いほど、分かれ目は高くなる(単調)
    ys = sorted(table)
    assert all(table[a] < table[b] for a, b in zip(ys, ys[1:])), table
    # 借りた直後に上がる場合の分かれ目は、固定金利そのもの
    assert abs(table[0] - RATE_FIX) < 0.02, table[0]
    assert table[5] == 3.83, table[5]

    # --- 章4: 繰上返済すると分かれ目はどう動くか ---
    # 5年の時点で300万円を繰り上げ(返済額軽減)、そのあと金利が上がる場合。
    be5 = table[5]
    be5_prepay = solve_break_even(5, prepay=3_000_000, prepay_at_years=5)
    assert be5_prepay > be5, (be5, be5_prepay)
    # 繰上返済しない場合の変動の総額(上がらない前提)との差
    total_var_prepay = total_if_steps_up(RATE_VAR, 5, prepay=3_000_000, prepay_at_years=5)
    saved = total_var - total_var_prepay
    assert saved > 0

    print("L002 verify: ALL OK")
    print(f"  借入 {PRINCIPAL:,}円 / {YEARS}年 = {n}回(元利均等)")
    print(f"  変動 {RATE_VAR}%: 毎月{m_var:,.0f}円 → 総返済{total_var:,.0f}円"
          f"(画面は{total_var / 10_000:.0f}万円)")
    print(f"  固定 {RATE_FIX}%: 毎月{m_fix:,.0f}円 → 総返済{tf:,.0f}円"
          f"(画面は{tf / 10_000:.0f}万円)")
    print(f"  差   {diff:,.0f}円(画面は{diff / 10_000:.0f}万円)")
    print(f"  変動が1%上がると 毎月 +{monthly_up:,.0f}円(年+{monthly_up * 12:,.0f}円)")
    print("  ★ 上がる時期ごとの分かれ目(そこまで上がって最後まで続く前提):")
    for y in ys:
        print(f"      {y:2d}年後に上がる → {table[y]:.2f}%"
              f"(総返済 {total_if_steps_up(table[y], y):,.0f}円)")
    print(f"  ★ 5年で300万円を繰上返済(返済額軽減)すると、分かれ目は"
          f" {be5:.2f}% → {be5_prepay:.2f}% に上がる")
    print(f"     (上がらない前提での総返済は {total_var:,.0f} → {total_var_prepay:,.0f}円、"
          f"{saved:,.0f}円ぶん少ない)")


if __name__ == "__main__":
    main()
