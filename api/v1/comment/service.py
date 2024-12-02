from api.core.base.services import Service
from api.v1.comment.model import (
    ReelComment,
    PhotoComment,
    ProductComment,
)


class ReelCommentService(Service):
    """
    Service class for reels comment.
    """
    def __init__(self, model) -> None:
        super().__init__(model)
        
class ProductCommentService(Service):
    """
    Service class for product comment.
    """
    def __init__(self, model) -> None:
        super().__init__(model)
        
class PhotoCommentService(Service):
    """
    Service class for photo comment.
    """
    def __init__(self, model) -> None:
        super().__init__(model)

reel_comment_service = ReelCommentService(ReelComment)
photo_comment_service = PhotoCommentService(PhotoComment)
product_comment_service = PhotoCommentService(ProductComment)
