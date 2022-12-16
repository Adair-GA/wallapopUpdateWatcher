from typing import Callable
import httpx
from collections import deque
from pathlib import Path
import pickle
from .query import Query
import logging

logger = logging.getLogger(__name__)


# tiempo total de espera en minutos (por cada request)
ESPERA = 15


class UpdateWatcher:
    # funcion que se llamará (con el id de la query que la ha activado y una lista de nuevos productos) cada vez
    # que se encuentren nuevos resultados
    callback: Callable
    
    espera: float

    # contiene las queries a realizar    
    _queries_queue: deque[Query] = deque()

    async def create(self,
                keywords: str,
                lat_lon: tuple[int,int] | None = None,
                min_max_sale_price: tuple[int,int] | None = None) -> Query:
        """
        Añade la querie a la lista a comprobar y devuelve un objeto Query
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

        return q

    async def checkOperation(self, args: list):
        """
        Realiza la comprobacion de la proxima query en la lista y llama al callback si hay productos nuevos 
        """
        async with httpx.AsyncClient() as client:
            q = self._queries_queue.popleft()
            result = await q.check(client)

        if result:
            await self._callback(q,result,*args)
        
        #se vuelve a añadir al final para que se vuelva a ciclar la lista completa antes de volver a comprobarse
        self._queries_queue.append(q)

    def load_queries_from_file(self, path: Path):
        with open(path, "rb") as f:
            self._queries_queue = pickle.load(f)

    def save_queries(self, path: Path):   
        path.touch(exist_ok=True)
        with open(path,"wb") as f:
            pickle.dump(self._queries_queue,f)

    def remove(self, ident: Query):
        self._queries_queue.remove(ident)

    def getWaitTime(self) -> float:
        """
        Devuelve el tiempo en segundos que se debe de esperar hasta ejecutar la siguiente comprobacion. 
        """
        try:
            return (self.espera*60)/len(self._queries_queue)
        except ZeroDivisionError:
            logger.warn("Se ha intentado llamar al metodo getWaitTime sin queries. Se ha de evitar esto")
            return 0
            

    def __init__(self, callback: Callable, espera: float = ESPERA) -> None:
        """
        Crea el watcher de novedaes
        **Parametros:**

        * **callback** -  La funcion que se llamara cada vez que se detecte un nuevo producto. Se le pasaran como parametros
        una lista de productos.
        * **espera** - (opcional) El tiempo en minutos entre cada comprobacion por cada alerta añadida. 15 minutos por defecto, es
        decir, si hay solo una alerta, se comprobará cada 15 minutos, si hay dos, se comprobara la primera y 7,5 minutos despues, la segunda,
        manteniendo entonces los 15 minutos por alerta 
        """
        self.espera = espera
        self._callback = callback

    def __len__(self) -> int:
        return len(self._queries_queue)