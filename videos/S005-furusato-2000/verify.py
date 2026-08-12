#!/usr/bin/env python3
"""S005: ふるさと納税の実質2000円と上限額の検証。

モデル: 年収400万円・独身・40歳未満・東京(S004と同一。住民税所得割はS004の計算から)
- 寄付4万円の控除内訳(ワンストップ特例でない確定申告ベースの式):
  所得税還付 = (寄付-2000)×所得税率5%×1.021
  住民税基本控除 = (寄付-2000)×10%
  住民税特例控除 = (寄付-2000)×(90%-5%×1.021)
  → 合計 = 寄付-2000(全額控除の範囲内なら)
- 上限の目安 = 住民税所得割×20% / (90%-所得税率×1.021) + 2000
- 年収別の目安は総務省「全額控除されるふるさと納税額(年間上限)の目安」の転記
  https://www.soumu.go.jp/main_sosiki/jichi_zeisei/czaisei/czaisei_seido/furusato/mechanism/deduction.html
  (総務省表は社会保険料を給与収入の15%と仮定した目安。確認日2026-08-12)
"""

# --- S004と同一モデルの住民税所得割(調整控除後) ---
INCOME = 4_000_000
SHAHO = INCOME * (0.0985 / 2 + 0.0023 / 2 + 0.183 / 2 + 0.0050)   # 587,600
SHOTOKU = INCOME - (INCOME * 0.20 + 440_000)                       # 2,760,000
kazei_j = int((SHOTOKU - 430_000 - SHAHO) // 1000 * 1000)          # 1,742,000
SHOTOKUWARI = kazei_j * 0.10 - 2_500                               # 171,700(調整控除後)

# --- 寄付4万円の内訳 ---
DONATION = 40_000
base = DONATION - 2_000                                            # 38,000
it_refund = base * 0.05 * 1.021                                    # 1,940
jt_basic = base * 0.10                                             # 3,800
jt_tokurei = base * (0.90 - 0.05 * 1.021)                          # 32,260
total_deduct = it_refund + jt_basic + jt_tokurei
assert round(total_deduct) == base, total_deduct                   # 合計38,000=寄付-2000
assert round(jt_tokurei) <= SHOTOKUWARI * 0.20, "特例控除が所得割2割以内(上限内の寄付)"

# --- 上限の自前計算と総務省目安の照合 ---
limit = SHOTOKUWARI * 0.20 / (0.90 - 0.05 * 1.021) + 2_000         # 42,451
SOUMU_LIMITS = {300: 28_000, 400: 42_000, 500: 61_000, 600: 77_000, 700: 108_000}
assert abs(limit - SOUMU_LIMITS[400]) < 2_000, limit  # 目安表(保険料15%仮定)と整合

print(f"住民税所得割(調整後): {SHOTOKUWARI:,.0f}円")
print(f"寄付{DONATION:,}円 → 控除合計 {total_deduct:,.0f}円(所得税{it_refund:,.0f}+住民税{jt_basic + jt_tokurei:,.0f}) → 自己負担2,000円")
print(f"上限の自前計算: {limit:,.0f}円 ≒ 総務省目安 {SOUMU_LIMITS[400]:,}円")
print(f"総務省目安表(独身): {SOUMU_LIMITS}")
print("OK: すべての数値が台本と一致")
