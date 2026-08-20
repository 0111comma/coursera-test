#!/usr/bin/env python3
"""S031 の数値検証。動画内の数字はすべてここで再計算する。

問い: 1年の医療費が20万円かかったら、いくら戻るのか。
前提(2026年8月時点・確認日 2026-08-19):
  医療費控除 = 払った医療費 − 保険金など − 10万円
  (総所得200万円未満の人は10万円ではなく所得の5%)
  戻るのは 控除額 × 所得税率(この例では10.21%)。住民税も 控除額 × 10% 減る
  家族のぶんも、通院の交通費も合算できる
"""
IRYOHI = 200_000
SHIKII = 100_000
SHOTOKU = 0.1021
JUMIN = 0.10


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S031 数値検証(医療費20万円 / 所得税率10%の人)")
    kojo = IRYOHI - SHIKII
    eq("控除される額", kojo, 100_000)

    modoru = round(kojo * SHOTOKU)
    eq("所得税の戻り", modoru, 10_210)
    heru = round(kojo * JUMIN)
    eq("翌年の住民税の減り", heru, 10_000)
    eq("合計", modoru + heru, 20_210)

    # 30万円かかった場合
    kojo30 = 300_000 - SHIKII
    eq("30万円のときの合計", round(kojo30 * SHOTOKU) + round(kojo30 * JUMIN), 40_420)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
