from wallapopUpdateWatcher import Query
import httpx
import pytest
from pytest_httpx import HTTPXMock
import re

def test_query_build_params():
    q = Query("0","0","Testkw",25,50)
    p = {
            "latitude": "0",
            "longitude": "0",
            "keywords": "Testkw",
            "order_by": "newest",
            "country_code": "ES",
            "filters_source": "search_box",
            "min_sale_price": "25",
            "max_sale_price": "50"
        }
    assert q._build_params() == p
    
    q = Query("0","0","Testkw",None,50)
    p = {
            "latitude": "0",
            "longitude": "0",
            "keywords": "Testkw",
            "order_by": "newest",
            "country_code": "ES",
            "filters_source": "search_box",
            "max_sale_price": "50"
        }
    assert q._build_params() == p

    q = Query("0","0","Testkw",25,None)
    p = {
            "latitude": "0",
            "longitude": "0",
            "keywords": "Testkw",
            "order_by": "newest",
            "country_code": "ES",
            "filters_source": "search_box",
            "min_sale_price": "25",
        }
    assert q._build_params() == p


@pytest.mark.asyncio
async def test_query_check(httpx_mock: HTTPXMock):
    RES = {
        "search_objects": [
        ]
    }
    def add(d: dict, n: int):
        d["search_objects"].append({
			"id": f"{n}",
			"title": f"Test{n}",
			"description": f"Test{n}",
			"images": [
				{
					"medium": f"image{n}"
				}
			],
			"price": 400/n,
			"currency": "EUR",
			"web_slug": f"test{n}",
			"supports_shipping": True,
			"shipping_allowed": True,
			"location": {
				"city": f"Mad{n}"
			}
		})


    pat = re.compile("https://api.wallapop.com/api/v3/general/search.*")
    httpx_mock.add_response(200,json=RES, url=pat)
    q = Query("0","0","Testkw",25,None)
    async with httpx.AsyncClient() as client:
        prod = await q.check(client)
        assert not prod
        
        add(RES,1)
        add(RES,2)
        add(RES,3)
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==3
        assert prod[0].title=="Test1"
        assert prod[1].title=="Test2"
        assert prod[2].title=="Test3"

        
        RES["search_objects"].reverse()
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==2
        assert prod[0].title=="Test3"
        assert prod[1].title=="Test2"
        
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0