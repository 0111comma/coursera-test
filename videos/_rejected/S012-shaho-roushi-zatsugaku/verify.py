#!/usr/bin/env python3
"""S012 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

**会社があなたに払っている額と、あなたの手元に残る額の差**を出す(ループ66)。
ユーザー判定:「S12面白くない」。
旧版のオチ「会社も同じ額を払っている」は豆知識で、視聴者の何も変わらなかった。
会社の支出460万円に対して手取りは315万円、**差は145万円**。これが実害になる。

年収400万円・東京都・40歳未満(介護保険料なし)・独身・扶養なしの概算。
実際は標準報酬月額の等級表で決まるため、ここでは年収に料率を掛けた概算とする。
"""
INCOME = 4_000_000

# 2026年度の料率
KOSEI = 0.183          # 厚生年金(労使折半)
KENKO = 0.0985         # 健康保険 協会けんぽ東京都(労使折半)
KODOMO = 0.0023        # 子ども・子育て支援金(労使折半)
KOYO_ME = 0.005        # 雇用保険 本人
KOYO_CO = 0.0085       # 雇用保険 会社

# 手取りを出すための控除(所得税・住民税)
KYUYO_KOJO = 0.20      # 給与所得控除(年収360万〜660万は 収入×20%+44万円)
KYUYO_KOJO_ADD = 440_000
KISO_SHOTOKU = 580_000  # 所得税の基礎控除(2025年改正後)
KISO_JUMIN = 430_000    # 住民税の基礎控除(据え置き)
FUKKO = 1.021           # 復興特別所得税
JUMIN_RITSU = 0.10      # 住民税の所得割
JUMIN_CHOSEI = 2_500    # 調整控除
JUMIN_KINTO = 5_000     # 均等割(森林環境税1,000円を含む)


def main():
    me_rate = KOSEI / 2 + KENKO / 2 + KODOMO / 2 + KOYO_ME
    co_rate = KOSEI / 2 + KENKO / 2 + KODOMO / 2 + KOYO_CO
    me = INCOME * me_rate
    co = INCOME * co_rate
    kosei_me = INCOME * KOSEI / 2

    assert round(KOSEI / 2 * 1000) / 10 == 9.2 or round(KOSEI / 2, 4) == 0.0915
    assert round(kosei_me) == 366_000, round(kosei_me)
    assert round(me / 10_000) == 59, round(me / 10_000)
    assert round(co / 10_000) == 60, round(co / 10_000)
    assert round((me + co) / 10_000) == 119, round((me + co) / 10_000)
    assert round((INCOME + co) / 10_000) == 460, round((INCOME + co) / 10_000)

    # ここからが新しいオチ: 会社の支出 と 手取り の差(ループ66)
    kyuyo_shotoku = INCOME - (int(INCOME * KYUYO_KOJO) + KYUYO_KOJO_ADD)
    social = int(me)
    kazei_sho = (kyuyo_shotoku - social - KISO_SHOTOKU) // 1000 * 1000
    shotokuzei = int(kazei_sho * 0.05 * FUKKO)          # 課税所得195万円以下は5%
    kazei_jum = (kyuyo_shotoku - social - KISO_JUMIN) // 1000 * 1000
    juminzei = int(kazei_jum * JUMIN_RITSU) - JUMIN_CHOSEI + JUMIN_KINTO
    tedori = INCOME - social - shotokuzei - juminzei
    kaisha = INCOME + co
    sa = kaisha - tedori

    assert kyuyo_shotoku == 2_760_000, kyuyo_shotoku
    assert social == 587_600, social
    assert round(shotokuzei) == 81_271, shotokuzei
    assert juminzei == 176_700, juminzei          # S015 と同じ計算・同じ額
    assert round(tedori / 10_000) == 315, round(tedori / 10_000)
    assert round(sa / 10_000) == 145, round(sa / 10_000)
    # 会社が出した額のうち、手元に残るのは何割か
    assert round(tedori / kaisha * 100) == 69, round(tedori / kaisha * 100)

    print(f"  給与所得 {kyuyo_shotoku:,}円 / 社会保険料 {social:,}円")
    print(f"  所得税 {shotokuzei:,}円 / 住民税 {juminzei:,}円")
    print(f"  手取り {tedori:,.0f}円(画面は{tedori / 10_000:.0f}万円)")
    print(f"  会社の支出 {kaisha:,.0f}円(画面は{kaisha / 10_000:.0f}万円)")
    print(f"  ★ 差 {sa:,.0f}円(画面は{sa / 10_000:.0f}万円)"
          f" — 会社が出した額の{tedori / kaisha:.0%}しか手元に残らない")

    print("S012 verify: ALL OK")
    print(f"  年収 {INCOME:,}円(東京都・40歳未満・概算)")
    print(f"  本人の負担率 {me_rate:.4%} → {me:,.0f}円(画面は約{me / 10_000:.0f}万円)")
    print(f"    うち厚生年金 9.15% = {kosei_me:,.0f}円(画面は36万6千円)")
    print(f"  会社の負担率 {co_rate:.4%} → {co:,.0f}円(画面は約{co / 10_000:.0f}万円)")
    print(f"  合計 {me + co:,.0f}円(画面は約{(me + co) / 10_000:.0f}万円)")
    print(f"  会社から見た費用 {INCOME:,} + {co:,.0f} = {INCOME + co:,.0f}円"
          f"(画面は約{(INCOME + co) / 10_000:.0f}万円)")


if __name__ == "__main__":
    main()
