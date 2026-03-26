import undetected_chromedriver as uc # Dùng thư viện tàng hình
from selenium.webdriver.common.by import By
import pandas as pd
import time
import random

# 1. Khởi tạo trình duyệt tàng hình (Bỏ qua Cloudflare)
options = uc.ChromeOptions()
# options.add_argument('--headless') # Đừng dùng headless lúc này vì cần Duy click tay

driver = uc.Chrome(options=options)

all_jobs = []
base_url = "https://itviec.com/it-jobs/ha-noi"

try:
    # --- BƯỚC QUAN TRỌNG: VƯỢT CLOUDFLARE & ĐĂNG NHẬP ---
    print("🚀 Đang mở ITViệc... làm 2 việc sau:")
    print("1. Nếu hiện Cloudflare 'Verify you are human', hãy LẤY CHUỘT NHẤN VÀO Ô VUÔNG.")
    print("2. Đăng nhập vào ITViệc để thấy được lương.")
    
    driver.get("https://itviec.com/sign_in")
    
    # Cho Duy 60 giây để vừa giải Captcha vừa đăng nhập
    time.sleep(60) 
    print("✅ Hết thời gian chờ! Code sẽ bắt đầu cào...")

    for page in range(1, 23): 
        url = f"{base_url}?page={page}"
        print(f"--- Đang cào trang {page}/40 ---")
        driver.get(url)
        
        # Nghỉ ngẫu nhiên lâu hơn một chút để Cloudflare không nghi ngờ
        time.sleep(random.uniform(5, 8))

        # Tìm các card công việc bằng Selector chuẩn của ITViệc
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-search--pagination-target='jobCard']")
        
        if not job_cards:
            print(f"⚠️ Không tìm thấy job ở trang {page}, có thể bị chặn hoặc hết trang.")
            break

        for card in job_cards:
            try:
                # 1. Lấy Tiêu đề (Sử dụng class định danh chính xác của ITViệc)
                title_el = card.find_element(By.CSS_SELECTOR, "h3.title a, [data-search--job-selection-target='jobTitle']")
                title = title_el.text.strip()
        
                # 2. Lấy Tên công ty 
                # ITViệc thường để tên công ty trong thẻ span hoặc div ngay dưới tiêu đề
                try:
                    company_el = card.find_element(By.CSS_SELECTOR, ".company-name, .logo-wrapper + div, .company-info span")
                    company = company_el.text.strip()
                except:
                    company = "N/A"

                # 3. LẤY LƯƠNG (Phần này bạn hay bị lỗi nhất)
                # Cách tốt nhất là tìm icon "đô la" hoặc văn bản đặc trưng trong các thẻ div/span
                try:
                    # Tìm thẻ chứa chữ "đăng nhập để xem mức lương" hoặc "love" hoặc có số tiền
                    salary_el = card.find_element(By.XPATH, ".//*[contains(text(), '$') or contains(text(), 'VNĐ') or contains(text(), 'love') or contains(text(), 'Sign in')]")
                    salary_raw = salary_el.text.strip()
            
                    # Chuẩn hóa văn bản lương theo ý bạn (Đổi thành "Thỏa thuận")
                    if "love" in salary_raw.lower() or "sign in" in salary_raw.lower() or "negotiable" in salary_raw.lower():
                        salary = "Thỏa thuận"
                    else:
                        salary = salary_raw
                except:
                    salary = "Thỏa thuận"

                # 4. Lấy Kỹ năng (Thường nằm trong các thẻ a có class 'tag-list')
                try:
                    tags_els = card.find_elements(By.CSS_SELECTOR, ".tag-list a, .itviec-tag, .tags .tag")
                    tags = [t.text.strip() for t in tags_els if t.text.strip()]
                except:
                    tags = []

                if title:
                    all_jobs.append({
                        "Job Title": title,
                        "Company": company,
                        "Salary": salary,
                        "Skills": ", ".join(tags),
                        "Location": "Ho Chi Minh"
                    })
            
            except Exception as e:
                # In ra lỗi để debug nếu cần, sau đó bỏ qua để chạy tiếp
                # print(f"Lỗi tại dòng: {e}")
                continue
        
        # In tiến độ
        if page % 5 == 0:
            print(f"📊 Đã thu thập được {len(all_jobs)} công việc...")
            # Lưu backup phòng hờ máy treo
            pd.DataFrame(all_jobs).to_csv("itviec_backup.csv", index=False, encoding="utf-8-sig")

finally:
    driver.quit()


if all_jobs:
    df = pd.DataFrame(all_jobs)
    df.drop_duplicates(subset=["Job Title", "Company"], inplace=True)
    df.to_csv("itviec_hanoi_data.csv", index=False, encoding="utf-8-sig")
    print(f"🎉 HOÀN THÀNH! Đã lưu {len(df)} jobs vào file !")
else:
    print("❌ Thất bại, không lấy được dữ liệu!")