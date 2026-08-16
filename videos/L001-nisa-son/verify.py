#!/usr/bin/env python3
"""L001 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

この動画が答える問い:
  **NISAで損したら、課税口座で損したときより不利になるのか。いくら不利なのか。**

答え(自前計算):
  不利になる額 = min(NISAの損, 課税口座の利益) × 20.315%
  これが「損益通算できないこと」の値段である。

前提: 2026年8月時点の制度。税率は上場株式等の譲渡益に対するもの。
      申告分離課税を選んだ場合。復興特別所得税は2037年分まで。
"""

# 税率(上場株式等の譲渡益)
SHOTOKU = 0.15          # 所得税
FUKKO = 0.15 * 0.021    # 復興特別所得税(所得税額の2.1%)
JUMIN = 0.05            # 住民税
ZEI = SHOTOKU + FUKKO + JUMIN


def zei(gain):
    """譲渡益にかかる税(円未満切り捨て)。"""
    return int(gain * ZEI)


def son_no_nedan(nisa_loss, kazei_gain):
    """NISAで損したことによって余分に払う税。

    課税口座どうしなら (利益 − 損失) にしか課税されない(損益通算)。
    NISAの損は「無かったもの」とされるので、課税口座の利益にまるごと課税される。
    差は、相殺できたはずの額 = 小さいほう に税率を掛けたもの。
    """
    zenbu_kazei = zei(max(0, kazei_gain - nisa_loss))
    genjitsu = zei(kazei_gain)
    return genjitsu - zenbu_kazei


def main():
    ok = []

    # 税率の内訳
    assert abs(ZEI - 0.20315) < 1e-9, ZEI
    ok.append(f"税率 {SHOTOKU:.0%} + {FUKKO * 100:.3f}% + {JUMIN:.0%} = {ZEI:.5%}")

    # --- 冒頭 & 章2: 同じ年に、NISAで20万円の損、課税口座で20万円の利益 ---
    L, G = 200_000, 200_000
    zenbu = zei(max(0, G - L))
    genjitsu = zei(G)
    sa = son_no_nedan(L, G)
    assert zenbu == 0, zenbu
    assert genjitsu == 40_630, genjitsu
    assert sa == 40_630, sa
    ok.append(f"NISAで{L:,}円の損 + 課税口座で{G:,}円の利益"
              f" → 全部課税口座なら {zenbu:,}円 / 実際は {genjitsu:,}円 / 差 {sa:,}円")

    # --- 章1: 損益通算そのものの説明用(課税口座どうし) ---
    assert zei(200_000) == 40_630
    assert zei(500_000) == 101_575
    ok.append(f"参考 利益20万円の税 {zei(200_000):,}円 / 利益50万円の税 {zei(500_000):,}円")

    # --- 章3: 繰越控除(2年またぎ) ---
    # 1年目に40万円の損、2年目に40万円の利益。
    # 課税口座なら1年目の損を繰り越して2年目の利益と相殺できる(要・確定申告)。
    L1, G2 = 400_000, 400_000
    kurikoshi_ari = zei(max(0, G2 - L1))
    kurikoshi_nashi = zei(G2)
    assert kurikoshi_ari == 0
    assert kurikoshi_nashi == 81_260, kurikoshi_nashi
    ok.append(f"1年目に{L1:,}円の損、2年目に{G2:,}円の利益"
              f" → 繰越控除できれば {kurikoshi_ari:,}円 / できなければ {kurikoshi_nashi:,}円")

    # --- 章4: 逆に、NISAで得をする額(利益が出た場合) ---
    # 同じ20万円でも、損ではなく利益なら、NISAは20.315%を丸ごと免れる。
    P = 200_000
    assert zei(P) == 40_630
    ok.append(f"NISAで{P:,}円の利益が出た場合、免れる税 {zei(P):,}円(損の場合と同額)")

    # --- 章4: 損の額と課税口座の利益がずれている場合 ---
    # 相殺できるのは小さいほうまで。ここが「min」であることを画面で見せる。
    for L_, G_, expect in [(300_000, 100_000, 20_315),
                           (100_000, 300_000, 20_315),
                           (300_000, 0, 0),
                           (0, 300_000, 0)]:
        got = son_no_nedan(L_, G_)
        assert got == expect, (L_, G_, got, expect)
    ok.append("相殺できるのは小さいほうまで: 損30万+利益10万 → 差20,315円 /"
              " 損10万+利益30万 → 差20,315円 / 片方が0なら差0円")

    # --- 章4: 課税口座の利益が無い人は、不利にならない ---
    assert son_no_nedan(1_000_000, 0) == 0
    ok.append("課税口座に利益が無い年は、NISAでいくら損しても差は0円")

    # --- 締め: 3つの場合の一覧表 ---
    hyo = [
        ("NISAで利益20万円", -zei(200_000)),      # マイナス = 得
        ("NISAで損20万円・課税口座の利益なし", 0),
        ("NISAで損20万円・課税口座で利益20万円", son_no_nedan(200_000, 200_000)),
    ]
    assert [v for _, v in hyo] == [-40_630, 0, 40_630]
    ok.append("一覧表: 得40,630円 / 差0円 / 損40,630円")

    # --- 枠の復活(金額そのものではなく仕組みの確認) ---
    # 100万円で買って80万円で売っても、翌年に戻る枠は「買った値段」の100万円。
    KAI, URI = 1_000_000, 800_000
    modoru = KAI            # 簿価(取得価額)ぶんが戻る
    assert modoru == 1_000_000
    assert KAI - URI == 200_000
    ok.append(f"{KAI:,}円で買って{URI:,}円で売る → 翌年に戻る枠は簿価の{modoru:,}円")

    for line in ok:
        print("  " + line)
    print("L001 verify: ALL OK")


if __name__ == "__main__":
    main()
