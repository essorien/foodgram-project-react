from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    default_page_size = 6
    page_size_query_param = 'limit'
