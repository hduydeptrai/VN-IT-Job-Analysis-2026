import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time
import random

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

all_jobs = []

try:
    base_url = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?page="
    
    for page in range(1, 100): 
        print(f"🚀 Đang bóc tách TopCV trang {page}...")
        driver.get(f"{base_url}{page}")
        time.sleep(random.uniform(5, 7))
        
        job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-item-2, .job-item-search-result")
        
        for card in job_cards:
            try:
                # 1. TIÊU ĐỀ: Lấy thuộc tính title để sạch bóng "Lì xì/Nổi bật"
                title_el = card.find_element(By.CSS_SELECTOR, ".title a, .job-title a")
                title = title_el.get_attribute("title") or title_el.text
                
                # 2. CÔNG TY
                company = card.find_element(By.CSS_SELECTOR, ".company, .company-name").text.strip()
                
                # 3. TÁCH BIỆT: LƯƠNG - KINH NGHIỆM - ĐỊA ĐIỂM
                # Lấy danh sách tất cả các nhãn thông tin
                info_labels = card.find_elements(By.CSS_SELECTOR, ".label-content")
                
                # Gán mặc định để tránh lỗi nếu thiếu data
                salary = "Thỏa thuận"
                experience = "Không yêu cầu"
                location = "Khác"

                # Phân tách theo vị trí cố định của TopCV
                if len(info_labels) >= 1:
                    raw_salary = info_labels[0].text.strip()
                    # Chuẩn hóa lương theo ý Duy: Số giữ, Chữ -> Thỏa thuận
                    salary = raw_salary if any(c.isdigit() for c in raw_salary) else "Thỏa thuận"
                
                if len(info_labels) >= 2:
                    experience = info_labels[1].text.strip()
                
                if len(info_labels) >= 3:
                    location = info_labels[2].text.strip()

                # 4. CHỈNH LẠI CỘT CITY (TỈNH THÀNH)
                city = "Khác"
                if any(x in location for x in ["Hà Nội", "HN"]): city = "Hà Nội"
                elif any(x in location for x in ["Hồ Chí Minh", "TP.HCM", "HCM"]): city = "TP.HCM"
                elif "Đà Nẵng" in location: city = "Đà Nẵng"
                else: city = location.split(',')[-1].strip()

                # 5. CỘT PHÚC LỢI (BENEFITS) & KỸ NĂNG (SKILLS)
                # Phúc lợi trên TopCV thường nằm ở các thẻ tag có màu hoặc label-content phía dưới
                all_tags = [t.text.strip() for t in card.find_elements(By.CSS_SELECTOR, ".tag, .item-tag")]
                
                # Tách riêng: Cái nào có chữ "Thưởng", "Lương", "Chế độ" là Phúc lợi
                benefits = [b for b in all_tags if any(word in b.lower() for word in ["thưởng", "chế độ", "bảo hiểm", "du lịch", "lương 13"])]
                # Cái còn lại là Skills
                skills = [s for s in all_tags if s not in benefits and 1 < len(s) < 15]

                all_jobs.append({
                    "Job Title": title,
                    "Company": company,
                    "Salary": salary,
                    "Experience": experience,
                    "City": city,
                    "Benefits": ", ".join(list(set(benefits))),
                    "Skills": ", ".join(list(set(skills)))
                })
            except: continue

finally:
    driver.quit()

# Xuất file CSV "Hoàn hảo"
df = pd.DataFrame(all_jobs)
df.to_csv("topcv_clean_final_v2.csv", index=False, encoding="utf-8-sig")
print(f"🎉 THÀNH CÔNG! Duy kiểm tra file 'topcv_clean_final_v2.csv' nhé!")