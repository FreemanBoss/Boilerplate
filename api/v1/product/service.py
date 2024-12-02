from api.core.base.services import Service
from api.v1.product.model import Product


class ProductService(Service):
    """
    Service class for Product resource.
    """
    def __init__(self, model) -> None:
        """
        Constructor
        """
        super().__init__(model)

product_service = ProductService(Product)
