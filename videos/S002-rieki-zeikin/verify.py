#!/usr/bin/env python3
"""S002: 積立の利益にかかる税金(20.315%)とNISAの数値検証。

計算方法:
- 利益はS001と同一の積立将来価値(毎月末積立・月次複利・年5%仮定)から。
  動画では四捨五入した「171万円」を宣言値として使う。
- 税率20.315% = 所得税15% + 復興特別所得税0.315%(=15%×2.1%、2037年12月まで) + 住民税5%
  出典: 国税庁「株式・配当・利子と税」(確認日2026-08-12)
- 手数料・為替・損益通算等は考慮しない。NISAは譲渡益非課税(金融庁NISA特設サイト)。
"""

RATE = 0.05
MONTHLY = 10_000


def fv(months: int, monthly: int = MONTHLY, annual: float = RATE) -> float:
    r = annual / 12
    return monthly * ((1 + r) ** months - 1) / r


def man(x: float) -> float:
    return x / 10_000


# --- 税率の構成 ---
INCOME_TAX = 0.15
RECON_TAX = INCOME_TAX * 0.021          # 復興特別所得税 0.00315
RESIDENT_TAX = 0.05
TAX_RATE = INCOME_TAX + RECON_TAX + RESIDENT_TAX
assert round(TAX_RATE, 5) == 0.20315, TAX_RATE

# --- 20年ケース(S001接続) ---
gain20_exact = fv(240) - 2_400_000      # 1,710,337円
GAIN = 1_710_000                        # 動画の宣言値「171万円」
tax171 = GAIN * TAX_RATE                # 347,386.65円
net171 = GAIN - tax171                  # 1,362,613.35円
assert round(man(gain20_exact)) == 171, gain20_exact
assert round(tax171 / 1000) == 347, tax171          # 「34万7千円」
assert round(man(net171)) == 136, net171            # 「136万円」
# 宣言値でなく厳密値でも表示は同じ「34万7千円」になることを確認
assert round(gain20_exact * TAX_RATE / 1000) == 347

# --- 30年ケース ---
gain30 = fv(360) - 3_600_000            # 4,722,586円
tax30 = gain30 * TAX_RATE               # 959,393円
assert round(man(gain30)) == 472, gain30
assert round(man(tax30)) == 96, tax30

# --- 早見表(利益別の税額) ---
TABLE_GAINS = [500_000, 1_000_000, GAIN, 3_000_000, 5_000_000]
taxes = [g * TAX_RATE for g in TABLE_GAINS]
disp = [round(t / 1000) / 10 for t in taxes]        # 万円1桁表示
assert disp == [10.2, 20.3, 34.7, 60.9, 101.6], disp

print(f"税率: {TAX_RATE:.5f} (所得税{INCOME_TAX} + 復興{RECON_TAX:.5f} + 住民{RESIDENT_TAX})")
print(f"利益(20年, 厳密): {gain20_exact:,.0f}円 → 宣言値 {GAIN:,}円")
print(f"税金(利益171万円): {tax171:,.2f}円 → 34万7千円")
print(f"手取り: {net171:,.2f}円 → 約136万円")
print(f"利益(30年): {gain30:,.0f}円 → 約472万円 / 税金: {tax30:,.0f}円 → 約96万円")
print("早見表(利益→税額万円):", dict(zip([man(g) for g in TABLE_GAINS], disp)))
print("OK: すべての数値が台本と一致")
