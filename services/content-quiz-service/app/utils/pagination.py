"""
Pagination Utilities
Efficient database pagination with performance optimization
"""

import math
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Query
from sqlalchemy import func


def paginate_query(
    query: Query,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    Paginate a SQLAlchemy query with efficient counting
    
    Args:
        query: SQLAlchemy query to paginate
        page: Page number (1-indexed)
        page_size: Items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Dictionary with pagination information and items
    """
    # Validate and sanitize inputs
    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get total count efficiently
    total = query.count()
    
    # Calculate pagination metadata
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    
    # Get paginated items
    items = query.offset(offset).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "next_page": page + 1 if has_next else None,
        "prev_page": page - 1 if has_prev else None,
        "offset": offset
    }


def paginate_list(
    items: List[Any],
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    Paginate a Python list
    
    Args:
        items: List to paginate
        page: Page number (1-indexed)
        page_size: Items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Dictionary with pagination information and items
    """
    # Validate and sanitize inputs
    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)
    
    total = len(items)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Calculate slice indices
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # Get paginated items
    paginated_items = items[start_index:end_index]
    
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "next_page": page + 1 if has_next else None,
        "prev_page": page - 1 if has_prev else None,
        "offset": start_index
    }


class PaginationHelper:
    """Advanced pagination helper with caching and optimization"""
    
    @staticmethod
    def get_pagination_params(
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        default_page_size: int = 20,
        max_page_size: int = 100
    ) -> Dict[str, int]:
        """
        Get validated pagination parameters
        """
        return {
            "page": max(1, page or 1),
            "page_size": min(max(1, page_size or default_page_size), max_page_size)
        }
    
    @staticmethod
    def create_pagination_metadata(
        total: int,
        page: int,
        page_size: int,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive pagination metadata
        """
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        has_next = page < total_pages
        has_prev = page > 1
        
        metadata = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": page + 1 if has_next else None,
            "prev_page": page - 1 if has_prev else None,
            "first_page": 1,
            "last_page": total_pages,
            "offset": (page - 1) * page_size
        }
        
        # Add URL links if base_url provided
        if base_url:
            metadata["links"] = {
                "first": f"{base_url}?page=1&page_size={page_size}",
                "last": f"{base_url}?page={total_pages}&page_size={page_size}",
                "prev": f"{base_url}?page={page-1}&page_size={page_size}" if has_prev else None,
                "next": f"{base_url}?page={page+1}&page_size={page_size}" if has_next else None
            }
        
        return metadata
    
    @staticmethod
    def optimize_query_for_pagination(query: Query, page: int, page_size: int) -> Query:
        """
        Optimize query for pagination by adding appropriate ordering and limits
        """
        # Add default ordering if none exists
        if not query.column_descriptions:
            # If it's a simple query, add id ordering
            try:
                model = query.column_descriptions[0]['type']
                if hasattr(model, 'id'):
                    query = query.order_by(model.id)
            except (IndexError, AttributeError):
                pass
        
        return query
    
    @staticmethod
    def get_page_range(
        current_page: int,
        total_pages: int,
        max_pages: int = 10
    ) -> List[int]:
        """
        Get a range of page numbers for pagination UI
        """
        if total_pages <= max_pages:
            return list(range(1, total_pages + 1))
        
        # Calculate start and end pages
        half_max = max_pages // 2
        start_page = max(1, current_page - half_max)
        end_page = min(total_pages, start_page + max_pages - 1)
        
        # Adjust start_page if we're near the end
        if end_page - start_page + 1 < max_pages:
            start_page = max(1, end_page - max_pages + 1)
        
        return list(range(start_page, end_page + 1))


def create_cursor_pagination(
    query: Query,
    cursor: Optional[str] = None,
    limit: int = 20,
    order_field: str = "id"
) -> Dict[str, Any]:
    """
    Create cursor-based pagination for better performance on large datasets
    
    Args:
        query: SQLAlchemy query
        cursor: Base64 encoded cursor for pagination
        limit: Number of items to return
        order_field: Field to order by (must be unique and sortable)
        
    Returns:
        Dictionary with cursor pagination data
    """
    import base64
    import json
    
    # Decode cursor if provided
    if cursor:
        try:
            cursor_data = json.loads(base64.b64decode(cursor).decode())
            cursor_value = cursor_data.get("value")
            direction = cursor_data.get("direction", "next")
        except:
            cursor_value = None
            direction = "next"
    else:
        cursor_value = None
        direction = "next"
    
    # Apply cursor filter
    if cursor_value is not None:
        order_column = getattr(query.column_descriptions[0]['type'], order_field)
        if direction == "next":
            query = query.filter(order_column > cursor_value)
        else:
            query = query.filter(order_column < cursor_value)
    
    # Apply ordering and limit
    order_column = getattr(query.column_descriptions[0]['type'], order_field)
    if direction == "prev":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
    
    # Get one extra item to check if there are more
    items = query.limit(limit + 1).all()
    
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    
    # Create next cursor
    next_cursor = None
    prev_cursor = None
    
    if items and has_more:
        last_item_value = getattr(items[-1], order_field)
        next_cursor = base64.b64encode(
            json.dumps({"value": last_item_value, "direction": "next"}).encode()
        ).decode()
    
    if items and cursor_value is not None:
        first_item_value = getattr(items[0], order_field)
        prev_cursor = base64.b64encode(
            json.dumps({"value": first_item_value, "direction": "prev"}).encode()
        ).decode()
    
    return {
        "items": items,
        "has_more": has_more,
        "next_cursor": next_cursor,
        "prev_cursor": prev_cursor,
        "limit": limit
    }
