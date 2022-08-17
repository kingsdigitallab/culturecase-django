from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from wagtail.core.models import Page
from wagtail.search.models import Query
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.html import strip_tags
from collections import OrderedDict
from django.http import HttpResponse
import csv

from culturecase_wagtail.models import ResearchSummary


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

@login_required
def view_audit(request):
    action = ''
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'download':
            rows = get_summaries_meta()
            if rows:
                res = HttpResponse(content_type='text/csv')
                res['Content-Disposition'] = 'attachment; filename="summaries.csv"'

                writer = csv.writer(res)
                writer.writerow(rows[0].keys())
                for row in rows:
                    writer.writerow(row.values())

                return res

    context = {}
    return render(
        request,
        'culturecase_wagtail/audit.html',
        context
    )


def get_summaries_meta():
    ret = []
    for summary in ResearchSummary.objects.prefetch_related('tags'):
        summary_body = strip_tags(summary.body or '')

        ret.append(OrderedDict([
            ['page_id', summary.pk],
            ['page_slug', summary.slug],
            ['page_url', summary.get_full_url()],
            ['page_published', summary.go_live_at.strftime('%Y-%m-%d') if summary.go_live_at else ''],
            ['page_is_live', 'true' if summary.live else 'false'],
            ['tags', ', '.join([
                tag.slug
                for tag
                in summary.tags.all()
            ])],
            ['categories', ', '.join([
                cat.slug
                for cat
                in summary.categories.all()
            ])],
            ['summary_title', summary.title],
            ['article_title', summary.article_title],
            ['article_year', summary.article_year],
            ['article_source', summary.article_source],
            ['article_url', summary.article_url],
            ['article_url_open_access', summary.article_oaurl or ''],
            ['author_email', summary.article_email],
            ['summary_body', summary_body],
        ]))

    return ret
