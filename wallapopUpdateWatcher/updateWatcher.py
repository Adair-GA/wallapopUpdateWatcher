from typing import Callable
import httpx
from collections import deque
from pathlib import Path
import pickle
from .query import Query
import logging
from asyncio import iscoroutinefunction

logger = logging.getLogger(__name__)

class UpdateWatcher:
    """Clase que se encarga de facilitar la comparacion de resultados de busquedas en wallapop, para detectar nuevos productos que se hayan añadido
    Esto es util para poder detectr productos baratos a tiempo, ya que las notificaciones de wallapop no funcionan bien
    """
    # funcion que se llamará (con el id de la query que la ha activado y una lista de nuevos productos) cada vez
    # que se encuentren nuevos resultados
    callback: Callable

    # contiene las queries a realizar    
    _queries_queue: deque[Query]

    async def create(self,
                keywords: str,
                # lat_lon: tuple[int,int] | None = None,
                min_max_sale_price: tuple[int,int] | None = None) -> Query:
        """
        Añade la querie a la lista a comprobar y devuelve un objeto Query correspondiente a la misma
        **Parametros:**

        * **keywords** -  Palabras que usar en la busqueda
        * **min_max_sale_price** - (opcional) Precio minimo y maximo (tuple de enteros)
        """

        # if not lat_lon:
            # latitude="40.41956"
            # longitude= "-3.69196"
        # else:
        #     latitude,longitude = map(str,lat_lon)

        latitude="40.41956"
        longitude= "-3.69196"


        if min_max_sale_price:
            min_sale_price,max_sale_price = min_max_sale_price
        else:
            min_sale_price,max_sale_price = None,None

        q = Query(latitude,longitude,keywords,min_sale_price,max_sale_price)
        async with httpx.AsyncClient() as ses:
            await q.check(ses)
        self._queries_queue.append(q)

        return q

    async def checkOperation(self, *args):
        """Comprueba si hay nuevos resultados para la siguiente query en la lista.

        Args:
            args * :Argumentos que se le pasaran a la funcion callback
        """        
        async with httpx.AsyncClient() as client:
            q = self._queries_queue.popleft()
            result = await q.check(client)

        if result:
            if iscoroutinefunction(self._callback):
                await self._callback(q,result,*args)
            else:
                self._callback(q,result,*args)
        
        #se vuelve a añadir al final para que se vuelva a ciclar la lista completa antes de volver a comprobarse
        self._queries_queue.append(q)

    def load_queries_from_file(self, path: Path):
        """Cargo las queries desde un archivo

        Args:
            path (Path): Path del archivo a cargar
        """
        with open(path, "rb") as f:
            self._queries_queue = pickle.load(f)

    def save_queries(self, path: Path):
        """Guarda las queries en un archivo

        Args:
            path (Path): Path del archivo
        """
        path.touch(exist_ok=True)
        with open(path,"wb") as f:
            pickle.dump(self._queries_queue,f)

    def remove(self, ident: Query):
        """Elimina una query de la lista de queries a comprobar

        Args:
            ident (Query): query a eliminar
        """
        self._queries_queue.remove(ident)

    def __init__(self, callback: Callable) -> None:
        """
        Crea un objeto UpdateWatcher que se encargara de comprobar las queries que se le pasen y llamar a la funcion cuando se encuentren nuevos productos
        **Parametros:**

        * **callback** -  La funcion que se llamara cada vez que se detecte un nuevo producto. Se le pasaran como parametros
        una lista de productos.
        """
        self._queries_queue = deque()
        self._callback = callback

    def __len__(self) -> int:
        return len(self._queries_queue)