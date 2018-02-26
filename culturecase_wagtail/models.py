from __future__ import unicode_literals
# from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from django.db.models.fields import BooleanField, CharField


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

    def get_shortest_title(self):
        return self.short_title or self.title


class HomePage(RichPage):
    pass


class ResearchPage(RichPage):
    pass
