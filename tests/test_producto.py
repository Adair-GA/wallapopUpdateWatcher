from wallapopUpdateWatcher import Producto

def test_producto_con_descripcion() -> None:
    p = Producto("aa","Test", "testDescription", "imagelink", 50, True, "mad", "test")
    assert p.link == "https://es.wallapop.com/item/test"
    assert p.msg() == "Producto: Test. Descripción: testDescription.\nPrecio: 50€. Se envia: Si.\nhttps://es.wallapop.com/item/test"

    p = Producto("aa","Test", "testDescription"*60, "imagelink", 50, True, "mad", "test")
    assert p.description == "testDescription"*60


def test_producto_sin_descripcion() -> None:
    p = Producto("aa","Test", None, "imagelink", 50, True, "mad", "test")
    assert p.msg() == "Producto: Test.\nPrecio: 50€. Se envia: Si.\nhttps://es.wallapop.com/item/test"
    assert p.msg() != "Producto: Test2.\nPrecio: 50€. Se envia: Si.\nhttps://es.wallapop.com/item/test"

def test_producto_update() -> None:
    p = Producto("aa","Test", None, "imagelink", 50, True, "mad", "test")
    assert p.msg() == "Producto: Test.\nPrecio: 50€. Se envia: Si.\nhttps://es.wallapop.com/item/test"
    d = {
        "title": "Test2",
        "description": None,
        "images": [{"medium": "imagelink"}],
        "price": 50,
        "supports_shipping": True,
        "shipping_allowed": True,
        "location": {
            "city": "mad"
            },
        "web_slug": "test"
    }
    
    p.update(d)
    assert p.msg() == "Producto: Test2.\nPrecio: 50€. Se envia: Si.\nhttps://es.wallapop.com/item/test"

    d["description"] = "testDescription"

    p.update(d)
    assert p.description=="testDescription"