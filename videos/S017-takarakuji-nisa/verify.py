#!/usr/bin/env python3
"""S017 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

「宝くじの当せん金には税金がかからないのに、株のもうけには2割かかる」を金額で示し、
その税金がかからない箱としてNISAを出す。

制度の前提:
  - 宝くじの当せん金は、当せん金付証票法 第13条により所得税がかからない。
    所得ではないので住民税もかからない(国内で正規に販売された宝くじの場合)
  - 株式・投資信託の譲渡益と配当には 所得税15.315%(復興特別所得税を含む)
    +住民税5% = 20.315% がかかる
  - NISA口座の中で出たもうけには、この20.315%がかからない
  - NISAに入れられる額は、生涯で1,800万円(簿価残高)、1年で360万円が上限
"""
TAX_RATE = 0.20315       # 株のもうけにかかる税(所得税15.315%+住民税5%)
BIG = 100_000_000        # 例に使うもうけ(1億円)
SMALL = 100_000          # 身近な額の例(10万円)
NISA_LIFETIME = 18_000_000
NISA_YEARLY = 3_600_000


def main():
    lottery_tax = 0                       # 当せん金付証票法 第13条
    stock_tax = int(BIG * TAX_RATE)
    stock_net = BIG - stock_tax
    small_tax = int(SMALL * TAX_RATE)

    assert lottery_tax == 0
    assert stock_tax == 20_315_000, stock_tax
    assert stock_net == 79_685_000, stock_net
    assert stock_tax + stock_net == BIG, "内訳が合計と合っていない"
    # 画面と台本は「およそ2000万円 / およそ8000万円」と丸めて言う。
    # 1000万円の位で丸めても内訳の合計が1億円のままであることを確認する
    assert round(stock_tax, -7) == 20_000_000, stock_tax
    assert round(stock_net, -7) == 80_000_000, stock_net
    assert round(stock_tax, -7) + round(stock_net, -7) == BIG, "丸めた表示の合計がずれている"
    assert abs(stock_tax - 20_000_000) / BIG < 0.005, "「およそ」で済ませてよい誤差か"
    # 身近な額でも同じ率
    assert small_tax == 20_315, small_tax
    assert small_tax == 2 * 10_000 + 315, small_tax      # 画面「2万315円」
    # 「およそ2割」と言ってよいこと
    assert 0.19 <= TAX_RATE <= 0.21
    # NISAの枠
    assert NISA_LIFETIME == 1800 * 10_000 and NISA_YEARLY == 360 * 10_000
    assert NISA_LIFETIME / NISA_YEARLY == 5, "1年の上限で埋めると5年"

    print("S017 verify: ALL OK")
    print(f"  宝くじ {BIG:,}円 → 税金 {lottery_tax}円(当せん金付証票法 第13条)")
    print(f"  株    {BIG:,}円 → 税金 {stock_tax:,}円(画面はおよそ2000万円)")
    print(f"        手元に残るのは {stock_net:,}円(画面はおよそ8000万円)")
    print(f"  身近な額: {SMALL:,}円のもうけ → 税金 {small_tax:,}円(画面は2万315円)")
    print(f"  NISAの上限: 一生 {NISA_LIFETIME:,}円 / 1年 {NISA_YEARLY:,}円")


if __name__ == "__main__":
    main()
