#!/usr/bin/env python3
"""S010: 年金額の検証。出典: 厚労省 令和8年度年金額改定/令和5年度事業の概況(plan.md参照)。"""

KOKUMIN_M = 70_608          # 国民年金(老齢基礎)満額 月額・2026年度
MODEL_HUFU = 237_279        # 厚生年金モデル(夫婦2人)月額・2026年度
HOSHU_HIREI = 96_063        # 同モデルの報酬比例部分
HEIKIN_TANSHIN = 147_000    # 厚生年金受給者の平均月額(基礎込み・令和5年度概況の丸め)
HOKENRYO = 17_920           # 国民年金保険料 月額・2026年度(日本年金機構)
MODEL_KAISHAIN = 166_671    # 会社員モデル1人分 = 基礎70,608 + 報酬比例96,063(2026年度モデル)


def main():
    year = KOKUMIN_M * 12
    assert year == 847_296, year                     # 年約85万円
    assert round(year / 10_000) == 85
    assert HOSHU_HIREI + KOKUMIN_M * 2 == MODEL_HUFU  # モデルの内訳整合
    diff = HEIKIN_TANSHIN - KOKUMIN_M
    assert diff == 76_392, diff                       # 差 約7万6千円
    assert round(diff / 1000) == 76
    assert HOKENRYO * 12 == 215_040               # 保険料 年約21.5万円
    assert round(HOKENRYO / 1000) == 18           # 「月1万8千円」表現の根拠
    # 比較は同じ物差し(モデル年金)で揃える(ループ㊴: 満額モデル−実績平均の引き算は不当)
    assert KOKUMIN_M + HOSHU_HIREI == MODEL_KAISHAIN
    assert MODEL_KAISHAIN - KOKUMIN_M == HOSHU_HIREI  # 差=そのまま厚生年金(2階)の分
    print("S010 verify: ALL OK")
    print(f"  国民年金満額: 月{KOKUMIN_M:,}円 = 年{year:,}円")
    print(f"  会社員平均(参考): 月{HEIKIN_TANSHIN:,}円 (差 {diff:,}円)")
    print(f"  夫婦モデル: 月{MODEL_HUFU:,}円")
    print(f"  会社員モデル1人: 月{MODEL_KAISHAIN:,}円(=基礎{KOKUMIN_M:,}+厚生{HOSHU_HIREI:,})")


if __name__ == "__main__":
    main()
