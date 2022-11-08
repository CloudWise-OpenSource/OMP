"""
公共分页器
"""

from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)


class PageNumberPager(PageNumberPagination):
    """ 容量分页 """
    page_size = 10
    max_page_size = 100
    page_query_param = 'page'
    page_size_query_param = 'size'


class LimitOffsetPager(LimitOffsetPagination):
    """ 偏移分页 """
    default_limit = 10
    max_limit = 100
    limit_query_param = 'limit'
    offset_query_param = 'offset'


class CursorPager(CursorPagination):
    """ 游标分页 """
    page_size = 10
    cursor_query_param = 'cursor'
