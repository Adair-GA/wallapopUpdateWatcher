from typing import Callable
import httpx
from collections import deque
from pathlib import Path
import pickle
from .query import Query


# tiempo total de espera en minutos (por cada request)
ESPERA = 15


class UpdateWatcher:
    # funcion que se llamará (con el id de la query que la ha activado y una lista de nuevos productos) cada vez
    # que se encuentren nuevos resultados
    callback: Callable
    
    espera: float

    # contiene las queries a realizar    
    _queries_queue: deque[Query] = deque()
    _a_eliminar = set()

    async def create(self,
                keywords: str,
                lat_lon: tuple[int,int] | None = None,
                min_max_sale_price: tuple[int,int] | None = None) -> int:
        """
        Añade la querie a la lista a comprobar y devuelve el identificador con el que se llamara al callback cuando haya un nuevo producto
        **Parametros:**

        * **keywords** -  Palabras que usar en la busqueda
        * **lat_lon** - (opcional) Tuple de latitud y longitud en las que buscar. Si no se establece se usara Madrid
        * **min_max_sale_price** - (opcional) Precio minimo y maximo (tuple de enteros)
        """

        if not lat_lon:
            latitude="40.41956"
            longitude= "-3.69196"
        else:
            latitude,longitude = map(str,lat_lon)

        if min_max_sale_price:
            min_sale_price,max_sale_price = min_max_sale_price
        else:
            min_sale_price,max_sale_price = None,None

        q = Query(latitude,longitude,keywords,min_sale_price,max_sale_price)
        async with httpx.AsyncClient() as ses:
            await q.check(ses)
        self._queries_queue.append(q)
        self.espera = self.getWaitTime()

        return id(q)

    async def checkOperation(self, args: list):
        
        async with httpx.AsyncClient() as client:
            q = self._queries_queue.popleft()
            if id(q) in self._a_eliminar:
                return
                # la query ni se comprueba ni se vuelve a añadir a la lista

            result = await q.check(client)
            if result:
                await self._callback(id(q),result,*args)
            
            self._queries_queue.append(q)

    def load_queries_from_file(self, path: Path):
        with open(path, "rb") as f:
            self._queries_queue = pickle.load(f)

    def save_queries(self, path: Path):   
        save = [item for item in self._queries_queue if id(item) not in self._a_eliminar]

        q = deque(save)

        path.touch(exist_ok=True)
        with open(path,"wb") as f:
            pickle.dump(q,f)

    def remove(self, ident: Query):
        self._a_eliminar.add(ident)

    def getWaitTime(self) -> float:
        return (ESPERA*60)/len(self._queries_queue)

    def __init__(self, callback: Callable, espera: float = ESPERA) -> None:
        """
        Crea el watcher de novedaes
        **Parametros:**

        * **callback** -  La funcion que se llamara cada vez que se detecte un nuevo producto. Se le pasaran como parametros
        la una lista de productos 
        * **espera** - (opcional) El tiempo en minutos entre cada comprobacion por cada alerta añadida. 5 minutos por defecto, es
        decir, si hay solo una alerta, se comprobará cada 5 minutos, si hay dos, se comprobara la primera y 2,5 minutos despues, la segunda,
        manteniendo entonces los 5 minutos por alerta 
        """
        self._callback = callback