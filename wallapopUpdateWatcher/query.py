from dataclasses import dataclass,field
from typing import Optional
import httpx
from .producto import Producto

URL = "https://api.wallapop.com/api/v3/general/search"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "DNT": "1",
    "DeviceOS": "0",
    "Origin": "https://es.wallapop.com",
    "Pragma": "no-cache",
    "Referer": "https://es.wallapop.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
}

@dataclass
class Query:
    latitude: str
    longitude: str
    keywords: str
    min_sale_price: Optional[int]
    max_sale_price: Optional[int]

    _last_item_id: str = field(init=False, default=None)

    async def check(self, ses: httpx.AsyncClient) -> list[Producto]:
        r = await ses.request("GET", URL, headers=HEADERS, params=self._build_params())
        r = r.json()

        ret = []
        for item in r["search_objects"]:
            if item["id"] == self._last_item_id:
                break
            ret.append(Producto(
                item["title"],
                item["description"],
                item["images"][0]["medium"],
                item["price"],
                item["supports_shipping"] and item["shipping_allowed"],
                item["location"]["city"],
                item["web_slug"]
            ))
        
        # actualizamos el valor de la ultima id para que no vuelva a detectarlos
        if ret:
            first_id=r["search_objects"][0]["id"]
            self._last_item_id = first_id
        
        return ret

    def _build_params(self):
        p = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "keywords": self.keywords,
            "order_by": "newest",
            "country_code": "ES",
            "filters_source": "search_box"
        }
        
        if self.min_sale_price:
            p["min_sale_price"] = str(self.min_sale_price)
        if self.max_sale_price:
            p["max_sale_price"] = str(self.max_sale_price)
        
        return p

    def __hash__(self):
        if self.max_sale_price:
            if self.min_sale_price:
                return hash(
                    f"walla{self.keywords}{self.latitude}{self.longitude}{self.max_sale_price}{self.min_sale_price}")
            else:
                return hash(f"walla{self.keywords}{self.latitude}{self.longitude}{self.max_sale_price}")
        else:
            if self.min_sale_price:
                return hash(f"walla{self.keywords}{self.latitude}{self.longitude}{self.min_sale_price}")
            else:
                return hash(f"walla{self.keywords}{self.latitude}{self.longitude}")