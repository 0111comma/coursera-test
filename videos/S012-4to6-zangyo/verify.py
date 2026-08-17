#!/usr/bin/env python3
"""S012 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

この動画が答える問い:
  **4月から6月に残業すると、手取りはいくら減るのか。それは取り返せるのか。**

なぜこの企画にしたか(ループ67):
  前の S012(社会保険料は会社も同じ額を払っている / 会社の460万円のうち手取りは315万円)は
  2回作り直したが、どちらもユーザー判定は「面白くない」だった。
  診断は**視聴者の身に何も起きないこと**。会社の財布がいくらでも、見た人は何もしない。
  同じ社会保険料でも「**4〜6月の残業で、自分の手取りが減る**」なら身に起きる。
  しかも残業を寄せるかどうかという**決められること**がある。

前提: 2026年度の料率。東京都・40歳未満(介護保険料なし)。
      標準報酬月額は等級表で決まるため、ここでは等級表に実在する
      34万円 → 38万円 の変化を例にとる。
      定時決定は4月・5月・6月に支払われた報酬の平均で決まり、
      その年の9月から翌年8月までの1年間に適用される。
"""
# 2026年度の料率(本人負担)
KOSEI = 0.183 / 2         # 厚生年金 9.15%
KENKO = 0.0985 / 2        # 健康保険 協会けんぽ東京都 4.925%
KODOMO = 0.0023 / 2       # 子ども・子育て支援金 0.115%

HOSHU_LOW = 340_000       # ふだんの標準報酬月額
HOSHU_HIGH = 380_000      # 4〜6月に残業したときの標準報酬月額
MONTHS = 12               # 定時決定が効く期間(9月から翌年8月)

# 厚生年金の報酬比例部分の乗率(平成15年4月以降・総報酬制)
NENKIN_RATE = 5.481 / 1000
JUKYU_AGE = 65
HEIKIN_JUMYO_M = 81       # 男性の平均寿命(S011と同じ値を使う)


def main():
    ok = []
    sa = HOSHU_HIGH - HOSHU_LOW
    assert sa == 40_000

    # --- 引かれる額がいくら増えるか(1ヶ月) ---
    kosei_m = sa * KOSEI
    kenko_m = sa * KENKO
    kodomo_m = sa * KODOMO
    tsuki = kosei_m + kenko_m + kodomo_m
    assert round(kosei_m) == 3_660, round(kosei_m)
    assert round(kenko_m) == 1_970, round(kenko_m)
    assert round(kodomo_m) == 46, round(kodomo_m)
    assert round(tsuki) == 5_676, round(tsuki)
    ok.append(f"標準報酬月額が{HOSHU_LOW:,}円→{HOSHU_HIGH:,}円({sa:,}円)上がると、"
              f"毎月 厚生年金{kosei_m:,.0f}円 + 健康保険{kenko_m:,.0f}円 + 支援金{kodomo_m:,.0f}円"
              f" = {tsuki:,.0f}円ふえる")

    # --- 1年ぶん ---
    nenkan = tsuki * MONTHS
    assert round(nenkan) == 68_112, round(nenkan)
    ok.append(f"9月から翌年8月までの{MONTHS}ヶ月で {nenkan:,.0f}円")

    # --- 見返り: 将来の厚生年金がいくら増えるか ---
    # 報酬比例部分 = 平均標準報酬額 × 5.481/1000 × 加入月数
    # 12ヶ月ぶん標準報酬月額が4万円高い、という差だけを見る
    nenkin_zou = sa * NENKIN_RATE * MONTHS
    assert round(nenkin_zou) == 2_631, round(nenkin_zou)
    ok.append(f"見返りに、65歳からの厚生年金が 年{nenkin_zou:,.0f}円ふえる(終身)")

    # --- 何年で取り返せるか ---
    # (a) 引かれた全部を分母にした場合
    nenkazu_all = nenkan / nenkin_zou
    age_all = JUKYU_AGE + nenkazu_all
    assert round(nenkazu_all) == 26, round(nenkazu_all, 2)
    assert round(age_all) == 91, round(age_all, 1)
    ok.append(f"引かれた{nenkan:,.0f}円を年金で取り返すには {nenkazu_all:.1f}年"
              f" → {JUKYU_AGE}歳 + {nenkazu_all:.0f}年 = 約{age_all:.0f}歳")

    # (b) 年金の保険料ぶんだけを分母にした場合(健康保険料は年金には反映されない)
    kosei_nen = kosei_m * MONTHS
    nenkazu_kosei = kosei_nen / nenkin_zou
    age_kosei = JUKYU_AGE + nenkazu_kosei
    assert round(kosei_nen) == 43_920, round(kosei_nen)
    assert round(nenkazu_kosei) == 17, round(nenkazu_kosei, 2)
    assert round(age_kosei) == 82, round(age_kosei, 1)
    ok.append(f"厚生年金の保険料{kosei_nen:,.0f}円ぶんだけで見ても {nenkazu_kosei:.1f}年"
              f" → 約{age_kosei:.0f}歳")

    # --- 判定: 平均寿命では取り返せるか ---
    assert age_all > HEIKIN_JUMYO_M, "全部を分母にすると平均寿命を超える"
    assert age_kosei > HEIKIN_JUMYO_M, "年金ぶんだけでも平均寿命を超える"
    todoku = (HEIKIN_JUMYO_M - JUKYU_AGE) * nenkin_zou
    assert round(todoku) == 42_094, round(todoku)
    ok.append(f"{HEIKIN_JUMYO_M}歳まで受け取っても {todoku:,.0f}円で、"
              f"引かれた{nenkan:,.0f}円には届かない")

    print("\n".join("  " + line for line in ok))
    print("S012 verify: ALL OK")


if __name__ == "__main__":
    main()
