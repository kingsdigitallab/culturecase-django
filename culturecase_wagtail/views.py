from django.shortcuts import render

from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch.models import Query
from django.conf import settings
from django.core.paginator import Paginator


def view_search(request):
    # Search
    search_query = request.GET.get('s', None)
    if search_query:
        search_results = Page.objects.live().search(search_query)[:50]
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


def render_page_list(request, page_query_set, template_name, context=None):
    page_number = request.GET.get('p', 1)

    # paginate
    paginator = Paginator(page_query_set, settings.ITEMS_PER_PAGE)
    if context is None:
        context = {}
    context['result_page'] = paginator.page(int(page_number))

    # Render template
    return render(request, template_name, context)
