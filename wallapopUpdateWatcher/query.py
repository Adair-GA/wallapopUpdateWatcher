from dataclasses import dataclass,field
from typing import Optional
import httpx
from .producto import Producto
from .strategies import Strategy

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
    strategy: Strategy


    async def check(self, ses: httpx.AsyncClient) -> list[Producto]:
        """Comprueba si hay nuevos resultados para la query.

        Args:
            ses (httpx.AsyncClient): Sesion httpx para utilizar

        Returns:
            list[Producto]: Lista de productos nuevos que se encuentren para la query
        """        
        r = await ses.request("GET", URL, headers=HEADERS, params=self._build_params())
        r = r.json()

        ret = []
        for item in r["search_objects"]:
            prod = self.strategy.isNotifiable(item)
            if prod[0]:
                ret.append(prod[1])
        
        return ret

    def _build_params(self)->dict:
        """Construye los parametros para la peticion de la query

        Returns:
            dict: Diccionario con los parametros
        """        
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