from api.core.base.services import Service
from api.v1.like.model import (
    PhotoLike,
    PhotoCommentLike,
    ReelCommentLike,
    ReelLike,
    ProductCommentLike,
    ProductLike
    
)


class PhotoLikeService(Service):
    """
    Service class for photo like.
    """
    def __init__(self, model) -> None:
        super().__init__(model)\


class PhotoCommentLikeService(Service):
    """
    Service class for photo comment like.
    """
    def __init__(self, model) -> None:
        super().__init__(model)

class ReelLikeService(Service):
    """
    Service class for reels like.
    """
    def __init__(self, model) -> None:
        super().__init__(model)\


class ReelCommentLikeService(Service):
    """
    Service class for reels comment like.
    """
    def __init__(self, model) -> None:
        super().__init__(model)

class ProductLikeService(Service):
    """
    Service class for products like.
    """
    def __init__(self, model) -> None:
        super().__init__(model)\


class ProductCommentLikeService(Service):
    """
    Service class for product comment like.
    """
    def __init__(self, model) -> None:
        super().__init__(model)



photo_like_service = PhotoLikeService(PhotoLike)
photo_comment_like_service = PhotoCommentLikeService(PhotoCommentLike)

product_like_service = ProductLikeService(ProductLike)
product_comment_like_service = ProductCommentLikeService(ProductCommentLike)

reel_like_service = ReelLikeService(ReelLike)
reel_comment_like_service = ReelCommentLikeService(ReelCommentLike)
