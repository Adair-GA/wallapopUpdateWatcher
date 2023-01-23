from . import Query
import httpx
import pytest
from pytest_httpx import HTTPXMock
from wallapopUpdateWatcher.strategies import AnyChangeStrategy, PriceChangedStrategy, OnlyNewStrategy
import re

def test_query_build_params():
    q = Query("0","0","Testkw",25,50,AnyChangeStrategy())
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
    
    q = Query("0","0","Testkw",None,50, AnyChangeStrategy())
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

    q = Query("0","0","Testkw",25,None, AnyChangeStrategy())
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


@pytest.mark.asyncio
async def test_query_check(httpx_mock: HTTPXMock):
    RES = {
        "search_objects": [
        ]
    }
    pat = re.compile("https://api.wallapop.com/api/v3/general/search.*")
    httpx_mock.add_response(200,json=RES, url=pat)
    q = Query("0","0","Testkw",25,None, AnyChangeStrategy())
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
        assert len(prod)==0

@pytest.mark.asyncio
async def test_query_check_AnyChangeStrategy(httpx_mock: HTTPXMock):
    RES = {
        "search_objects": [
    ]
    }
    pat = re.compile("https://api.wallapop.com/api/v3/general/search.*")
    httpx_mock.add_response(200,json=RES, url=pat)

    q = Query("0","0","Testkw",25,None, AnyChangeStrategy())

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

        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0


        RES["search_objects"][0]["title"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        assert prod[0].title=="Test1Cambiado"

        RES["search_objects"][0]["description"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        assert prod[0].description=="Test1Cambiado"

        RES["search_objects"][0]["images"][0]["medium"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        assert prod[0].image=="Test1Cambiado"

        RES["search_objects"][0]["price"] = 100
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        assert prod[0].price==100

        RES["search_objects"][0]["currency"] = "USD"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES["search_objects"][0]["web_slug"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        assert prod[0].link=="https://es.wallapop.com/item/Test1Cambiado"

        RES["search_objects"][0]["supports_shipping"] = False
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        assert not prod[0].shippable

        RES["search_objects"][0]["location"]["city"] = "Test1Cambiado" 
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        assert prod[0].city=="Test1Cambiado"

        RES['search_objects'][0]['description'] = "Test1Cambiado" * 8
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1

        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES['search_objects'][0]['description'] = "Test1Cambiado" * 8 + "test"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        print(prod[0].description)



@pytest.mark.asyncio
async def test_query_check_PriceChangeStrategy(httpx_mock: HTTPXMock):
    RES = {
        "search_objects": [
    ]
    }
    pat = re.compile("https://api.wallapop.com/api/v3/general/search.*")
    httpx_mock.add_response(200,json=RES, url=pat)

    q = Query("0","0","Testkw",25,None, PriceChangedStrategy())

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

        RES["search_objects"][0]["title"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES["search_objects"][0]["price"] = 75
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1
        assert prod[0].title== "Test1Cambiado"
        assert prod[0].price== 75


        RES["search_objects"][0]["price"] = 75
        RES["search_objects"][0]["title"] = "Test1"
        RES["search_objects"][1]["price"] = 29
        RES["search_objects"][2]["price"] = 86
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==2
        assert prod[0].title== "Test2"
        assert prod[0].price== 29
        assert prod[1].title== "Test3"
        assert prod[1].price== 86




@pytest.mark.asyncio
async def test_query_check_OnlyNewStrategy(httpx_mock: HTTPXMock):
    RES = {
        "search_objects": [
    ]
    }
    pat = re.compile("https://api.wallapop.com/api/v3/general/search.*")
    httpx_mock.add_response(200,json=RES, url=pat)

    q = Query("0","0","Testkw",25,None, OnlyNewStrategy())

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

        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0


        RES["search_objects"][0]["title"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES["search_objects"][0]["description"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES["search_objects"][0]["images"][0]["medium"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES["search_objects"][0]["price"] = 100
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES["search_objects"][0]["web_slug"] = "Test1Cambiado"
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES["search_objects"][0]["supports_shipping"] = False
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES["search_objects"][0]["location"]["city"] = "Test1Cambiado" 
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0

        RES['search_objects'][0]['description'] = "Test1Cambiado" * 8
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==0
        
        add(RES,4)
        httpx_mock.add_response(200,json=RES, url=pat)
        prod = await q.check(client)
        assert len(prod)==1