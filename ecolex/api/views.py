import re
from django.conf import settings
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin#, RetrieveModelMixin
from ecolex.xviews import SearchViewMixin
from ecolex.xsearch import Searcher
from . import serializers
from . import pagination


class ApiViewMixin(object):
    def perform_authentication(self, request):
        # skip authentication, we haven't any
        pass


# TODO: get_queryset is being called twice. wut?

class SearchResultViewSet(ApiViewMixin,
                          SearchViewMixin,
                          ListModelMixin,
                          GenericViewSet):
    serializer_class = serializers.SearchResultSerializer
    pagination_class = pagination.SolrQuerysetPagination

    def get_queryset(self, *args, **kwargs):
        self._prepare(self.request.query_params)
        results = self.search()
        return results


class BaseFacetViewSet(ApiViewMixin,
                       SearchViewMixin,
                       ListModelMixin,
                       GenericViewSet):
    serializer_class = serializers.SearchFacetSerializer
    pagination_class = pagination.SolrFacetPagination

    # must be defined by subclasses
    field = None

    def get_queryset(self, *args, **kwargs):
        if not self.form.is_valid():
            return []

        field = self.field
        data = self.form.cleaned_data
        language = self.form.data.get('lang')

        if not language:
            language = settings.LANGUAGE_CODE
        else:
            if language not in dict(settings.LANGUAGES).keys():
                return []

        searcher = Searcher(data, language=language)
        response = searcher.search()

        facet = {
            'field': field,
            # fetch all facet values and do search and pagination locally
            'limit': -1,
        }

        items = searcher.get_facets([field])[field]

        search = self.request.query_params.get('search', '').strip()
        if search:
            search = Searcher._normalize_facet(search)
            terms = [t for t in search.split(" ") if t]
            def _matches(item):
                return all(map(lambda t: re.search(r'\b%s' % t, item, re.I),
                               terms))

            items = [item for item in items if _matches(item['id'])]

        return items
