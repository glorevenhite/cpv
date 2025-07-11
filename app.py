# app.py
import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# --- KHỞI TẠO ỨNG DỤNG FLASK VÀ FIREBASE ---

# Khởi tạo Flask
app = Flask(__name__)
# Cho phép Cross-Origin Resource Sharing (CORS) để frontend có thể gọi API này
CORS(app)

# Đường dẫn tới file service account key
SERVICE_ACCOUNT_KEY_PATH = "service-account-key.json"

# Khởi tạo kết nối tới Firebase
# Lệnh này chỉ nên được chạy một lần
cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
firebase_admin.initialize_app(cred)

# Lấy một đối tượng client của Firestore để tương tác với database
db = firestore.client()

# --- ĐỊNH NGHĨA API ENDPOINT ---

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint nhận file CSV, đọc dữ liệu và lưu vào Firestore.
    Mỗi dòng trong CSV sẽ là một document trong collection 'stock_data'.
    """
    # 1. Kiểm tra xem request có chứa file không
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # 2. Kiểm tra xem người dùng có chọn file không
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 3. Đọc và xử lý file CSV bằng Pandas
    if file:
        try:
            # Đọc file CSV trực tiếp từ đối tượng file mà không cần lưu tạm
            df = pd.read_csv(file)
            
            # Lấy tên collection trong Firestore
            collection_name = 'stock_data'
            
            # Bắt đầu một "batch" để gửi nhiều lệnh ghi cùng lúc, giúp tăng hiệu suất
            batch = db.batch()

            # 4. Lặp qua từng dòng trong DataFrame
            for index, row in df.iterrows():
                # Chuyển đổi dòng thành một dictionary
                data = row.to_dict()
                
                # Lấy Ticker làm ID cho document để tránh trùng lặp
                # Nếu không có cột 'Ticker', bạn có thể để Firestore tự tạo ID
                doc_id = row['Ticker']
                
                # Tạo một tham chiếu tới document mới trong collection 'stock_data'
                doc_ref = db.collection(collection_name).document(doc_id)
                
                # Thêm lệnh ghi vào batch
                batch.set(doc_ref, data)
                
            # 5. Gửi toàn bộ batch lên Firestore
            batch.commit()

            # 6. Trả về thông báo thành công
            return jsonify({
                "message": f"Successfully uploaded and saved {len(df)} records to Firestore in collection '{collection_name}'."
            }), 200

        except Exception as e:
            # Trả về lỗi nếu có vấn đề xảy ra
            return jsonify({"error": f"An error occurred: {e}"}), 500

# Chạy server khi file này được thực thi
if __name__ == '__main__':
    # Chạy ở chế độ debug để tự động khởi động lại khi có thay đổi code
    app.run(debug=True, port=5000)