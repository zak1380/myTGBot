import csv
import os

FILE_NAME = "users.csv"

# ذخیره اطلاعات کاربر (فقط اگر user_id جدید باشد)
def save_user_data(user_id, name, age, education, experience, interest, reason):
    try:
        if not os.path.isfile(FILE_NAME):
            with open(FILE_NAME, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'user_id', 'نام', 'سن', 'مدرک تحصیلی',
                    'تجربه قبلی', 'بخش مورد علاقه', 'انگیزه'
                ])

        with open(FILE_NAME, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and row[0] == str(user_id):
                    return  # قبلاً ثبت شده

        with open(FILE_NAME, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                user_id, name, age, education,
                experience, interest, reason
            ])

    except Exception as e:
        print(f"❌ خطا در ذخیره اطلاعات کاربر: {e}")

# گرفتن لیست یونیک از user_id ها
def get_all_user_ids():
    if not os.path.isfile(FILE_NAME):
        return []
    ids = set()
    with open(FILE_NAME, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row and row[0].isdigit():
                ids.add(row[0])
    return list(ids)

# تعداد کل کاربران یونیک
def get_user_count():
    return len(get_all_user_ids())
