import os
import face_recognition

# 全域人臉資料儲存
known_face_encodings = []
known_face_names = []

def load_known_faces(directory='known_faces'):
    """
    掃描 known_faces 資料夾，讀取每個子資料夾中的圖片並提取人臉編碼
    子資料夾名稱 = 人名
    """
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []

    if not os.path.exists(directory):
        print(f"⚠️ 指定資料夾 {directory} 不存在")
        return

    for person_name in os.listdir(directory):
        person_folder = os.path.join(directory, person_name)
        if not os.path.isdir(person_folder):
            continue

        for filename in os.listdir(person_folder):
            img_path = os.path.join(person_folder, filename)

            try:
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(person_name)
                    print(f"✅ 已載入 {person_name} 的照片：{filename}")
                else:
                    print(f"⚠️ 找不到人臉：{filename}")
            except Exception as e:
                print(f"❌ 讀取錯誤 {img_path}：{e}")

    print(f"🎉 共載入 {len(known_face_encodings)} 張人臉照片")

def recognize_face(image_path):
    """
    輸入一張照片，回傳辨識到的第一個人名（或 None）
    """
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        for encoding in face_encodings:
            results = face_recognition.compare_faces(known_face_encodings, encoding)
            if True in results:
                match_index = results.index(True)
                return known_face_names[match_index]
        return None
    except Exception as e:
        print(f"❌ 辨識錯誤：{e}")
        return None
