import pandas as pd

PRODUCT_CSV = "products.csv"

# 讀取產品資料（class_name 對應價格）
def load_product_info():
    df = pd.read_csv(PRODUCT_CSV)
    return df

# 查詢單一商品的價格與其他資訊
def get_product_details(class_name):
    df = load_product_info()
    match = df[df['class_name'] == class_name]
    if not match.empty:
        row = match.iloc[0]
        return {
            "class_name": class_name,
            "product_name": row["product_name"],
            "price": float(row["price"]),
            "discount_rule": row.get("discount_rule", None)
        }
    else:
        return {
            "class_name": class_name,
            "product_name": "Unknown",
            "price": 0.0,
            "discount_rule": None
        }

# 批次查詢：傳入 class_name list
def get_all_product_details(class_names):
    result = []
    for name in class_names:
        result.append(get_product_details(name))
    return result
