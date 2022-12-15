from dataclasses import dataclass
from typing import Optional

@dataclass(repr=False)
class Producto:
    title: str
    description: Optional[str]
    image: str
    price: int
    shippable: bool
    city: str
    link: str

    def __post_init__(self) -> None:
        if self.description is not None and len(self.description)>60:
            self.description = self.description[:60] + '...' 

        self.link = f"https://es.wallapop.com/item/{self.link}"


    def msg(self) -> str:
        envio = "Si" if self.shippable else "No"
        
        if self.description is None:
            return f"Producto: {self.title}.\nPrecio: {self.price}€. Se envia: {envio}.\n{self.link}"
        else:
            return f"Producto: {self.title}. Descripción: {self.description}.\nPrecio: {self.price}€. Se envia: {envio}.\n{self.link}"