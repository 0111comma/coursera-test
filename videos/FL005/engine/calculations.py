from decimal import Decimal as D
def calculate(theme):
    if theme=='fx':
        principal=D('1000000');rate=D('150');interest=D('1.05');exit_rate=D('135')
        final=principal/rate*interest*exit_rate
        assert final==D('945000')
        return {'hypothetical':True,'initial_jpy':1000000,'annual_interest_rate':.05,'years':1,'initial_usd_jpy':150,'final_usd_jpy':135,'final_usd':7000,'final_jpy':945000,'jpy_loss':55000,'tax_and_fx_fees_excluded':True}
    tax=D('200000')*D('0.20315');net=D('200000')-tax
    assert tax==40630 and net==159370
    return {'hypothetical':True,'dividend_jpy':200000,'withholding_rate':.20315,'withholding_jpy':40630,'net_jpy':159370,'scope':'NISA国内上場株式の配当・大口株主等を除く・銀行口座への直接受取','tax_free_method':'株式数比例配分方式'}
