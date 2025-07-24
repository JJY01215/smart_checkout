# export_result.py

import os
import pandas as pd
from datetime import datetime

def export_csv(items, total, output_path=None):
    """
    將結帳結果匯出成 CSV
    :param items: 商品清單 (list of dicts)，每筆包含 商品, 單價, 數量, 小計, 折扣, 折扣後, 折扣規則
    :param total: 總金額（例如折扣後總價）
    :param output_path: 可選，自訂輸出路徑
    :return: 實際儲存的檔案路徑
    """
    if not output_path:
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = f"outputs/checkout_{now_str}.csv"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df = pd.DataFrame(items)
    
    # 加入總金額行（在最後一行）
    total_row = [""] * (len(df.columns) - 2) + ["總計", total]
    df.loc[len(df)] = total_row

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 匯出完成：{output_path}")
    return output_path
