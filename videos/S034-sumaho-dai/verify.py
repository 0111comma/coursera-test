#!/usr/bin/env python3
"""S034「スマホ代、大手のままだと1年でいくら違うか」の数値検証。

P-M(35歳・男性・会社員)向け。欲求A(知らないうちに引かれているものを止めたい)。

| 前提 | 値 | 出どころ | 確度 |
|---|---|---|---|
| スマホ代の平均 | 4,356円/月 | MM総研 2025年1月調査(端末代の分割を除く) | B |
| 大手4ブランド | 5,025円/月 | 同上 | B |
| MVNO | 1,961円/月 | 同上 | B |
| ahamo | 2,970円/月 | 30GB + 5分かけ放題 | B |
| 35歳→65歳 | 30年 = 360か月 | 仮定(docs/persona.md の P-M) | 仮定 |
| 年5% | 運用の利回り | **仮定。**元本保証ではない | 仮定 |

**確度Bなのは、この環境から一次資料を開けないため**(egress proxy が
m2ri.jp も各社サイトも遮断)。検索スニペットの突き合わせまで。
**投稿前にユーザーの環境で料金を確認すること。**
"""
AVERAGE = 4_356        # スマホ代の平均(MM総研 2025年1月)
MAJOR = 5_025          # 大手4ブランドの平均
ONLINE = 2_970         # ahamo(30GB + 5分かけ放題)
MVNO = 1_961           # MVNOの平均

START_AGE = 35
END_AGE = 65
MONTHS = (END_AGE - START_AGE) * 12     # 360か月

DIFF = MAJOR - ONLINE                   # 大手 − オンライン専用
YEAR = DIFF * 12                        # 1年ぶんの差
LIFE = DIFF * MONTHS                    # 30年ぶんの差


def future_value(monthly: int, months: int, annual_rate: float) -> float:
    bal = 0.0
    for _ in range(months):
        bal = bal * (1 + annual_rate / 12) + monthly
    return bal


CASES = [(0.00, "ただ貯める"), (0.03, "年3%で運用"), (0.05, "年5%で運用")]
RESULT = {r: future_value(DIFF, MONTHS, r) for r, _ in CASES}
FV5 = RESULT[0.05]

if __name__ == "__main__":
    print("スマホ代の月額(MM総研 2025年1月調査):")
    for n, v in (("全体の平均", AVERAGE), ("大手4ブランド", MAJOR),
                 ("ahamo(30GB+5分かけ放題)", ONLINE), ("MVNO", MVNO)):
        print(f"  {n:26} {v:>6,}円")

    print(f"\n大手 {MAJOR:,} − ahamo {ONLINE:,} = **{DIFF:,}円/月**")
    assert DIFF == 2_055, DIFF
    print(f"1年ぶん: {DIFF:,} × 12 = **{YEAR:,}円**")
    assert YEAR == 24_660, YEAR
    print(f"{START_AGE}歳→{END_AGE}歳({MONTHS}か月): {DIFF:,} × {MONTHS} = **{LIFE:,}円**")
    assert LIFE == 739_800, LIFE

    print("\n同じ差額を積んだ場合(いずれも仮定):")
    for r, label in CASES:
        print(f"  {label:12}: {RESULT[r]:,.0f}円")

    # 台本で**声に出す**丸めた値。切り捨てない(S032の「82歳」の再発防止)
    R_DIFF, R_YEAR = 2_055, 2                 # 「約2万円」ではなく「2万4660円」で言う
    R_LIFE = round(LIFE / 10_000)             # 74万円
    R_FV5 = round(FV5 / 10_000)
    assert R_LIFE == 74, R_LIFE
    print(f"\n台本で言う値: 月{DIFF:,}円 / 1年{YEAR:,}円 / "
          f"30年{R_LIFE}万円 / 年5%と仮定して{R_FV5}万円 ✓")

    # MVNOまで下げた場合(参考。台本では使わないが概要欄に出す)
    d2 = MAJOR - MVNO
    print(f"\n(参考)大手 → MVNO: 月{d2:,}円 / 1年{d2*12:,}円 / 30年{d2*MONTHS/10_000:.0f}万円")
