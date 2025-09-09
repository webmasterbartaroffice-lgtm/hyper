import base64
import time
from datetime import datetime
from typing import Dict, Any, List

import requests
import urllib3

from .config import Config


# غیرفعال‌کردن هشدارهای SSL در صورت verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WooUpdater:
    def __init__(self) -> None:
        credentials = base64.b64encode(
            f"{Config.WOOCOMMERCE_CONSUMER_KEY}:{Config.WOOCOMMERCE_CONSUMER_SECRET}".encode()
        ).decode()

        self.auth_header = {
            'Authorization': f'Basic {credentials}',
            'User-Agent': 'TelegramBot/1.0',
            'Accept': 'application/json',
        }

        self.base_url = Config.WOOCOMMERCE_BASE_URL.rstrip('/')

    def _safe_float(self, value, default=0.0) -> float:
        try:
            if value in (None, "", False):
                return default
            return float(value)
        except Exception:
            return default

    def _get_all_products(self) -> List[Dict[str, Any]]:
        all_products: List[Dict[str, Any]] = []
        page = 1
        per_page = 50
        while True:
            resp = requests.get(
                f"{self.base_url}/products",
                headers=self.auth_header,
                params={"per_page": per_page, "page": page, "status": "publish"},
                verify=False,
            )
            if resp.status_code != 200:
                break
            items = resp.json()
            if not isinstance(items, list) or not items:
                break
            all_products.extend(items)
            total_pages = int(resp.headers.get('X-WP-TotalPages', 0))
            if page >= total_pages:
                break
            page += 1
            time.sleep(Config.REQUEST_DELAY)
        return all_products

    def _batch_update(self, updates: List[Dict[str, Any]]) -> bool:
        if not updates:
            return True
        payload = {
            "update": [
                {
                    "id": item['id'],
                    "regular_price": str(item['regular_price']),
                    **({"sale_price": str(item['sale_price'])} if item.get('sale_price') is not None else {}),
                }
                for item in updates
            ]
        }
        resp = requests.post(
            f"{self.base_url}/products/batch",
            headers=self.auth_header,
            json=payload,
            verify=False,
        )
        return resp.status_code == 200

    async def update_prices(self, excel_data: Dict[str, Dict[str, Any]]):
        start = datetime.now()
        try:
            products = self._get_all_products()
            if not products:
                return {"total": 0, "updated": 0, "errors": 1, "duration": 0}

            sku_to_product = {p.get('sku'): p for p in products if p.get('sku')}
            matching = set(excel_data.keys()) & set(sku_to_product.keys())

            updates: List[Dict[str, Any]] = []
            for sku in matching:
                p = sku_to_product[sku]
                new_vals = excel_data[sku]
                current_regular = self._safe_float(p.get('regular_price'))
                current_sale = self._safe_float(p.get('sale_price')) if p.get('sale_price') else None

                desired_regular = float(new_vals['regular_price'])
                desired_sale = float(new_vals['sale_price']) if new_vals.get('sale_price') is not None else None

                if current_regular != desired_regular or (current_sale or 0) != (desired_sale or 0):
                    updates.append({
                        'id': p['id'],
                        'regular_price': desired_regular,
                        'sale_price': desired_sale,
                    })

            updated = 0
            errors = 0
            # پردازش دسته‌ای
            for i in range(0, len(updates), Config.BATCH_SIZE):
                chunk = updates[i:i + Config.BATCH_SIZE]
                ok = self._batch_update(chunk)
                if ok:
                    updated += len(chunk)
                else:
                    errors += len(chunk)
                if i + Config.BATCH_SIZE < len(updates):
                    time.sleep(max(Config.REQUEST_DELAY, 0.2))

            duration = (datetime.now() - start).total_seconds()
            return {
                'total': len(matching),
                'updated': updated,
                'errors': errors,
                'duration': round(duration, 2),
            }
        except Exception:
            return {"total": 0, "updated": 0, "errors": 1, "duration": 0}


