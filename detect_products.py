import os
import cv2
import numpy as np
import pandas as pd
import h5py
from ultralytics import YOLO
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
from discount_util import apply_discount  # 確保有這個檔案

# === 參數設定 ===
YOLO_MODEL_PATH = "yolov8n.pt"
CLASSIFIER_PATH = "models/iou_resnet50_csv_06.h5"
CLASS_CSV_PATH = "classes.csv"
OUTPUT_CSV = "detected_products.csv"
IMAGE_SIZE = (224, 224)

# === 載入 YOLO 模型 ===
print("🔍 載入 YOLO 模型...")
yolo_model = YOLO(YOLO_MODEL_PATH)

# === 建構分類模型架構（ResNet50） ===
def build_classifier_model(num_classes=110):
    base_model = ResNet50(weights=None, include_top=False, input_tensor=Input(shape=(224, 224, 3)))
    x = GlobalAveragePooling2D()(base_model.output)
    x = Dense(256, activation='relu')(x)
    output = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=output)
    return model

# === 讀取 classes.csv 並建立 sku_map（類別對應表）===
sku_map = {}
num_classes = 110  # 預設類別數
if os.path.exists(CLASS_CSV_PATH):
    df = pd.read_csv(CLASS_CSV_PATH, header=0)
    for _, row in df.iterrows():
        sku_map[int(row[0])] = {"name": row[1], "price": int(row[2])}
    num_classes = len(sku_map)
else:
    print("⚠️ 找不到 classes.csv，將使用預設類別編號")

# === 建立模型並載入 h5py 權重 ===
print("🔧 建構 ResNet50 架構...")
classifier = build_classifier_model(num_classes)

print("🔄 使用 h5py 載入權重中...")
with h5py.File(CLASSIFIER_PATH, "r") as f:
    weights_group = f["model_weights"]
    loaded = 0
    for layer in classifier.layers:
        if layer.name in weights_group:
            try:
                weights = [weights_group[layer.name][w][:] for w in weights_group[layer.name]]
                layer.set_weights(weights)
                loaded += 1
            except Exception as e:
                print(f"⚠️ 無法載入層 {layer.name}: {e}")
print(f"✅ 成功套用 {loaded} 層權重")

# === 商品偵測與分類主流程 ===
def detect_and_classify_products(image_path, result_img_output_path="static/detected_result.jpg"):
    print(f"📸 處理圖片: {image_path}")
    img = cv2.imread(image_path)
    results = yolo_model(img)[0]
    temp_products = []

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cropped = img[y1:y2, x1:x2]

        if cropped.size == 0:
            continue

        cropped = cv2.resize(cropped, IMAGE_SIZE)
        image_array = img_to_array(cropped)
        image_array = preprocess_input(image_array)
        image_array = np.expand_dims(image_array, axis=0)

        pred = classifier.predict(image_array)[0]
        class_id = int(np.argmax(pred))
        product_info = sku_map.get(class_id)

        if product_info:
            class_name = product_info["name"]
            price = int(product_info["price"])
        else:
            class_name = f"未知類別_{class_id}"
            price = 0
            print(f"⚠️ 未知類別：{class_id} 不在 classes.csv 中")

        temp_products.append({
            "商品": class_name,
            "單價": price
        })

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imwrite(result_img_output_path, img)

    # 整理數量與折扣
    summary = {}
    for item in temp_products:
        key = item["商品"]
        if key not in summary:
            summary[key] = {
                "商品": key,
                "單價": item["單價"],
                "數量": 1
            }
        else:
            summary[key]["數量"] += 1

    discount_rules = {
        "洋芋片": "buy3_get1free",
        "泡麵": "buy2_get10percent",
        "可口可樂": "buy1_get5off"
    }

    detected_products = []
    for item in summary.values():
        name = item["商品"]
        qty = item["數量"]
        unit = item["單價"]
        subtotal = qty * unit
        rule = discount_rules.get(name, None)
        discount = apply_discount(qty, unit, rule)
        final_price = subtotal - discount

        detected_products.append({
            "商品": name,
            "單價": unit,
            "數量": qty,
            "小計": subtotal,
            "折扣": discount,
            "折扣後": final_price,
            "折扣規則": rule or "無"
        })

    if detected_products:
        pd.DataFrame(detected_products).to_csv(OUTPUT_CSV, index=False)
        print(f"✅ 偵測完成，結果儲存在 {OUTPUT_CSV}")
    else:
        print("⚠️ 沒有偵測到商品")

    return detected_products, result_img_output_path
