BUY_MAN = 100
SELL_UP_MAN = 120
SELL_DOWN_MAN = 80
REUSE_MAN = BUY_MAN
GAIN_MAN = SELL_UP_MAN - BUY_MAN
LOSS_MAN = BUY_MAN - SELL_DOWN_MAN
assert GAIN_MAN == LOSS_MAN == 20
assert REUSE_MAN == 100

if __name__ == "__main__":
    print({k:v for k,v in globals().copy().items() if k.isupper()})
