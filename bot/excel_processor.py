import pandas as pd


class ExcelProcessor:
    def __init__(self) -> None:
        # توجه: در داده‌های شما ستون ‘قيمت فروش  ’ دارای دو فاصله انتهایی است
        self.required_columns = ['كد كالا', 'قيمت فروش  ']

    def _to_float(self, value):
        if value is None:
            return None
        try:
            # حذف ویرگول‌های هزارگان و فاصله
            return float(str(value).replace(',', '').strip())
        except Exception:
            return None

    def process_file(self, file_path: str):
        try:
            df = pd.read_excel(file_path)

            # اعتبارسنجی ستون‌ها
            missing = [c for c in self.required_columns if c not in df.columns]
            if missing:
                raise ValueError(f"ستون‌های مورد نیاز پیدا نشد: {missing}")

            sku_data = {}
            for _, row in df.iterrows():
                sku = str(row['كد كالا']).strip() if pd.notna(row['كد كالا']) else None
                sale_price = self._to_float(row['قيمت فروش  ']) if pd.notna(row['قيمت فروش  ']) else None
                discount = self._to_float(row['مبلغ تخفيف']) if 'مبلغ تخفيف' in df.columns and pd.notna(row['مبلغ تخفيف']) else 0

                if not sku or sale_price is None:
                    continue

                # اگر قیمت‌ها بر حسب ریال باشند و باید به تومان تبدیل شود، می‌توانید اینجا تقسیم بر 10 کنید
                # sale_price = sale_price / 10
                # discount = (discount or 0) / 10

                if (discount or 0) > 0:
                    regular_price = sale_price
                    final_sale = max(sale_price - discount, 0)
                else:
                    regular_price = sale_price
                    final_sale = None

                sku_data[sku] = {
                    'regular_price': regular_price,
                    'sale_price': final_sale
                }

            return sku_data
        except Exception as e:
            print(f"خطا در پردازش Excel: {e}")
            return None


