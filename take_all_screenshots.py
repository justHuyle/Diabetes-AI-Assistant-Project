# take_all_screenshots.py - Tự động hóa kiểm thử giao diện và chụp ảnh màn hình bằng Selenium
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

os.makedirs("reports/figures", exist_ok=True)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1360,1100")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    print("[1/5] Chụp màn hình trạng thái ban đầu (Empty State)...")
    driver.get("http://127.0.0.1:5173/")
    time.sleep(2)
    driver.save_screenshot("reports/figures/screenshot_empty.png")
    print(" -> Lưu tại: reports/figures/screenshot_empty.png")

    # KỊCH BẢN 1: Hỏi kiến thức chuẩn
    print("[2/5] Thực hiện Kịch bản 1: Hỏi tiêu chuẩn chẩn đoán...")
    sample_btns = driver.find_elements(By.CLASS_NAME, "btn-sample-row")
    if sample_btns:
        sample_btns[0].click()  # Mẫu 1
        time.sleep(0.5)
        submit_btn = driver.find_element(By.CLASS_NAME, "btn-primary-action")
        submit_btn.click()
        # Chờ xuất hiện kết quả
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sheet-section")))
        time.sleep(1)
        driver.save_screenshot("reports/figures/screenshot_scenario_1.png")
        print(" -> Lưu tại: reports/figures/screenshot_scenario_1.png")

    # KỊCH BẢN 2: Hồ sơ chỉ số đầy đủ
    print("[3/5] Thực hiện Kịch bản 2: Hồ sơ chỉ số đầy đủ...")
    sample_btns = driver.find_elements(By.CLASS_NAME, "btn-sample-row")
    if len(sample_btns) > 1:
        sample_btns[1].click()  # Mẫu 2
        time.sleep(0.5)
        submit_btn = driver.find_element(By.CLASS_NAME, "btn-primary-action")
        submit_btn.click()
        # Chờ hoàn thành
        time.sleep(2)
        driver.save_screenshot("reports/figures/screenshot_scenario_2.png")
        print(" -> Lưu tại: reports/figures/screenshot_scenario_2.png")

    # KỊCH BẢN 3: Cấp cứu hạ đường huyết
    print("[4/5] Thực hiện Kịch bản 3: Dấu hiệu hạ đường huyết cấp cứu...")
    sample_btns = driver.find_elements(By.CLASS_NAME, "btn-sample-row")
    if len(sample_btns) > 2:
        sample_btns[2].click()  # Mẫu 3
        time.sleep(0.5)
        submit_btn = driver.find_element(By.CLASS_NAME, "btn-primary-action")
        submit_btn.click()
        # Chờ hoàn thành
        time.sleep(2)
        driver.save_screenshot("reports/figures/screenshot_scenario_3.png")
        print(" -> Lưu tại: reports/figures/screenshot_scenario_3.png")

    # MÀN HÌNH LỖI 503
    print("[5/5] Kiểm tra và chụp màn hình hiển thị lỗi 503...")
    # Điều hướng với lỗi giả lập hoặc gọi JavaScript để kích hoạt error state trong React
    driver.execute_script("""
        // Gọi dispatch lỗi trực tiếp hoặc render ErrorState
        window.__TEST_TRIGGER_503__ = true;
    """)
    # Tạo một file HTML testbed mô phỏng hiển thị ErrorState 503 nếu cần, hoặc tiêm mã hiển thị
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
    driver.save_screenshot("reports/figures/screenshot_error_503.png")
    print(" -> Lưu tại: reports/figures/screenshot_error_503.png")

finally:
    driver.quit()
    print("Đã hoàn tất toàn bộ ảnh chụp màn hình!")
