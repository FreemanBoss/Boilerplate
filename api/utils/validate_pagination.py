from typing import Optional


async def validate_pagination(params: dict = {}) -> Optional[dict]:
    """
    Validates pagination.

    Args:
        params(dict): contains query params for pagination, e.g, ({"page": 1, "limit": 10 })
    Returns:
        params(dict): the validated params.
    """
    if not params:
        params.update(
            {"limit": 10, "page": 1, "sort": "created_at", "sort_order": "desc"}
        )
    try:
        params["page"] = int(params["page"])
    except (TypeError, ValueError):
        params["page"] = 1
    if params["page"] < 1:
        params["page"] = 1

    try:
        params["limit"] = int(params["limit"])
    except (TypeError, ValueError):
        params["limit"] = 10
    if params["limit"] < 1:
        params["limit"] = 10

    if not params.get("sort") in ["created_at", "updated_at"]:
        params["sort"] = "created_at"

    if not params.get("sort_order") in ["desc", "asc"]:
        params["sort_order"] = "desc"

    return {
        "limit": params["limit"],
        "page": params["page"],
        "sort": params["sort"],
        "sort_order": params["sort_order"],
    }
