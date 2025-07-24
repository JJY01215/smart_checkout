import pandas as pd
from collections import defaultdict
from discount_rules import apply_discount

OUTPUT_CSV = "checkout_result.csv"

def generate_summary(product_list):
    summary = defaultdict(lambda: {
        "product_name": "",
        "unit_price": 0,
        "quantity": 0,
        "subtotal": 0,
        "discount_rule": None
    })

    # 統計每樣商品
    for item in summary["items"]:
        row = [
            item["商品"],
            item["數量"],
            item["單價"],
            item.get("單位", ""),
            item["小計"],
            item.get("折扣規則", "")
            ]
    writer.writerow(row)

    # 計算小計與折扣
    rows = []
    total = 0
    total_discount = 0

    for class_name, info in summary.items():
        qty = info["quantity"]
        unit_price = info["unit_price"]
        discount_rule = info["discount_rule"]

        subtotal = qty * unit_price
        discount = apply_discount(qty, unit_price, discount_rule)

        total += subtotal
        total_discount += discount

        rows.append({
            "商品": info["product_name"],
            "單價": unit_price,
            "數量": qty,
            "小計": subtotal,
            "折扣": discount,
            "折扣後": subtotal - discount,
            "折扣規則": discount_rule or "無"
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"✅ 結帳資訊已匯出到 {OUTPUT_CSV}")

    return {
        "items": rows,
        "total": total,
        "total_discount": total_discount,
        "total_pay": total - total_discount
    }
