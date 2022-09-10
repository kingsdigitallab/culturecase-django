from django import template
from culturecase_wagtail.models import ResearchSummary, Menu
from wagtail.core.models import Site
from django.utils.safestring import mark_safe
from wagtail.core.templatetags.wagtailcore_tags import pageurl


register = template.Library()


@register.simple_tag()
def get_latest_research_articles():
    # see AC-129
    # field = '-go_live_at'
    field = '-first_published_at'
    ret = ResearchSummary.objects.live().filter(
        first_published_at__isnull=False
    ).order_by(field)[:5]

    return ret


@register.simple_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    ret = None

    site = getattr(context['request'], 'site', None)
    if not site:
        # no reference, let's get ANY site
        site = Site.objects.first()

    if site:
        ret = site.root_page

    return ret


def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


@register.inclusion_tag(
    'culturecase_wagtail/menu_top.html', takes_context=True)
def kdl_menu_top(context, menu_slug, active_page_slug=None):
    return kdl_menu(context, menu_slug=menu_slug,
                    active_page_slug=active_page_slug)


@register.inclusion_tag(
    'culturecase_wagtail/menu_top_second.html', takes_context=True)
def kdl_menu_top_second(context, menu_slug, active_page_slug=None):
    return kdl_menu(context, menu_slug=menu_slug,
                    active_page_slug=active_page_slug)


@register.inclusion_tag(
    'culturecase_wagtail/menu_sub.html', takes_context=True)
def kdl_menu_sub(context, menu_slug, active_page_slug=None):
    return kdl_menu(context, menu_slug=menu_slug,
                    active_page_slug=active_page_slug)


def kdl_menu(context, menu_slug, active_page_slug=None):
    '''
    menu_root: the menu root
    calling_page = the requested page
    active_page_slug = slug of a page that should be selected in the menu
    '''
    request = context.get('request', {})
    menuitems = []
    if request:
        # menuitems = menu_slug.get_children().live().in_menu()
        menus = Menu.objects.filter(slug__in=menu_slug.split(','))

        for menu in menus:
            for menuitem in menu.menu_items.all():
                menuitem = menuitem.page
                menuitem.show_dropdown = has_menu_children(menuitem)
                # We don't directly check if calling_page is None since the
                # template engine can pass an empty string to calling_page
                # if the variable passed as calling_page does not exist.
                item_path = pageurl(context, menuitem)
                menuitem.active = menuitem.slug == active_page_slug or (
                    request.path.startswith(item_path)
                )
                menuitems.append(menuitem)

    from culturecase_wagtail.context_processors import\
        settings as settings_processor

    ret = {
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': request,
    }
    ret.update(settings_processor(request))

    return ret


# Retrieves all live pages which are children of the calling page
# for standard index listing
@register.inclusion_tag(
    'demo/tags/standard_index_listing.html',
    takes_context=True
)
def standard_index_listing(context, calling_page):
    pages = calling_page.get_children().live()
    return {
        'pages': pages,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.simple_tag(takes_context=True)
def update_qs(context, name, value):
    from urllib import parse
    params = context.request.GET.dict()
    params[name] = value
    ret = '?{}'.format(parse.urlencode(params))
    return mark_safe(ret)


@register.filter(name='clean_result')
def clean_result(value):
    ret = value or ''
    import re
    ret = re.sub(r'(<br/?>\s*)+', '<br>', ret)
    return ret
