from __future__ import unicode_literals
# from django.db import models

from wagtail.wagtailsearch import index
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from django.db.models.fields import BooleanField, CharField, URLField,\
    EmailField, IntegerField
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from django.http import Http404
from taggit.models import TaggedItemBase, Tag as TaggitTag
from modelcluster.fields import ParentalKey
from wagtail.wagtailsnippets.models import register_snippet
from modelcluster.contrib.taggit import ClusterTaggableManager


class RichPage(Page):
    body = RichTextField(blank=True)

    show_kcl_logo = BooleanField(
        'Show KCL Logo',
        blank=False,
        null=False,
        default=False)

    short_title = CharField(
        'Short title',
        max_length=32,
        blank=True,
        null=True,
        default=None,
        help_text='A word or two that can be included in the main menu'
    )

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('show_kcl_logo'),
            FieldPanel('short_title')
        ],
            heading='Presentation',
            classname='collapsible'
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        # index.FilterField('date'),
    ]

    def get_shortest_title(self):
        return self.short_title or self.title


class HomePage(RoutablePageMixin, RichPage):

    def get_summaries(self):
        return ArticleSummaryPage.objects.live()

    @route(r'^research-tags/(?P<slug>[-\w]+)/$')
    def get_summaries_from_tag(self, request, slug, *args, **kwargs):

        tag = ResearchTag.objects.filter(slug=slug).first()
        if not tag:
            raise Http404

        summaries = self.get_summaries().filter(
            tags__slug=slug
        ).order_by('-go_live_at')
        from .views import render_page_list
        return render_page_list(
            request,
            summaries,
            'culturecase_wagtail/tag_results.html',
            {'search_tag': tag}
        )


class ResearchPage(RoutablePageMixin, RichPage):

    def get_summaries(self):
        return ArticleSummaryPage.objects.descendant_of(self).live()

    @route(r'^(?P<year>\d{4,4})/(?P<month>\d{2,2})/(?P<slug>[-\w]+)/$')
    def get_summary_from_slug(
            self, request, year, month, slug, *args, **kwargs):
        summary = self.get_summaries().filter(slug=slug).first()
        if not summary:
            raise Http404

        return Page.serve(summary, request, *args, **kwargs)


class ResearchCategoryHomePage(RoutablePageMixin, RichPage):

    def get_summaries(self):
        return ArticleSummaryPage.objects.live()

    @route(r'^(?P<slug>[-\w]+)/$')
    def get_summary_from_category(
            self, request, slug, *args, **kwargs):

        category = ResearchCategoryPage.objects.filter(slug=slug).first()
        if not category:
            raise Http404

        summaries = self.get_summaries().filter(
            # tags__slug=slug
        ).order_by('-go_live_at')
        from .views import render_page_list
        return render_page_list(
            request,
            summaries,
            'culturecase_wagtail/category_results.html',
            {'search_category': category}
        )


class ResearchCategoryPage(RichPage):

    def get_url_parts(self, *args, **kwargs):
        '''Flatten the path, ignore the parent categories.
        to match legacy wordpress site.
        '''
        ret = list(super(RichPage, self).get_url_parts(*args, **kwargs))

        # e.g. /research-category/this-category-slug/
        category_home = ResearchCategoryHomePage.objects.first()
        category_home_parts = category_home.get_url_parts()

        ret[2] = '{}{}'.format(
            category_home_parts[2],
            self.slug
        )

        return ret


class ArticleSummaryPage(RichPage):

    article_title = CharField(
        'Article title', max_length=255,
        blank=True,
        null=True,
        default=None,
        help_text='The title of the research paper',
    )
    article_authors = CharField(
        'Article authors', max_length=255,
        blank=True,
        null=True,
        default=None,
        help_text='The names of one or more authors separated by commas'
    )
    article_year = IntegerField(
        'Article year',
        blank=True,
        null=True,
        default=None,
        help_text='Year of publication'
    )
    article_source = CharField(
        'Article source', max_length=255,
        blank=True,
        null=True,
        default=None,
        help_text='Source reference'
    )
    article_url = URLField(
        'Article link',
        blank=True,
        null=True,
        default=None,
        help_text='Reference URL (including the http:// part)'
    )
    article_oaurl = URLField(
        'Article open access link',
        blank=True,
        null=True,
        default=None,
        help_text='Open access URL (including the http:// part)'
    )
    article_email = EmailField(
        'Author email',
        blank=True,
        null=True,
        default=None,
        help_text='Contact email address for the lead author'
    )

    tags = ClusterTaggableManager(
        through='culturecase_wagtail.ArticleSummaryPageResearchTag',
        blank=True
    )

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        MultiFieldPanel([
            FieldPanel('article_title'),
            FieldPanel('article_authors'),
            FieldPanel('article_year'),
            FieldPanel('article_source'),
            FieldPanel('article_url'),
            FieldPanel('article_oaurl'),
            FieldPanel('article_email'),
        ],
            heading='Article details',
            classname='collapsible'
        ),
    ]

    def get_url_parts(self, *args, **kwargs):
        '''We insert the year and month into the webpath
        /research/2018/02/SLUG'''
        ret = list(super(RichPage, self).get_url_parts(*args, **kwargs))

        parent = self.get_parent()
        parent_parts = parent.get_url_parts()

        ret[2] = '{}{:02d}/{:02d}/{}'.format(
            parent_parts[2],
            self.go_live_at.year,
            self.go_live_at.month,
            self.slug
        )
        return ret


class ArticleSummaryPageResearchTag(TaggedItemBase):
    content_object = ParentalKey(
        'ArticleSummaryPage',
        related_name='research_tags'
    )


@register_snippet
class ResearchTag(TaggitTag):
    class Meta:
        proxy = True
