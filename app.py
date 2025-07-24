from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
from werkzeug.utils import secure_filename
from detect_products import detect_and_classify_products
from export_result import export_csv
from face_recognition_util import load_known_faces, recognize_face
from line_notify import notify_member_login  # <== 新增這行

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'static/uploads'
RESULT_IMAGE = 'static/detected_result.jpg'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
        return 0  # 未定義規則

# 載入已知人臉資料
load_known_faces()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/upload_face', methods=['POST'])
def upload_face():
    image_file = request.files['image']
    if image_file.filename == '':
        return redirect(url_for('index'))

    filename = secure_filename("face_" + image_file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image_file.save(filepath)

    # 執行人臉辨識
    person = recognize_face(filepath)
    status = bool(person)
    name = person if person else "未知使用者"

    # ✅ 若辨識成功就發送 Line 通知
    if status:
        notify_member_login(member_name=name, total_spent=session.get("total", 0))

    return render_template('face_result.html', name=name, status=status)
# ✅ 商品辨識路由
@app.route('/upload_product', methods=['POST'])
def upload_product():
    image_file = request.files['image']
    if image_file.filename == '':
        return redirect(url_for('index'))

    filename = secure_filename(image_file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image_file.save(filepath)

    # 商品偵測與分類
    detected_items, result_img_path = detect_and_classify_products(filepath, RESULT_IMAGE)
    total_pay = sum([item.get("折扣後", item.get("小計", 0)) for item in detected_items])

    # 存入 session
    session['items'] = detected_items
    session['total'] = total_pay
    session['image_path'] = result_img_path

    return redirect(url_for('result'))

# ✅ 人臉辨識路由（純辨識，不發送通知）


@app.route('/result')
def result():
    return render_template('result.html',
        image_path=session.get('image_path'),
        items=session.get('items'),
        total=session.get('total')
    )

@app.route('/product')
def product_page():
    return render_template('product_upload.html')

@app.route('/face')
def face_page():
    return render_template('face_upload.html')

@app.route('/export')
def export_csv_file():
    file_path = export_csv(session.get('items'), session.get('total'))
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
