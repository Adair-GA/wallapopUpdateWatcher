from wallapopUpdateWatcher import UpdateWatcher,Query
import httpx
import pytest
from pytest_httpx import HTTPXMock
import re


@pytest.mark.asyncio
async def test_updateWatcher_create(httpx_mock: HTTPXMock):
    res = {
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
    httpx_mock.add_response(200,json=res, url=pat)
    
    watcher = UpdateWatcher(print)
    assert len(watcher) == 0
    q = await watcher.create("Test",None)

    assert q.keywords=="Test"
    assert q.max_sale_price==None
    assert q.min_sale_price==None
    assert q._last_item_id==None
    
    assert len(watcher) == 1



    # comprobar precios

    q = await watcher.create("Test2",(15,30))

    assert q.keywords=="Test2"
    assert q.min_sale_price==15
    assert q.max_sale_price==30
    assert q._last_item_id==None



    q = await watcher.create("Test2",(None,30))

    assert q.keywords=="Test2"
    assert q.min_sale_price==None
    assert q.max_sale_price==30
    assert q._last_item_id==None
    
    q = await watcher.create("Test2",(15,None))

    assert q.keywords=="Test2"
    assert q.min_sale_price==15
    assert q.max_sale_price==None
    assert q._last_item_id==None



    # comprobar que se establece bien el ultimo elemento al crearlas


    add(res,1)
    httpx_mock.add_response(200,json=res, url=pat)
    q = await watcher.create("Test2",None)

    assert q.keywords=="Test2"
    assert q.max_sale_price==None
    assert q.min_sale_price==None
    assert q._last_item_id=="1"

@pytest.mark.asyncio
async def test_updateWatcher_remove():
    watcher = UpdateWatcher(print)
    assert len(watcher)==0

    q = await watcher.create("Test",None)
    assert len(watcher)==1
    assert q in watcher._queries_queue

    watcher.remove(q)
    assert len(watcher)==0

    assert q not in watcher._queries_queue

@pytest.mark.asyncio
async def test_updateWatcher_getWaitTime():
    watcher = UpdateWatcher(print)
    assert watcher.getWaitTime() == 0

    await watcher.create("Test",None)
    assert watcher.getWaitTime() == 15*60

    q = await watcher.create("Test2",None)
    assert watcher.getWaitTime() == (15*60)/2

    watcher.remove(q)
    assert watcher.getWaitTime() == 15*60


    # comprobar con tiempos de espera personalizados
    watcher=UpdateWatcher(print,5)
    assert watcher.getWaitTime() == 0

    await watcher.create("Test",None)
    assert watcher.getWaitTime() == 5*60

    q = await watcher.create("Test2",None)
    assert watcher.getWaitTime() == (5*60)/2

    watcher.remove(q)
    assert watcher.getWaitTime() == 5*60


times_callback=0

@pytest.mark.asyncio
async def test_updateWatcher_check(httpx_mock: HTTPXMock):
    res_1 = {
        "search_objects": [
        ]
    }
    res_2 = {
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
    global times_callback

    async def callback(q: Query,result, should_be: Query):
        global times_callback
        times_callback+=1
        assert q==should_be
        print("djfhsdifb")


    pattern_1 = re.compile("https://api.wallapop.com/api/v3/general/search.*keywords=Test1")
    httpx_mock.add_response(200,json=res_1, url=pattern_1)
    pattern_2 = re.compile("https://api.wallapop.com/api/v3/general/search.*keywords=Test2")
    httpx_mock.add_response(200,json=res_2, url=pattern_2)


    watcher = UpdateWatcher(callback)

    q1 = await watcher.create("Test1",None)
    q2 = await watcher.create("Test2",None)

    add(res_1,1)
    httpx_mock.add_response(200,json=res_1, url=pattern_1)
    await watcher.checkOperation(q1)
    assert times_callback==1

    await watcher.checkOperation()
    assert times_callback==1


    add(res_2,1)
    httpx_mock.add_response(200,json=res_2, url=pattern_2)
    
    await watcher.checkOperation()
    assert times_callback==1

    await watcher.checkOperation(q2)
    assert times_callback==2

