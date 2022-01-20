from rest_framework.filters import BaseFilterBackend


class RollBackHistoryFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        params = request.query_params.get("history_id", '')
        params = params.replace('\x00', '').replace('null', '')
        if not params:
            return queryset
        queryset = queryset.filter(history_id=int(params))
        return queryset
