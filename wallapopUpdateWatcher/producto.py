from dataclasses import dataclass
from typing import Optional


@dataclass(repr=False)
class Producto:
    """A class used to represent a product

    Attributes
    ----------
    title : str
        the title of the product
    description : str | None
        the description of the product (can be None)
    image : str
        the url of the image of the product
    price : int
        product price
    shippable : bool
        if the product can be shipped
    city : str
        the city where the product is located
    link : str
        the link to the product

    Methods
    -------
    msg() -> str
        Generates the message that will be sent to the user to alert him of a new product
    """
    ident: str
    title: str
    description: Optional[str]
    image: str
    price: int
    shippable: bool
    city: str
    link: str

    def __post_init__(self) -> None:
        self._process_data()

    def _process_data(self):
        """Añade el link completo
        """

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
            description_short = self.description[:60] + '...' if len(self.description) > 60 else self.description

            return f"Producto: {self.title}. Descripción: {description_short}.\nPrecio: {self.price}€. Se envia: {envio}.\n{self.link}"

    def _update(self, item: dict):
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

        self._process_data()

    def __hash__(self) -> int:
        return hash(self.ident)
