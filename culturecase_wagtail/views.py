from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.search.models import Query
from django.conf import settings
from django.core.paginator import Paginator


def view_search(request):
    # Search
    search_query = request.GET.get('s', None)
    if search_query:
        search_results = Page.objects.live().search(
            search_query
        )
        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = Page.objects.none()

    return render_page_list(
        request,
        search_results,
        'culturecase_wagtail/search_results.html',
        {'search_query': search_query}
    )


def render_page_list(request, search_results, template_name, context=None):
    page_number = request.GET.get('p', 1)

    # replicate legacy site trimming to 50 result items
    page_query_set = search_results[:settings.ITEMS_PER_RESULT]

    # paginate
    paginator = Paginator(page_query_set, settings.ITEMS_PER_PAGE)
    if context is None:
        context = {}
    context['result_page'] = paginator.page(int(page_number))

    # Render template
    ret = render(request, template_name, context)

    return ret
