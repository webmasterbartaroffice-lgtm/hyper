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
    # Get SKUs from 'کد کالا' and prices from 'قیمت فروش  ' (note the extra spaces)
    sku_price_data = {
        str(row['كد كالا']).strip(): float(row['قيمت فروش  '])  # Convert SKU to string and price to float
        for _, row in df.iterrows()
        if pd.notna(row['كد كالا']) and pd.notna(row['قيمت فروش  '])  # Only include rows where both SKU and price exist
    }
    return sku_price_data

def get_all_products():
    """Get all products from WooCommerce with better error handling"""
    all_products = []
    page = 1
    per_page = 20  # Reduced page size for better reliability
    
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

def update_batch_prices(product_updates):
    """Update multiple products at once using the batch update endpoint"""
    try:
        batch_data = {
            "update": [
                {
                    "id": product_id,
                    "regular_price": str(price)
                }
                for product_id, price in product_updates
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
        sku_price_data = load_excel_data('new.xlsx')
        print(f"Loaded {len(sku_price_data)} SKUs from Excel")
        
        # Get all WooCommerce products
        print("Fetching WooCommerce products...")
        all_products = get_all_products()
        
        if not all_products:
            print("No products found in WooCommerce or couldn't fetch products!")
            return
        
        print(f"\nSuccessfully fetched {len(all_products)} products from WooCommerce")
        
        # Create a mapping of SKU to product ID and current price
        sku_to_product = {
            product['sku']: {'id': product['id'], 'current_price': product['regular_price']}
            for product in all_products 
            if product['sku']
        }
        
        # Find matching SKUs
        matching_skus = set(sku_price_data.keys()) & set(sku_to_product.keys())
        
        print("\nSKU Analysis:")
        print(f"Total SKUs in Excel: {len(sku_price_data)}")
        print(f"Total SKUs in WooCommerce: {len(sku_to_product)}")
        print(f"Matching SKUs: {len(matching_skus)}")
        
        # Prepare updates
        updates_needed = []
        for sku in matching_skus:
            new_price = sku_price_data[sku]
            current_price = float(sku_to_product[sku]['current_price']) if sku_to_product[sku]['current_price'] else 0
            
            if current_price != new_price:
                updates_needed.append((sku_to_product[sku]['id'], new_price))
                print(f"Will update {sku}: {current_price} → {new_price}")
        
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