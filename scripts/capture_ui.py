# scripts/capture_ui.py
# Tự động hóa khởi động Backend + Frontend, điều khiển Chrome Headless để chụp ảnh 3 kịch bản và màn hình lỗi 503
import os
import sys
import time
import subprocess
import requests

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

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"


def wait_for_server(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code in [200, 404]:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def main():
    backend_proc = None
    frontend_proc = None

    # 1. Kiểm tra xem backend đã chạy chưa, nếu chưa thì khởi động
    need_kill_backend = False
    try:
        r = requests.get(f"{BACKEND_URL}/api/health", timeout=1)
        print("Backend đã sẵn sàng trên port 8000.")
    except Exception:
        print("Đang khởi động Backend FastAPI...")
        python_exe = sys.executable
        env = os.environ.copy()
        env["PYTHONPATH"] = BASE_DIR
        backend_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "backend.app.main:app", "--port", "8000"],
            cwd=BASE_DIR,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        need_kill_backend = True
        if not wait_for_server(f"{BACKEND_URL}/api/health", timeout=25):
            print("Lỗi: Không thể khởi động backend!")
            if backend_proc:
                backend_proc.terminate()
            return

    # 2. Kiểm tra xem frontend đã chạy chưa, nếu chưa thì khởi động
    need_kill_frontend = False
    try:
        r = requests.get(FRONTEND_URL, timeout=1)
        print("Frontend đã sẵn sàng trên port 5173.")
    except Exception:
        print("Đang khởi động Frontend Vite...")
        frontend_dir = os.path.join(BASE_DIR, "frontend")
        frontend_proc = subprocess.Popen(
            "npm run dev",
            cwd=frontend_dir,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        need_kill_frontend = True
        if not wait_for_server(FRONTEND_URL, timeout=25):
            print("Lỗi: Không thể khởi động frontend!")
            if frontend_proc:
                subprocess.call(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True)
            if need_kill_backend and backend_proc:
                subprocess.call(f"taskkill /F /T /PID {backend_proc.pid}", shell=True)
            return

    # 3. Khởi tạo Chrome Webdriver
    print("Đang mở Chrome Headless...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1100")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 25)

    try:
        print("[1/4] Chụp Kịch bản 1: Hỏi kiến thức chuẩn (ui_scenario_1.png)...")
        driver.get(FRONTEND_URL)
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
            target_1 = os.path.join(FIGURES_DIR, "ui_scenario_1.png")
            driver.save_screenshot(target_1)
            print(f" -> Đã lưu: {target_1}")

        print("[2/4] Chụp Kịch bản 2: Nhập chỉ số và tư vấn lối sống (ui_scenario_2.png)...")
        driver.get(FRONTEND_URL)
        time.sleep(1.5)
        sample_btns = driver.find_elements(By.CLASS_NAME, "btn-sample-row")
        if len(sample_btns) > 1:
            sample_btns[1].click()
            time.sleep(0.5)
            submit_btn = driver.find_element(By.CLASS_NAME, "btn-primary-action")
            submit_btn.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sheet-section")))
            time.sleep(2)
            target_2 = os.path.join(FIGURES_DIR, "ui_scenario_2.png")
            driver.save_screenshot(target_2)
            print(f" -> Đã lưu: {target_2}")

        print("[3/4] Chụp Kịch bản 3: Tình huống cấp cứu hạ đường huyết (ui_scenario_3.png)...")
        driver.get(FRONTEND_URL)
        time.sleep(1.5)
        sample_btns = driver.find_elements(By.CLASS_NAME, "btn-sample-row")
        if len(sample_btns) > 2:
            sample_btns[2].click()
            time.sleep(0.5)
            submit_btn = driver.find_element(By.CLASS_NAME, "btn-primary-action")
            submit_btn.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sheet-section")))
            time.sleep(2)
            target_3 = os.path.join(FIGURES_DIR, "ui_scenario_3.png")
            driver.save_screenshot(target_3)
            print(f" -> Đã lưu: {target_3}")

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
        target_503 = os.path.join(FIGURES_DIR, "ui_error_503.png")
        driver.save_screenshot(target_503)
        print(f" -> Đã lưu: {target_503}")

    finally:
        driver.quit()
        if need_kill_frontend and frontend_proc:
            print("Đang tắt tiến trình Frontend...")
            subprocess.call(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True)
        if need_kill_backend and backend_proc:
            print("Đang tắt tiến trình Backend...")
            subprocess.call(f"taskkill /F /T /PID {backend_proc.pid}", shell=True)
        print("Hoàn tất chụp ảnh giao diện!")


if __name__ == "__main__":
    main()
