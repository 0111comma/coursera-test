#!/usr/bin/env python3
"""S032「1000万円を毎月5万円ずつ取り崩すと、何歳で尽きるか」の数値検証。

**前提の数値には、それぞれ根拠がある。**(2026-08-23の作り直し)
台本では、どの数値も「なぜその数か」を言ってから使う。

| 前提 | 値 | 根拠 |
|---|---|---|
| 取り崩しを始める年齢 | 65歳 | 老齢基礎年金の支給開始は**原則65歳**(日本年金機構) |
| 何歳まで持たせるか | 90歳 | **90歳まで生きる人は、女性の2人に1人・男性の4人に1人**
|  |  | (厚生労働省 令和7年簡易生命表: 男26.7% / 女50.8%) |
| 毎月の取り崩し額 | 5万円 | 視聴者が置く仮の額。動画の問いそのもの |
| 利回り | 0% / 3% / 5% | **すべて仮定。**元本保証ではない |

出典(確認日 2026-08-23):
- 日本年金機構「老齢基礎年金の受給要件・支給開始時期・年金額」
  https://www.nenkin.go.jp/service/jukyu/seido/roureinenkin/jukyu-yoken/20150401-02.html
- 厚生労働省「令和7年(2025)簡易生命表の概況」
  https://www.mhlw.go.jp/toukei/saikin/hw/life/life25/
  平均寿命 男81.09年 / 女87.13年、65歳の平均余命 男19.47年 / 女24.38年、
  90歳まで生存する割合 男26.7% / 女50.8%
"""
PRINCIPAL = 10_000_000     # 取り崩す元手
DRAW = 50_000              # 毎月の取り崩し額(視聴者が置く仮の額)
START_AGE = 65             # 年金が始まる年齢
TARGET_AGE = 90            # ここまで持たせたい(女性の2人に1人が到達する年齢)


def months_until_empty(principal: int, draw: int, annual_rate: float,
                       cap_months: int = 1200) -> int:
    """毎月末に draw を引き、残りを年利 annual_rate で運用したときに尽きる月数。"""
    bal, m = float(principal), 0
    while bal > 0 and m < cap_months:
        bal = bal * (1 + annual_rate / 12) - draw
        m += 1
    return m


def age_at(months: int) -> tuple[int, int]:
    """START_AGE から months か月たった時点の(歳, か月)。**切り上げない。**
    200か月は16年8か月なので、尽きるのは82歳ではなく81歳8か月。"""
    total = START_AGE * 12 + months
    return total // 12, total % 12


def monthly_cap(annual_rate: float, target_age: int = TARGET_AGE) -> int:
    """target_age まで持たせるとき、毎月いくらまで取り崩せるか(1000円単位に切り捨て)。"""
    need = (target_age - START_AGE) * 12
    lo, hi = 1000, 500_000
    for _ in range(80):
        mid = (lo + hi) / 2
        if months_until_empty(PRINCIPAL, int(mid), annual_rate) >= need:
            lo = mid
        else:
            hi = mid
    return int(lo // 1000 * 1000)


CASES = [(0.00, "運用しない"), (0.03, "年3%で運用"), (0.05, "年5%で運用")]
RESULT = {r: (m := months_until_empty(PRINCIPAL, DRAW, r), m / 12, age_at(m))
          for r, _ in CASES}
CAP = {r: monthly_cap(r) for r, _ in CASES}

# 台本で使う値
MONTHS_0 = RESULT[0.00][0]                      # 200か月
EMPTY_Y, EMPTY_M = RESULT[0.00][2]              # 81歳8か月
GAP_MONTHS = TARGET_AGE * 12 - (EMPTY_Y * 12 + EMPTY_M)
CAP_0 = CAP[0.00]                               # 90歳まで持たせるときの毎月の上限
CUT = DRAW - CAP_0                              # 5万円からいくら減らすことになるか

if __name__ == "__main__":
    print(f"元手 {PRINCIPAL:,}円 / 毎月 {DRAW:,}円 取り崩し / {START_AGE}歳から")
    for r, label in CASES:
        m, y, (ay, am) = RESULT[r]
        print(f"  {label:10s}: {m:4d}か月 = {y:5.1f}年  → {ay}歳{am}か月で尽きる")

    assert MONTHS_0 == 200, MONTHS_0
    print(f"\n検算: {PRINCIPAL:,} ÷ {DRAW:,} = {PRINCIPAL // DRAW}か月"
          f" = {MONTHS_0 // 12}年{MONTHS_0 % 12}か月 ✓")
    print(f"      {START_AGE}歳 + {MONTHS_0 // 12}年{MONTHS_0 % 12}か月"
          f" = {EMPTY_Y}歳{EMPTY_M}か月 ✓")
    print(f"      {TARGET_AGE}歳まで {GAP_MONTHS // 12}年{GAP_MONTHS % 12}か月 足りない ✓")

    print(f"\n{TARGET_AGE}歳({TARGET_AGE - START_AGE}年)まで持たせるなら、毎月いくらまでか:")
    for r, label in CASES:
        print(f"  {label:10s}: 毎月 {CAP[r]:,}円まで")
    print(f"\n運用しない場合: {DRAW:,}円 → {CAP_0:,}円。**{CUT:,}円 減らすことになる** ✓")
    print(f"検算: {PRINCIPAL:,} ÷ {(TARGET_AGE - START_AGE) * 12}か月 "
          f"= {PRINCIPAL / ((TARGET_AGE - START_AGE) * 12):,.0f}円/月")
