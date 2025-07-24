def apply_discount(quantity, unit_price, rule):
    if not rule:
        return 0  # 無折扣

    if rule == "buy2_get10percent":
        if quantity >= 2:
            return quantity * unit_price * 0.10  # 每件打 9 折
        return 0

    elif rule == "buy3_get1free":
        free_items = quantity // 4  # 每 4 件送 1
        return free_items * unit_price

    elif rule == "buy1_get5off":
        return quantity * 5  # 每件折 5 元

    else:
        # 其他尚未定義規則
        return 0
