from dataclasses import dataclass
from typing import Optional

@dataclass(repr=False)
class Producto:
    ident: str
    title: str
    description: Optional[str]
    image: str
    price: int
    shippable: bool
    city: str
    link: str

    def __post_init__(self) -> None:
        self.process_data()

    def process_data(self):
        """Limita la descripcion a 60 caracteres y añade el link completo
        """
        if self.description is not None and len(self.description)>60:
            self.description = self.description[:60] + '...' 

        self.link = f"https://es.wallapop.com/item/{self.link}"


    def msg(self) -> str:
        """Genera el mensaje que se enviara al usuario para alertarle de un nuevo producto

        Returns:
            str: mensaje
        """        
        envio = "Si" if self.shippable else "No"
        
        if self.description is None:
            return f"Producto: {self.title}.\nPrecio: {self.price}€. Se envia: {envio}.\n{self.link}"
        else:
            return f"Producto: {self.title}. Descripción: {self.description}.\nPrecio: {self.price}€. Se envia: {envio}.\n{self.link}"

    def update(self, item: dict):
        """Actualiza los datos del producto con los de un item de la api de wallapop

        Args:
            item (dict): item de la api de wallapop
        """        
        self.title = item["title"]
        self.description = item["description"]
        self.image = item["images"][0]["medium"]
        self.price = item["price"]
        self.shippable = item["supports_shipping"] and item["shipping_allowed"]
        self.city = item["location"]["city"]
        self.link = item["web_slug"]
        
        self.process_data()


    def __hash__(self) -> int:
        return hash(self.ident)