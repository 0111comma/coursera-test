#!/usr/bin/env python3
"""S033「Netflix・Spotify・Amazonプライムの3つ。30年でいくらか」の数値検証。

**前提の額は調べたものであって、置いたものではない。**(2026-08-24)
経緯は docs/research/subsc-2026-08-24.md。
最初の版は「月5000円」を根拠なしで置いていて、ユーザーに
「多くの人がどれぐらい払ってるかちゃんと調査してから」と指摘された。

| 前提 | 値 | 根拠 | 確度 |
|---|---|---|---|
| Netflix スタンダード | 1,590円 | 2026年5月時点で変更なし | B |
| Spotify Premium | 1,080円 | **980円説もあり割れている。要確認** | B- |
| Amazonプライム | 年5,900円(月492円) | 2023年8月改定 | B |
| 35歳→65歳 | 30年=360か月 | 仮定(docs/persona.md の P-M) | 仮定 |
| 利回り | 年5% | 仮定。元本保証ではない | 仮定 |

**確度Bなのは、この環境から公式ページを開けないため**(egress proxy が
全ドメインを遮断)。検索スニペットの突き合わせまでしかできていない。

裏づけ: LINEリサーチ(2025年10月・n=3,148)で支払額は「3,000円未満」が
6割台半ば。**実サービスの積み上げ3,162円と、分布の境界が一致した。**
独立した2つの見方が同じ額を指したので、前提として使う。
"""
SERVICES = [
    ("Netflix スタンダード", 1_590),
    ("Spotify Premium", 1_080),
    ("Amazonプライム(年5900円÷12)", 492),
]
MONTHLY = sum(v for _, v in SERVICES)      # 3,162円
START_AGE = 35
END_AGE = 65
MONTHS = (END_AGE - START_AGE) * 12        # 360か月
DAYS_PER_MONTH = 30                        # 「1日あたり」を出すための概数


def future_value(monthly: int, months: int, annual_rate: float) -> float:
    """毎月末に monthly を積み、残りを年利 annual_rate で運用したときの残高。"""
    bal = 0.0
    for _ in range(months):
        bal = bal * (1 + annual_rate / 12) + monthly
    return bal


CASES = [(0.00, "ただ貯める"), (0.03, "年3%で運用"), (0.05, "年5%で運用")]
RESULT = {r: future_value(MONTHLY, MONTHS, r) for r, _ in CASES}

PRINCIPAL = MONTHLY * MONTHS               # 出したお金の合計
FV5 = RESULT[0.05]
DAILY = MONTHLY / DAYS_PER_MONTH
ONE = 1_080                                # 1つだけ止めた場合(Spotify)
ONE_PRINCIPAL = ONE * MONTHS
ONE_FV5 = future_value(ONE, MONTHS, 0.05)

if __name__ == "__main__":
    print("30代男性の典型的な3つ(docs/research/subsc-2026-08-24.md):")
    for n, v in SERVICES:
        print(f"  {n:32} {v:>6,}円")
    print(f"  {'合計':32} {MONTHLY:>6,}円/月")
    assert MONTHLY == 3_162, MONTHLY

    print(f"\n1日あたり: {MONTHLY:,} ÷ {DAYS_PER_MONTH} = {DAILY:.0f}円")
    print(f"{START_AGE}歳→{END_AGE}歳 = {END_AGE - START_AGE}年 = {MONTHS}か月")
    # 台本は「月3162円を、360回。」と**回数**でも言う(2026-08-29 審査6周目。
    # 期間(30年)と回数(360回)で役割を分けた)。360回 = 360か月 = 毎月1回の支払い
    print(f"払う回数: 月1回 × {MONTHS}か月 = {MONTHS}回")
    print(f"出したお金: {MONTHLY:,} × {MONTHS} = {PRINCIPAL:,}円")
    assert MONTHS == 360 and PRINCIPAL == 1_138_320, (MONTHS, PRINCIPAL)

    for r, label in CASES:
        print(f"  {label:12}: {RESULT[r]:,.0f}円")

    # 台本で**声に出す**丸めた値。丸めが嘘になっていないかを機械で確かめる
    R_DAILY = 105                       # 「1日105円」
    R_PRINCIPAL = 114                   # 「114万円」(万円単位で四捨五入)
    R_FV5 = 263                         # 「263万円」
    assert round(DAILY) == R_DAILY, DAILY
    assert round(PRINCIPAL / 10_000) == R_PRINCIPAL, PRINCIPAL / 10_000
    assert round(FV5 / 10_000) == R_FV5, FV5 / 10_000
    print(f"\n台本で言う値: 1日{R_DAILY}円 / 出したお金{R_PRINCIPAL}万円 / "
          f"年5%なら{R_FV5}万円 ✓")

    print(f"\n1つ({ONE:,}円)だけ止めた場合:")
    print(f"  出したお金 {ONE_PRINCIPAL:,}円 / 年5%(仮定) {ONE_FV5:,.0f}円")
    # 台本で声に出す丸めた値。zentei が「出どころ不明」と言わないよう、
    # **万円の単位でも必ず出力する**
    # **切り捨てない。**898,839円を「89万円」と言うのは S032 の「82歳」と同じ誤り。
    R_ONE_P = round(ONE_PRINCIPAL / 10_000)      # 39万円
    R_ONE_FV = round(ONE_FV5 / 10_000)           # 90万円
    assert R_ONE_P == 39 and R_ONE_FV == 90, (R_ONE_P, R_ONE_FV)
    print(f"  台本で言う値: 出したお金 約{R_ONE_P}万円 / "
          f"年5%と仮定して 約{R_ONE_FV}万円 ✓")
