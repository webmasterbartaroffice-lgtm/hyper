import pandas as pd
import requests
import json
import time
import base64
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API credentials
CONSUMER_KEY = "ck_632cbd31da67a07adb33b6b848a98facd472b951"
CONSUMER_SECRET = "cs_1c8e450957778bd589844854a0007a98f84ed8e1"
BASE_URL = "https://hypermahdi.com/wp-json/wc/v3"

# Create basic auth header
AUTH_HEADER = {
    'Authorization': f'Basic {base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()}',
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json'
}

def load_excel_data(file_path):
    """Load and prepare Excel data"""
    df = pd.read_excel(file_path)
    
    sku_price_data = {}
    
    for _, row in df.iterrows():
        sku = str(row['كد كالا']).strip() if pd.notna(row['كد كالا']) else None
        
        # قیمت فروش (به ریال) → تبدیل به تومان
        sale_price = float(str(row['قيمت فروش  ']).replace(',', '').strip()) / 10 if pd.notna(row['قيمت فروش  ']) else None
        
        # مبلغ تخفیف (به ریال) → تبدیل به تومان
        discount = float(str(row['مبلغ تخفيف']).replace(',', '').strip()) / 10 if pd.notna(row['مبلغ تخفيف']) else 0
        
        if sku and sale_price is not None:
            sku_price_data[sku] = {
                'sale_price': sale_price,
                'discount': discount
            }
    
    return sku_price_data

def get_all_products():
    """Get all products from WooCommerce with better error handling"""
    all_products = []
    page = 1
    per_page = 50  # افزایش تعداد محصولات در هر صفحه به 50
    
    while True:
        try:
            print(f"Fetching page {page}...")
            response = requests.get(
                f"{BASE_URL}/products",
                headers=AUTH_HEADER,
                params={
                    "per_page": per_page,
                    "page": page,
                    "status": "publish"
                },
                verify=False
            )
            
            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                print(f"Response: {response.text}")
                break
            
            products = response.json()
            if not isinstance(products, list) or not products:
                break
            
            all_products.extend(products)
            print(f"Successfully fetched {len(products)} products from page {page}")
            
            # Check if we've got all products
            total_pages = int(response.headers.get('X-WP-TotalPages', 0))
            if page >= total_pages:
                break
                
            page += 1
            time.sleep(0.5)  # Small delay between requests
            
        except Exception as e:
            print(f"Error on page {page}: {str(e)}")
            break
    
    return all_products

def safe_float(value, default=0):
    """تبدیل ایمن مقدار به float"""
    if not value or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def update_batch_prices(product_updates):
    """Update multiple products at once using the batch update endpoint"""
    try:
        batch_data = {
            "update": [
                {
                    "id": product_id,
                    "regular_price": str(price_data['regular_price']),
                    "sale_price": str(price_data['sale_price']) if price_data.get('sale_price') is not None else ""
                }
                for product_id, price_data in product_updates
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/products/batch",
            headers=AUTH_HEADER,
            json=batch_data,
            verify=False
        )
        
        if response.status_code != 200:
            print(f"Batch update failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        return True
    except Exception as e:
        print(f"Error in batch update: {str(e)}")
        return False

def main():
    try:
        # Load Excel data
        print("Loading Excel data...")
        excel_data = load_excel_data('new.xlsx')
        print(f"Loaded {len(excel_data)} SKUs from Excel")
        
        # Get all WooCommerce products
        print("Fetching WooCommerce products...")
        all_products = get_all_products()
        
        if not all_products:
            print("No products found in WooCommerce or couldn't fetch products!")
            return
        
        print(f"\nSuccessfully fetched {len(all_products)} products from WooCommerce")
        
        # Prepare updates for ALL products
        updates_needed = []
        for product in all_products:
            if not product.get('sku'):  # اگر محصول SKU نداشت، رد کن
                continue
                
            sku = product['sku']
            current_price = safe_float(product['price'])
            
            # اگر محصول در فایل اکسل بود
            if sku in excel_data:
                excel_price = excel_data[sku]['sale_price']  # قیمت فروش از اکسل
                discount = excel_data[sku]['discount']       # مبلغ تخفیف از اکسل
                
                if discount > 0:
                    # مثال: قیمت فروش = 1000 تومان، تخفیف = 200 تومان
                    # Regular Price = 1000 تومان (قیمت عادی)
                    # Sale Price = 1000 - 200 = 800 تومان (قیمت نهایی با تخفیف)
                    regular_price = excel_price
                    sale_price = excel_price - discount
                else:
                    # اگر تخفیف نداشت، فقط قیمت عادی
                    regular_price = excel_price
                    sale_price = None
            else:
                # اگر محصول در فایل اکسل نبود، از قیمت فعلی استفاده کن
                current_regular_price = safe_float(product['regular_price'], current_price)
                current_sale_price = safe_float(product['sale_price'])
                
                if current_sale_price > 0:
                    # اگر قیمت فروش داشت، تخفیف رو محاسبه کن
                    regular_price = current_regular_price
                    sale_price = current_sale_price
                else:
                    # اگر قیمت فروش نداشت، فقط قیمت عادی رو تنظیم کن
                    regular_price = current_regular_price
                    sale_price = None
            
            # اگر قیمت‌ها تغییر کرده باشند، به‌روزرسانی کن
            current_regular = safe_float(product.get('regular_price', 0))
            current_sale = safe_float(product.get('sale_price', 0))
            
            if (current_regular != regular_price or current_sale != (sale_price or 0)):
                updates_needed.append((
                    product['id'],
                    {
                        'regular_price': regular_price,
                        'sale_price': sale_price
                    }
                ))
                print(f"\nWill update {sku}:")
                print(f"Regular Price: {current_regular} → {regular_price}")
                if sale_price is not None:
                    print(f"Sale Price: {current_sale} → {sale_price}")
        
        print(f"\nFound {len(updates_needed)} products that need price updates")
        
        if not updates_needed:
            print("No price updates needed!")
            return
        
        # Ask for confirmation
        input("\nPress Enter to start updating prices, or Ctrl+C to cancel...")
        
        # Process updates in batches of 20
        batch_size = 20  # Reduced batch size for better reliability
        success_count = 0
        error_count = 0
        
        for i in range(0, len(updates_needed), batch_size):
            batch = updates_needed[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} of {(len(updates_needed) + batch_size - 1)//batch_size}")
            
            if update_batch_prices(batch):
                success_count += len(batch)
                print(f"Successfully updated {len(batch)} products in this batch")
            else:
                error_count += len(batch)
                print(f"Failed to update {len(batch)} products in this batch")
            
            # Add a small delay between batches
            if i + batch_size < len(updates_needed):
                print("Waiting 2 seconds before next batch...")
                time.sleep(2)
        
        print("\nUpdate Summary:")
        print(f"Successfully updated: {success_count} products")
        print(f"Failed to update: {error_count} products")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()