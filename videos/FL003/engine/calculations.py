def calculate(theme='shipping'):
    item=4000;shipping=500;extra=1000;threshold=5000
    original=item+shipping;added=item+extra
    assert added>=threshold
    assert (original,added,added-original)==(4500,5000,500)
    return dict(hypothetical=True,tax_inclusive=True,item_yen=item,shipping_yen=shipping,unneeded_extra_yen=extra,free_shipping_threshold_yen=threshold,without_extra_yen=original,with_extra_yen=added,additional_spending_yen=added-original)
