#!/usr/bin/env python3
"""S034「働くと年金が減る」は2026年4月に基準が変わる、の数値検証。

欲求B(大きな選択を間違えたくない)+ A(取られたくない)。
**60代前半で働きながら年金を受け取る人が、年金を減らされないために
勤務や報酬を抑える調整をしていたなら、その調整をやめられる。**

| 前提 | 値 | 出どころ | 確度 |
|---|---|---|---|
| 支給停止の基準額(2025年度) | 51万円/月 | 在職老齢年金の現行基準 | B |
| 支給停止の基準額(2026年4月〜) | 65万円/月 | 令和7年法律第74号による改正 | B |
| 計算式 | (基本月額 + 総報酬月額相当額 − 基準額) ÷ 2 | 同上 | B |
| 減額されるのは老齢厚生年金のみ | 老齢基礎年金は減らない | 同上 | B |
| 例に使う基本月額 10万円 | 老齢厚生年金(報酬比例部分)の月額 | **仮定**(この動画の例として置いた値) | 仮定 |
| 例に使う給与 45万円 | 総報酬月額相当額(月給+賞与÷12) | **仮定**(この動画の例として置いた値) | 仮定 |

**確度Bなのは、この環境から一次資料を開けないため。**
egress proxy が mhlw.go.jp を遮断する(2026-08-30確認)。
社会保険労務士事務所3件・給与計算ベンダー2件の独立した解説が、
基準額(51→65万円)・計算式・施行日(2026年4月1日)・根拠法
(令和7年法律第74号、2025年6月13日成立)のすべてで一致することを確認した。

**投稿前にユーザーの環境で、日本年金機構・厚生労働省の資料を確認すること。**

法成立時点の試算は62万円だったが、賃金変動を反映して施行時点は65万円。
**基準額は毎年4月に見直される**ので、動画には必ず時点表記を入れる。
"""

# ---- 支給停止の基準額(月額)
LIMIT_OLD = 510_000        # 2025年度
LIMIT_NEW = 650_000        # 2026年4月1日から
RAISE = LIMIT_NEW - LIMIT_OLD

# ---- 例に使う人(いずれも仮定。この動画の中でだけ使う値)
BASIC = 100_000            # 基本月額 = 老齢厚生年金の月額
SALARY = 450_000           # 総報酬月額相当額 = 月給 + 直近1年の賞与 ÷ 12
TOTAL = BASIC + SALARY


def suspended(basic: int, salary: int, limit: int) -> int:
    """支給停止額(月額)。合計が基準額以下なら停止ゼロ。

    式: (基本月額 + 総報酬月額相当額 − 基準額) ÷ 2
    停止されるのは老齢厚生年金だけなので、基本月額が上限になる。
    """
    over = basic + salary - limit
    if over <= 0:
        return 0
    return min(basic, over // 2)


STOP_OLD = suspended(BASIC, SALARY, LIMIT_OLD)
STOP_NEW = suspended(BASIC, SALARY, LIMIT_NEW)
DIFF_MONTH = STOP_OLD - STOP_NEW
DIFF_YEAR = DIFF_MONTH * 12

# 旧基準で「1円でも止まる」境目の給与(基本月額10万円のとき)
BORDER_OLD = LIMIT_OLD - BASIC
BORDER_NEW = LIMIT_NEW - BASIC

if __name__ == "__main__":
    print(f"支給停止の基準額: {LIMIT_OLD:,}円 → {LIMIT_NEW:,}円"
          f"(2026年4月1日から。{RAISE:,}円の引き上げ)")
    print(f"\n例(いずれも仮定): 年金の月額 {BASIC:,}円 / 給与 {SALARY:,}円 "
          f"= 合計 {TOTAL:,}円")
    print(f"  2025年度: ({TOTAL:,} − {LIMIT_OLD:,}) ÷ 2 = "
          f"**月 {STOP_OLD:,}円 止まる**")
    print(f"  2026年4月: {TOTAL:,} は {LIMIT_NEW:,} 以下 → **止まらない**")
    assert STOP_OLD == 20_000, STOP_OLD
    assert STOP_NEW == 0, STOP_NEW
    print(f"\n差: 月 {DIFF_MONTH:,}円 / 年 {DIFF_YEAR:,}円")
    assert DIFF_YEAR == 240_000, DIFF_YEAR

    print(f"\n「1円でも止まる」境目の給与(年金月額 {BASIC:,}円のとき):")
    print(f"  2025年度: 給与 {BORDER_OLD:,}円 を超えると止まりはじめる")
    print(f"  2026年4月: 給与 {BORDER_NEW:,}円 を超えると止まりはじめる")
    assert BORDER_OLD == 410_000 and BORDER_NEW == 550_000

    print("\n給与別の早見(年金の月額を10万円と仮定):")
    print(f"  {'給与':>9} | {'2025年度':>9} | {'2026年4月〜':>10}")
    for sal in (350_000, 410_000, 450_000, 500_000, 550_000, 600_000):
        a = suspended(BASIC, sal, LIMIT_OLD)
        b = suspended(BASIC, sal, LIMIT_NEW)
        print(f"  {sal:>7,}円 | {a:>7,}円 | {b:>8,}円")

    print("\n台本で言う値: 基準51万円→65万円 / 例は年金10万+給与45万 / "
          f"月2万円→0円 / 年24万円 ✓")
