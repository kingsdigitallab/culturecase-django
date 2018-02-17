from __future__ import unicode_literals
from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class RichPage(Page):
    body = RichTextField(blank=True)
    # id of the imported wordpress page
    # so we just update the page each time after the initial import
    legacyid = models.CharField(
        'Legacy ID',
        max_length=32,
        blank=True,
        null=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]


class HomePage(RichPage):
    pass
