from abc import ABC
from wallapopUpdateWatcher.producto import Producto


class Strategy(ABC):
    alertados: dict[str, Producto]

    def __init__(self):
        self.alertados = dict()

    def is_notifiable(self, d: dict) -> tuple[bool, Producto | None]:
        raise NotImplementedError

    def _add(self, d) -> Producto:
        p = Producto(d["id"],
                     d["title"],
                     d["description"],
                     d["images"][0]["medium"],
                     d["price"],
                     d["supports_shipping"] and d["shipping_allowed"],
                     d["location"]["city"],
                     d["web_slug"])
        self.alertados[d["id"]] = p
        return p


class OnlyNewStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def is_notifiable(self, d: dict) -> tuple[bool, Producto | None]:
        if d["id"] not in self.alertados:
            p = self._add(d)

            return True, p
        else:
            return False, None


class PriceChangedStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def is_notifiable(self, d: dict) -> tuple[bool, Producto | None]:
        if d["id"] not in self.alertados:
            p = self._add(d)

            return True, p
        else:
            if self.alertados[d["id"]].price != d["price"]:
                old = self.alertados[d["id"]]
                old._update(d)

                return True, old
            else:
                return False, None


class AnyChangeStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def is_notifiable(self, d: dict) -> tuple[bool, Producto | None]:
        if d["id"] not in self.alertados:
            p = self._add(d)

            return True, p
        else:
            old = self.alertados[d["id"]]
            new_p = Producto(d["id"], d["title"], d["description"], d["images"][0]["medium"], d["price"],
                             d["supports_shipping"] and d["shipping_allowed"], d["location"]["city"], d["web_slug"])
            if old != new_p:
                self.alertados[d["id"]] = new_p

                return True, new_p
            else:
                return False, None
