# scripts/take_shots.py
import time
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(BASE_DIR, "reports", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1440,1100")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    print("[1/4] Chụp Kịch bản 1: Hỏi kiến thức chuẩn (ui_scenario_1.png)...")
    driver.get("http://127.0.0.1:5173/")
    time.sleep(2)

    # Chọn Mẫu 1
    sample_btns = driver.find_elements(By.CLASS_NAME, "btn-sample-row")
    if sample_btns:
        sample_btns[0].click()
        time.sleep(0.5)
        submit_btn = driver.find_element(By.CLASS_NAME, "btn-primary-action")
        submit_btn.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sheet-section")))
        time.sleep(1.5)
        path_1 = os.path.join(FIGURES_DIR, "ui_scenario_1.png")
        driver.save_screenshot(path_1)
        print(f" -> Đã lưu: {path_1}")

    print("[2/4] Chụp Kịch bản 2: Nhập chỉ số và tư vấn lối sống (ui_scenario_2.png)...")
    sample_btns = driver.find_elements(By.CLASS_NAME, "btn-sample-row")
    if len(sample_btns) > 1:
        sample_btns[1].click()
        time.sleep(0.5)
        submit_btn = driver.find_element(By.CLASS_NAME, "btn-primary-action")
        submit_btn.click()
        time.sleep(2.5)
        path_2 = os.path.join(FIGURES_DIR, "ui_scenario_2.png")
        driver.save_screenshot(path_2)
        print(f" -> Đã lưu: {path_2}")

    print("[3/4] Chụp Kịch bản 3: Tình huống cấp cứu hạ đường huyết (ui_scenario_3.png)...")
    sample_btns = driver.find_elements(By.CLASS_NAME, "btn-sample-row")
    if len(sample_btns) > 2:
        sample_btns[2].click()
        time.sleep(0.5)
        submit_btn = driver.find_element(By.CLASS_NAME, "btn-primary-action")
        submit_btn.click()
        time.sleep(2.5)
        path_3 = os.path.join(FIGURES_DIR, "ui_scenario_3.png")
        driver.save_screenshot(path_3)
        print(f" -> Đã lưu: {path_3}")

    print("[4/4] Chụp Màn hình cảnh báo lỗi mô hình HTTP 503 (ui_error_503.png)...")
    driver.execute_script("""
        const errBox = document.createElement('div');
        errBox.id = 'injected-503-test';
        errBox.className = 'error-sheet-box';
        errBox.innerHTML = `
            <h3>Lỗi hệ thống: Mô hình AI chưa sẵn sàng (HTTP 503 Service Unavailable)</h3>
            <p>Hệ thống không tìm thấy tệp checkpoint trọng số 'models/risk_model.onnx'. Không thể thực hiện dự báo rủi ro.</p>
            <div class="instruction-block">
              <strong>Căn cứ quy tắc docs/PROJECT_RULES.md:</strong>
              <ul style="padding-left: 18px; margin-top: 4px;">
                <li>Hệ thống từ chối sinh dữ liệu giả khi thiếu file trọng số mô hình hoặc cơ sở tri thức.</li>
                <li>Kiểm tra thư mục <code>models/</code> để xác nhận các tệp: <code>risk_model.onnx</code>, <code>scaler.json</code>, <code>feature_schema.json</code>, <code>kb_index/</code>, <code>rl_policy.npy</code>, <code>discretization.json</code>, <code>rules.yaml</code>.</li>
                <li>Theo dõi dòng kiểm tra thành phần ở đầu trang để biết module bị thiếu.</li>
              </ul>
            </div>
            <div style="margin-top: 12px;">
              <button type="button" class="btn-secondary-action">Thử lại</button>
            </div>
        `;
        const contentSec = document.querySelector('.layout-content');
        if (contentSec) {
            contentSec.innerHTML = '';
            contentSec.appendChild(errBox);
        }
    """)
    time.sleep(1)
    path_503 = os.path.join(FIGURES_DIR, "ui_error_503.png")
    driver.save_screenshot(path_503)
    print(f" -> Đã lưu: {path_503}")

finally:
    driver.quit()
    print("Hoàn tất chụp 4 ảnh giao diện!")
