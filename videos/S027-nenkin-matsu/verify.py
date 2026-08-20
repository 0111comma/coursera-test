#!/usr/bin/env python3
"""S027 の数値検証。動画内の数字はすべてここで再計算する。

問い: 年金を1年待って(繰り下げて)もらうと、何歳で追いつくのか。
前提(2026年8月時点・確認日 2026-08-19):
  繰下げは1ヶ月ごとに +0.7%。1年で +8.4%
  例は月16万円(仮定)の人が、65歳を66歳に遅らせた場合
"""
TSUKI = 160_000
UP = 0.007 * 12


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S027 数値検証(月16万円と仮定 / 65歳→66歳)")
    eq("1年の増額率(%の10倍)", round(UP * 1000), 84)
    zou = round(TSUKI * UP)
    eq("月の増え", zou, 13_440)

    # 待った1年でもらい損ねた額
    minoga = TSUKI * 12
    eq("もらい損ねる額", minoga, 1_920_000)

    # 追いつくまでの月数と年齢
    months = minoga / zou
    eq("追いつくまでの月数(切り上げ)", -(-minoga // zou), 143)
    years = months / 12
    print(f"  追いつくまで: {months:.1f}ヶ月 = {years:.1f}年")
    eq("追いつく年齢(66 + 12年)", 66 + round(years), 78)

    # 5年待った場合(70歳開始・+42%)
    zou5 = round(TSUKI * 0.007 * 60)
    eq("5年待ったときの月の増え", zou5, 67_200)
    eq("5年でもらい損ねる額", TSUKI * 60, 9_600_000)
    m5 = -(-TSUKI * 60 // zou5)
    eq("追いつくまでの月数", m5, 143)
    print(f"  70歳開始 → {70 + m5/12:.1f}歳で追いつく(約82歳)")

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
