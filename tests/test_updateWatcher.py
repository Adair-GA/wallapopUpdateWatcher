from . import UpdateWatcher,Query
import pytest
from pytest_httpx import HTTPXMock
import re
import pathlib
import pickle

times_callback=0
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
async def test_updateWatcher_create(httpx_mock: HTTPXMock):
    res = {
        "search_objects": [
        ]
    }

    pat = re.compile("https://api.wallapop.com/api/v3/general/search.*")
    httpx_mock.add_response(200,json=res, url=pat)
    
    watcher = UpdateWatcher(print)
    assert len(watcher) == 0
    q = await watcher.create("Test")

    assert q.keywords=="Test"
    assert q.max_sale_price==None
    assert q.min_sale_price==None
    
    assert len(watcher) == 1

    # comprobar precios

    q = await watcher.create("Test2", min_max_sale_price=(15,30))

    assert q.keywords=="Test2"
    assert q.min_sale_price==15
    assert q.max_sale_price==30


    q = await watcher.create("Test2",min_max_sale_price=(None,30))

    assert q.keywords=="Test2"
    assert q.min_sale_price==None
    assert q.max_sale_price==30
    
    q = await watcher.create("Test2",min_max_sale_price=(15,None))

    assert q.keywords=="Test2"
    assert q.min_sale_price==15
    assert q.max_sale_price==None



    # comprobar que se establece bien el ultimo elemento al crearlas


    add(res,1)
    httpx_mock.add_response(200,json=res, url=pat)
    q = await watcher.create("Test2")

    assert q.keywords=="Test2"
    assert q.max_sale_price==None
    assert q.min_sale_price==None

@pytest.mark.asyncio
async def test_updateWatcher_remove():
    watcher = UpdateWatcher(print)
    assert len(watcher)==0

    q = await watcher.create("Test")
    assert len(watcher)==1
    assert q in watcher._queries_queue

    watcher.remove(q)
    assert len(watcher)==0

    assert q not in watcher._queries_queue

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

    q1 = await watcher.create("Test1")
    q2 = await watcher.create("Test2")

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

@pytest.mark.asyncio
async def test_updateWatcher_save_and_load(httpx_mock: HTTPXMock):
    p = pathlib.Path("tests/test.pickle")

    if p.exists():
        p.unlink()

    assert not p.exists()

    res = {
        "search_objects": [
        ]
    }

    pat = re.compile("https://api.wallapop.com/api/v3/general/search.*")
    httpx_mock.add_response(200,json=res, url=pat)
    
    watcher = UpdateWatcher(print)
    assert len(watcher) == 0
    await watcher.create("Test")
    assert len(watcher) == 1
    watcher.save_queries(p)
    assert p.exists()

    load = pickle.load(open(p,"rb"))
    assert len(load) == 1
    assert load[0].keywords == "Test"
    assert load[0].min_sale_price == None
    assert load[0].max_sale_price == None

    del watcher
    watcher = UpdateWatcher(print)
    watcher.load_queries_from_file(p)
    q = watcher._queries_queue[0]

    assert q.keywords=="Test"
    assert q.min_sale_price==None
    assert q.max_sale_price==None


    await watcher.create("Test2")
    await watcher.checkOperation()
    await watcher.checkOperation()
    await watcher.checkOperation()
    await watcher.checkOperation()
    await watcher.checkOperation()
    assert len(watcher) == 2

    watcher.save_queries(p)
    assert p.exists()

    load = pickle.load(open(p,"rb"))
    assert len(load) == 2
    assert load[0].keywords == "Test" or load[1].keywords == "Test"
    assert load[0].min_sale_price == None
    assert load[0].max_sale_price == None

    del watcher
    watcher = UpdateWatcher(print)
    watcher.load_queries_from_file(p)
    q = watcher._queries_queue[0]

    assert q.keywords=="Test" or q.keywords=="Test2"
    assert q.min_sale_price==None
    assert q.max_sale_price==None
