'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''
from __future__ import unicode_literals
from django.db import models

from wagtail.wagtailsearch import index
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel,\
    PageChooserPanel, InlinePanel
from django.db.models.fields import BooleanField, CharField, URLField,\
    EmailField, IntegerField
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from django.http import Http404
from taggit.models import TaggedItemBase, Tag as TaggitTag
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.wagtailsnippets.models import register_snippet
from modelcluster.contrib.taggit import ClusterTaggableManager
from django import forms
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from django.shortcuts import render
from django.http.response import HttpResponseRedirect, HttpResponse

'''
Page and Snippet classes:

PAGES

HomePage                       /
    StaticPage                 /SLUG/
    ResearchSummariesTree      /research/
        ResearchSummary        /research/YYYY/MM/SUMMARY-SLUG/
    CategorisedSummariesPage   /contents/
    ResearchCategoriesTree     /research-category/
        ResearchCategory       /research-category/CATEGORY-SLUG/
                               /research-tags/TAG-SLUG/

SNIPPETS
    ResearchTag
'''

# ===================================================================
#                            STATIC PAGES
# ===================================================================


class RichPage(Page):
    '''
    The base class for all other pages
    '''
    is_creatable = False

    body = RichTextField(blank=True)

    show_kcl_logo = BooleanField(
        'Show KCL Logo',
        blank=False,
        null=False,
        default=False
    )

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

    def body_highlightable(self):
        from django.utils.html import strip_tags
        return strip_tags((self.body or ''))

    search_fields = Page.search_fields + [
        # we don't index body directly, Elasticsearch isn't XML aware
        # e.g. search 'strong' returns pages with <strong> and highlighting
        # tags generate invalid XML e.g. <<hl>strong</hl>>
        index.SearchField('body_highlightable'),
        # index.FilterField('date'),
    ]

    def get_shortest_title(self):
        return self.short_title or self.title

    def get_related_categories(self):
        '''
        Find the ResearchCategory which has the same slug as this page
        and return all its live (& in menu) children (ResearchCategory).
        '''
        ret = []

        category = ResearchCategory.objects.filter(slug=self.slug).first()
        if category:
            ret = ResearchCategory.objects.descendant_of(
                category).live().in_menu()

        return ret


class StaticPage(RichPage):
    pass


# ===================================================================
#                            Home Page
# ===================================================================


class AbstractSlide(models.Model):
    title = models.CharField(max_length=128)
    caption = models.TextField()
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    related_page = models.ForeignKey(
        'RichPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    background_color = models.CharField(
        max_length=32, null=True, blank=True,
        help_text='leave blank for transparent/white background. Or use '
        'a css color code, e.g. black or #101010 .',
        default=None
    )
    text_color = models.CharField(
        max_length=32, null=True, blank=True,
        help_text='leave blank for black color. Or use '
        'a css color code, e.g. white or #ffffff .',
        default=None
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('caption'),
        ImageChooserPanel('image'),
        PageChooserPanel('related_page'),
        FieldPanel('background_color'),
        FieldPanel('text_color'),
    ]

    class Meta:
        abstract = True


class HomePageSlide(Orderable, AbstractSlide):
    page = ParentalKey('HomePage', related_name='slides')


class NewsLetterForm(forms.Form):
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64)
    organisation = forms.CharField(max_length=64, required=False)
    email = forms.EmailField()


class HomePage(RoutablePageMixin, RichPage):
    parent_page_types = []

    content_panels = RichPage.content_panels + [
        InlinePanel('slides', label="Slides"),
    ]

    def get_summaries(self):
        return ResearchSummary.objects.live()

    @route(r'^research-tags/(?P<slug>[-\w]+)/$')
    def serve_summaries_from_tag(self, request, slug, *args, **kwargs):

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

    @route(r'^newsletter/$', name='newsletter')
    def serve_newsletter(self, request, *args, **kwargs):

        if request.method == 'POST':
            form = NewsLetterForm(request.POST)
            if form.is_valid():
                # TODO: error management!

                # we sign them up with mailchimp API
                from .utils import signup_to_newsletter

                signup_to_newsletter({
                    'EMAIL': form.cleaned_data['email'],
                    'FNAME': form.cleaned_data['first_name'],
                    'LNAME': form.cleaned_data['last_name'],
                    'ORG': form.cleaned_data['organisation'],
                })

                # then redirect to thank you page
                return HttpResponseRedirect(
                    '/' + self.reverse_subpage('newsletter_signed')
                )
        else:
            form = NewsLetterForm()

        return render(
            request,
            'culturecase_wagtail/newsletter.html',
            {
                'page': StaticPage(title='Sign up to our newsletter'),
                'newsletter_form': form,
            }
        )

    @route(r'^newsletter-signed/$', name='newsletter_signed')
    def serve_newsletter_signed(self, request, *args, **kwargs):

        return render(
            request,
            'culturecase_wagtail/newsletter_signed.html',
            {
                'page': StaticPage(title='Signed up to newsletter'),
            }
        )

# ===================================================================
#                            FAQs
# ===================================================================


class FAQsPage(RichPage):
    subpage_types = ['QuestionAndAnswer']

    template = 'culturecase_wagtail/faqs.html'

    class Meta:
        verbose_name = "FAQs Page"

    def get_questions(self):
        # TODO: returns only questions below this page
        return QuestionAndAnswer.objects.filter().live()


class QuestionAndAnswer(RichPage):
    '''
    We use a sub page rather than a snippet, for two reasons:
    We need an order and wagtail has no way to reorder snippets by default.
    It's convenient to have them under the FAQsPage directly so the
    user doesn't have to move back and forth between Page tree and snippets.
    '''

    parent_types = ['FAQsPage']

# ===================================================================
#                    RESEARCH ARTICLE SUMMARIES
# ===================================================================


class ResearchSummary(RichPage):
    '''
    A summary of a research article / paper
    '''

    subpage_types = []
    parent_page_types = ['ResearchSummariesTree']

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
        through='culturecase_wagtail.ResearchSummaryResearchTag',
        blank=True
    )

    categories = ParentalManyToManyField(
        'ResearchCategory',
        blank=True,
        related_name='research_summaries'
    )

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
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

    class Meta:
        ordering = ['-go_live_at']

    def get_template(self, request, *args, **kwargs):
        ret = super(ResearchSummary, self).get_template(
            request, *args, **kwargs
        )
        if request.GET.get('format') == 'print':
            ret = ret.replace('.html', '_print.html')

        return ret

    def serve(self, request, *args, **kwargs):

        if request.GET.get('format') == 'pdf':
            # get the print format HTML
            print_url = request.build_absolute_uri(self.url + '?format=print')
            import weasyprint
            # process it with weasyprint
            doc = weasyprint.HTML(print_url)
            # convert to PDF and get it as a string
            pdf_string = doc.write_pdf()
            # prepare http response
            ret = HttpResponse(pdf_string, content_type='application/pdf')

            ret['Content-Disposition'] = 'attachment; filename="' + \
                self.slug + '.pdf"'
        else:
            ret = RichPage.serve(self, request, *args, **kwargs)

        return ret

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

    def get_breadcrumb(self):
        '''returns one categories and its parent categories.
        We don't show all applied categories.
        Only one (arbitrary and) deep category and all its parent categories.

        E.g.
        Home > Impact > Economic impacts of arts and culture
        '''
        ret = []

        # find first deepest category (among all applied)
        deepest_category = None

        for cat in self.categories.all():
            if deepest_category is None or cat.depth > deepest_category.depth:
                deepest_category = cat

        # add all its ancestor categories (even if not applied)
        if deepest_category:
            cat = deepest_category
            while True:
                ret.append(cat)
                parent = cat.get_parent().specific
                if isinstance(parent, ResearchCategory):
                    cat = parent
                else:
                    break

        return ret[::-1]


class ResearchSummariesTree(RoutablePageMixin, RichPage):
    '''
    The ancestor/root of all the ResearchSummary.
    Not exposed on the site, only there to give a root webpath to summaries.
    '''

    subpage_types = ['ResearchSummary']

    def get_summaries(self):
        return ResearchSummary.objects.descendant_of(self).live()

    @route(r'^(?P<year>\d{4,4})/(?P<month>\d{2,2})/(?P<slug>[-\w]+)/$')
    def get_summary_from_slug(
            self, request, year, month, slug, *args, **kwargs):
        summary = self.get_summaries().filter(slug=slug).first()
        if not summary:
            raise Http404

        return ResearchSummary.serve(summary, request, *args, **kwargs)

# ===================================================================
#                              TAGS
# ===================================================================


class ResearchSummaryResearchTag(TaggedItemBase):
    content_object = ParentalKey(
        'ResearchSummary',
        related_name='research_tags'
    )


@register_snippet
class ResearchTag(TaggitTag, index.Indexed):
    class Meta:
        proxy = True

    search_fields = [
        index.SearchField('slug', partial_match=True),
        index.SearchField('name', partial_match=True),
    ]

# ===================================================================
#                          CATEGORIES
# ===================================================================


class ResearchCategory(RichPage):
    '''
    A research category that can be applied to the article summary pages.
    Categories can be organised as a tree.
    Root of the tree is a ResearchCategoriesTree
    '''

    subpage_types = ['ResearchCategory']
    parent_types = ['ResearchCategoriesTree', 'ResearchCategory']

    def get_url_parts(self, *args, **kwargs):
        '''Flatten the path, ignore the parent categories.
        to match legacy wordpress site.
        '''
        ret = list(super(RichPage, self).get_url_parts(*args, **kwargs))

        # e.g. /research-category/this-category-slug/
        category_home = ResearchCategoriesTree.objects.first()
        category_home_parts = category_home.get_url_parts()

        ret[2] = '{}{}'.format(
            category_home_parts[2],
            self.slug
        )

        return ret

    def get_summaries(self):
        # Following the M2MPrentalKey in reverse won't return the
        # summaries according to the summaries.ordering...
        # So we have to do it here ourselves.
        # TODO: optimise this page, it's a bit slower than the rest (1.3s)
        return self.research_summaries.live().order_by('-go_live_at')


class ResearchCategoriesTree(RoutablePageMixin, RichPage):
    '''
    The ancestor/root of the tree of categories (ResearchCategory).
    Not exposed on the site, only there to give a root webpath to categories.
    '''
    subpage_types = ['ResearchCategory']

    def get_summaries(self):
        return ResearchSummary.objects.live()

    @route(r'^(?P<slug>[-\w]+)/$')
    def get_summaries_from_category(
            self, request, slug, *args, **kwargs):

        category = ResearchCategory.objects.filter(slug=slug).first()
        if not category:
            raise Http404

        summaries = self.get_summaries().filter(
            categories__id=category.id
        ).order_by('-go_live_at')

        from .views import render_page_list

        return render_page_list(
            request,
            summaries,
            'culturecase_wagtail/category_results.html',
            {
                'search_category': category,
                # Make sure parent category is highlighted in the menu.
                'menu_slug': category.get_parent().slug
            }
        )


class CategorisedSummariesPage(RichPage):
    '''
    The web page that lists all categories and articles beneath them.
    '''

    def get_context(self, *args, **kwargs):
        ret = super(
            CategorisedSummariesPage,
            self).get_context(
            *
            args,
            **kwargs)

        root = ResearchCategoriesTree.objects.first()
        ret['categories'] = []

        if root:
            ret['categories'] = root.get_children()

        return ret
