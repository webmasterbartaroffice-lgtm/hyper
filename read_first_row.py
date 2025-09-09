import pandas as pd

def read_first_row():
    try:
        # خواندن فایل اکسل
        df = pd.read_excel('new.xlsx')
        
        # نمایش نام ستون‌ها
        print("\nنام ستون‌ها:")
        print("-------------")
        for col in df.columns:
            print(col)
            
        # نمایش اولین ردیف
        print("\nمقادیر اولین ردیف:")
        print("------------------")
        first_row = df.iloc[0]
        for col, value in first_row.items():
            print(f"{col}: {value}")
            
    except Exception as e:
        print(f"خطا در خواندن فایل: {str(e)}")

if __name__ == "__main__":
    read_first_row()