LOSS_MAN = 20
PROFIT_MAN = 20
NET_MAN = PROFIT_MAN - LOSS_MAN
TAXABLE_MAN = PROFIT_MAN
assert NET_MAN == 0 and TAXABLE_MAN == 20

if __name__ == "__main__":
    print({k:v for k,v in globals().copy().items() if k.isupper()})
