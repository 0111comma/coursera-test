#!/usr/bin/env python3
"""S017 の数値検証。動画内の数字はすべてここで再計算する。

問い: ふるさと納税をやらないと、年にいくら損しているのか。
前提(2026年8月時点・確認日 2026-08-18):
  年収500万円・独身・給与所得者の控除上限の目安 = 60,000円
  返礼品は寄付額の3割まで(総務省の3割基準)
  自己負担は年2,000円
上限は家族構成や他の控除で変わるので、動画では「目安」と言う。
"""
JOGEN = 60_000
HENREI_RATE = 0.3
JIKO = 2_000


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S017 数値検証(年収500万円・独身の目安)")
    henrei = int(JOGEN * HENREI_RATE)
    eq("上限まで寄付したときの返礼品", henrei, 18_000)
    eq("手元に残る差し引き(年)", henrei - JIKO, 16_000)
    eq("10年ぶん", (henrei - JIKO) * 10, 160_000)

    # 税金そのものは減っていない。減るのは「どこに払うか」だけ
    eq("税から引かれる額", JOGEN - JIKO, 58_000)

    # 月あたりに直すと
    eq("月あたり(円)", (henrei - JIKO) // 12, 1_333)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
