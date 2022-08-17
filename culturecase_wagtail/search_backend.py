from wagtail.search.backends.elasticsearch5 import (
    Elasticsearch5SearchBackend, Elasticsearch5SearchResults
)

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

# Size of the fragments/snippets, in characters
SEARCH_HIGHLIGHTS_SIZE = 500
SEARCH_HIGHLIGHTS_LIMIT = 1
SEARCH_HIGHLIGHTS_CLASS = 'relevanssi-query-term'


class ElasticsearchSearchResultsWithHighlights(Elasticsearch5SearchResults):

    def _get_es_body(self, for_count=False, *args, **kwargs):
        '''
        Returns the json body of the search request to be sent to ES5.
        We request highlights.
        '''
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

    def _get_results_from_hits(self, hits, *args, **kwargs):
        ret = super()._get_results_from_hits(hits, *args, **kwargs)

        def get_highlights_from_hit(hit):
            ret = []
            for vals in hit['highlight'].values():
                ret.extend([v.replace('\n', '<br>') for v in vals])
            return ret

        highlights = {
            hit['fields']['pk'][0]: get_highlights_from_hit(hit)
            for hit in hits
        }

        for rec in ret:
            rec.highlights = highlights.get(str(rec.pk), [])
            yield rec


class Elasticsearch5SearchWithHighlightsBackend(Elasticsearch5SearchBackend):
    results_class = ElasticsearchSearchResultsWithHighlights


SearchBackend = Elasticsearch5SearchWithHighlightsBackend
