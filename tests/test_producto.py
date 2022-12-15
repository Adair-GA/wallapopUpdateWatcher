from wallapopUpdateWatcher import Producto

def test_producto_con_descripcion() -> None:
    p = Producto("Test", "testDescription", "imagelink", 50, True, "mad", "test")
    assert p.link == "https://es.wallapop.com/item/test"
    assert p.msg() == "Producto: Test. Descripción: testDescription.\nPrecio: 50€. Se envia: Si.\nhttps://es.wallapop.com/item/test"

    p = Producto("Test", "testDescription"*60, "imagelink", 50, True, "mad", "test")
    assert p.description == ("testDescription"*60)[0:60] + "..."


def test_producto_sin_descripcion() -> None:
    p = Producto("Test", None, "imagelink", 50, True, "mad", "test")
    assert p.msg() == "Producto: Test.\nPrecio: 50€. Se envia: Si.\nhttps://es.wallapop.com/item/test"
    assert p.msg() != "Producto: Test2.\nPrecio: 50€. Se envia: Si.\nhttps://es.wallapop.com/item/test"
