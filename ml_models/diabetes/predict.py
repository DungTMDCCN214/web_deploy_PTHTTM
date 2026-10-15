import json
import os
import sys
import warnings

if hasattr(sys.stdout, 'reconfigure'):
  sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
  sys.stderr.reconfigure(encoding='utf-8')

# Tắt toàn bộ warning của scikit-learn để tránh làm bẩn luồng JSON đầu ra (stdout)
warnings.filterwarnings('ignore')

import joblib
import pandas as pd


# Xác định đường dẫn tương đối đến file .sav
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, 'diabetes_model.sav')


def main():
  # 1. Kiểm tra tham số đầu vào từ Java
  raw_input = sys.argv[1] if len(sys.argv) >= 2 else sys.stdin.read()

  if not raw_input:
    print(
        json.dumps(
            {'error': 'Thiếu dữ liệu đầu vào JSON'}, ensure_ascii=False
        )
    )
    sys.exit(1)

  # 2. Kiểm tra sự tồn tại của file mô hình .sav
  if not os.path.exists(MODEL_PATH):
    print(
        json.dumps(
            {
                'isDiabetic': False,
                'probability': 0.0,
                'riskLevel': 'Chưa nạp model',
                'advice': f'Không tìm thấy file model tại: {MODEL_PATH}',
            },
            ensure_ascii=False,
        )
    )
    sys.exit(0)

  try:
    # 3. Load mô hình đã huấn luyện
    model = joblib.load(MODEL_PATH)

    # 4. Parse dữ liệu JSON truyền sang từ Spring Boot
    input_data = json.loads(raw_input)

    # Khai báo danh sách thuộc tính khớp 100% với tên cột khi train model
    feature_names = [
        'Pregnancies',
        'Glucose',
        'BloodPressure',
        'SkinThickness',
        'Insulin',
        'BMI',
        'DiabetesPedigreeFunction',
        'Age',
    ]

    # Chuyển đổi dữ liệu sang pandas DataFrame để kèm tên cột (Khắc phục UserWarning feature names)
    features_df = pd.DataFrame(
        [[
            float(input_data.get('pregnancies', 0)),
            float(input_data.get('glucose', 0.0)),
            float(input_data.get('bloodPressure', 0.0)),
            float(input_data.get('skinThickness', 0.0)),
            float(input_data.get('insulin', 0.0)),
            float(input_data.get('bmi', 0.0)),
            float(input_data.get('diabetesPedigreeFunction', 0.47)),
            float(input_data.get('age', 0)),
        ]],
        columns=feature_names,
    )

    # 5. Tiến hành dự đoán
    pred = int(model.predict(features_df)[0])

    if hasattr(model, 'predict_proba'):
      prob = float(model.predict_proba(features_df)[0][1])
    else:
      prob = 1.0 if pred == 1 else 0.0

    is_diabetic = bool(pred == 1 or prob >= 0.5)
    risk_level = (
        'Cao' if prob >= 0.6 else ('Trung bình' if prob >= 0.35 else 'Thấp')
    )
    advice = (
        'Nguy cơ tiểu đường cao. Bạn nên đến cơ sở y tế để kiểm tra chỉ số'
        ' HbA1c.'
        if is_diabetic
        else 'Các chỉ số an toàn. Hãy duy trì thói quen sinh hoạt lành mạnh.'
    )

    # 6. Đóng gói kết quả trả về đúng tên thuộc tính khớp với DiabetesResponse.java
    output = {
        'isDiabetic': is_diabetic,
        'probability': round(prob, 4),
        'riskLevel': risk_level,
        'advice': advice,
    }

    # In ra dòng JSON duy nhất
    print(json.dumps(output, ensure_ascii=False))

  except Exception as e:
    # Bắt lỗi ngoại lệ và phản hồi về cho Java hiển thị
    error_output = {
      'isDiabetic': False,
      'probability': 0.0,
      'riskLevel': 'Lỗi thực thi',
      'advice': f'Lỗi trong quá trình dự đoán Python: {str(e)}',
    }
    print(json.dumps(error_output, ensure_ascii=False))


if __name__ == '__main__':
  main()
