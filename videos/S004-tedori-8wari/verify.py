#!/usr/bin/env python3
"""S004: 年収400万円の手取り(約8割)と天引きの内訳の検証。

モデル(概要欄にも明記):
- 年収400万円・独身・40歳未満(介護保険なし)・東京都・協会けんぽ・扶養なし
- 社会保険料は「年収×本人負担率」の概算(実際は標準報酬月額の等級で数千円程度の差)
- 2026年度(令和8年度)の料率・税制:
  - 健康保険(東京) 9.85% 労使折半 → 本人4.925%
  - 子ども・子育て支援金 0.23% 労使折半 → 本人0.115%(2026年4月〜)
  - 厚生年金 18.3% 労使折半 → 本人9.15%
  - 雇用保険(一般) 本人0.50%(2026年度引下げ)
  - 所得税: 給与所得控除(年収400万円→124万円)、基礎控除88万円
    (2025年改正: 合計所得132万超336万以下の時限上乗せ、2025・2026年分)、復興特別所得税2.1%
  - 住民税: 基礎控除43万円、所得割10%、均等割4,000円+森林環境税1,000円、調整控除2,500円
出典: 協会けんぽ(令和8年度保険料額表)・日本年金機構・厚生労働省(雇用保険料率)・
      国税庁/財務省(令和7年度税制改正)。確認日2026-08-12
"""

INCOME = 4_000_000

# --- 社会保険(本人負担率の概算) ---
KENPO = 0.0985 / 2          # 4.925%
SHIENKIN = 0.0023 / 2       # 0.115%
KOSEI = 0.183 / 2           # 9.15%
KOYO = 0.0050               # 0.50%

sh_kenpo = INCOME * KENPO           # 197,000
sh_shien = INCOME * SHIENKIN        # 4,600
sh_kosei = INCOME * KOSEI           # 366,000
sh_koyo = INCOME * KOYO             # 20,000
SHAHO = sh_kenpo + sh_shien + sh_kosei + sh_koyo   # 587,600

# --- 所得税 ---
KYUYO_KOJO = INCOME * 0.20 + 440_000     # 給与所得控除 1,240,000(年収360万超660万以下)
SHOTOKU = INCOME - KYUYO_KOJO            # 給与所得 2,760,000
KISO_SHOTOKU = 880_000                   # 基礎控除(所得132万超336万以下・2026年分)
kazei_shotoku = int((SHOTOKU - KISO_SHOTOKU - SHAHO) // 1000 * 1000)  # 1,292,000
shotokuzei = kazei_shotoku * 0.05 * 1.021                             # 65,956.6

# --- 住民税 ---
KISO_JUMIN = 430_000
kazei_jumin = int((SHOTOKU - KISO_JUMIN - SHAHO) // 1000 * 1000)      # 1,742,000
juminzei = kazei_jumin * 0.10 - 2_500 + 4_000 + 1_000                 # 176,700

TOTAL_OFF = SHAHO + shotokuzei + juminzei    # 830,256.6
TEDORI = INCOME - TOTAL_OFF                  # 3,169,743
RATE = TEDORI / INCOME                       # 79.24%

# --- 台本の数字と照合 ---
assert round(sh_kosei / 1000) == 366        # 厚生年金 36万6千円
assert round(sh_kenpo / 1000) == 197        # 健康保険 19万7千円
assert round(sh_shien / 100) == 46          # 支援金 4,600円
assert round(sh_koyo / 1000) == 20          # 雇用保険 2万円
assert round(juminzei / 1000) == 177        # 住民税 17万7千円
assert round(shotokuzei / 1000) == 66       # 所得税 6万6千円
assert round(TOTAL_OFF / 10_000) == 83      # 合計 約83万円
assert round(TEDORI / 10_000) == 317        # 手取り 約317万円
assert 0.79 < RATE < 0.80                   # 約8割

print(f"社会保険料: {SHAHO:,.0f}円 (厚年{sh_kosei:,.0f}/健保{sh_kenpo:,.0f}/支援金{sh_shien:,.0f}/雇用{sh_koyo:,.0f})")
print(f"所得税: {shotokuzei:,.0f}円 / 住民税: {juminzei:,.0f}円")
print(f"引かれる合計: {TOTAL_OFF:,.0f}円 → 約83万円")
print(f"手取り: {TEDORI:,.0f}円 ({RATE:.1%}) → 約317万円・約8割")
print("OK: すべての数値が台本と一致")
