import pandas as pd
import re

# 1. Đọc file
df = pd.read_csv('D:\Data Analysis\data\final_project_data_unified.csv')

# 2. Chuẩn hóa Địa điểm (Về Ha Noi và Ho Chi Minh)
def advanced_clean_location(loc):
    if pd.isna(loc): return "Unknown"
    loc = str(loc).lower().strip()
    
    # Gom nhóm chính
    if 'hà nội' in loc or 'ha noi' in loc: return "Ha Noi"
    if 'hồ chí minh' in loc or 'ho chi minh' in loc or 'hcm' in loc: return "Ho Chi Minh"
    if 'đà nẵng' in loc or 'da nang' in loc: return "Da Nang"
    
    # Xử lý tin rác/không rõ
    if loc in ['khác', 'unknown', 'toàn quốc', 'others']: return "Unknown"
    
    # Nếu có \n (lỗi cào TopCV), lấy phần tỉnh thành đầu tiên
    loc = loc.split('\n')[0].strip()
    return loc.title() # Tự động viết hoa chữ cái đầu

# 3. Chuyển Kinh nghiệm thành con số (Để Power BI tính được)
def get_exp_year(exp):
    nums = re.findall(r'\d+', str(exp))
    return int(nums[0]) if nums else 0
df['Exp_Year'] = df['Experience'].apply(get_exp_year)

# 4. Tách lương thành số Min và Max
def get_salary_num(sal):
    nums = re.findall(r'\d+', str(sal))
    if len(nums) >= 2: return pd.Series([float(nums[0]), float(nums[1])])
    if len(nums) == 1: return pd.Series([float(nums[0]), float(nums[0])])
    return pd.Series([None, None])
df[['Sal_Min', 'Sal_Max']] = df['Salary'].apply(get_salary_num)

# 5. Lưu file "Pro Cleaned"
df.to_csv('final_data_pro_cleaned.csv', index=False)