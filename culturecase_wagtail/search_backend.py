from wagtail.wagtailsearch.backends.elasticsearch5 import (
    Elasticsearch5SearchBackend, Elasticsearch5SearchResults
)
import types

'''
A search backend for wagtail.
Based on ElasticSearch5SearchBackend.
Adds an array of snippets to each record returned by <queryset>.search().
Array accessible via record.highlights.
Each snippet has the search keywords surrounded by <span class="search-term".
Only fields which name ends with 'highlightable' can be used for highlights.
Those fields must be in plain text (no XML/HTML tags).

Author: Geoffroy Noel, 2018
'''

# Size of the fragments/snippets, in charcters
SEARCH_HIGHLIGHTS_SIZE = 500
SEARCH_HIGHLIGHTS_LIMIT = 1
SEARCH_HIGHLIGHTS_CLASS = 'relevanssi-query-term'


class ElasticsearchSearchResultsWithHighlights(Elasticsearch5SearchResults):

    def _get_es_body(self, for_count=False, *args, **kwargs):
        ret = super()._get_es_body(for_count=for_count, *args, **kwargs)

        if not for_count:
            ret['highlight'] = {
                "pre_tags": [
                    "<span class='{}'>".format(SEARCH_HIGHLIGHTS_CLASS)
                ],
                "post_tags": [
                    "</span>"
                ],
                "require_field_match": False,
                "fragment_size": SEARCH_HIGHLIGHTS_SIZE,
                "no_match_size": SEARCH_HIGHLIGHTS_SIZE,
                "number_of_fragments": SEARCH_HIGHLIGHTS_LIMIT,
                "fields": {
                    "*highlightable": {
                    }
                }
            }

        return ret

    def _do_search(self, *args, **kwargs):
        ret = super()._do_search(*args, **kwargs)

        # set .highlights to each result
        for rec in ret:
            rec.highlights = self.backend.es.highlights[str(rec.pk)]

        return ret


def es_search(self, *args, **kwargs):
    self.highlights = {}

    ret = self.search_old(*args, **kwargs)

    '''
    ret = {

    hits: {
      hits: [{
        'highlight': {
          'culturecase_wagtail_richpage__body_highlightable': [
            "This research was conducted by Brian Kisida, Da
    '''

    for hit in ret['hits']['hits']:
        highlights = []
        for _, values in hit['highlight'].items():
            highlights.extend([v.replace('\n', '<br>') for v in values])
        self.highlights[str(hit['fields']['pk'][0])] = highlights

    return ret


class Elasticsearch5SearchWithHighlightsBackend(Elasticsearch5SearchBackend):
    results_class = ElasticsearchSearchResultsWithHighlights

    def __init__(self, params, *args, **kwargs):
        super().__init__(params, *args, **kwargs)

        # it's a bit of a hack to replace the method here
        # but it's more sustainable and stable than copying
        # _do_search() (see above) and patching it
        self.es.search_old = self.es.search
        self.es.search = types.MethodType(es_search, self.es)


SearchBackend = Elasticsearch5SearchWithHighlightsBackend
