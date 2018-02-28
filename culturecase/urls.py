from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from kdl_ldap.signal_handlers import \
    register_signal_handlers as kdl_ldap_register_signal_hadlers
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from culturecase_wagtail.views import view_search

kdl_ldap_register_signal_hadlers()

admin.autodiscover()

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),


    url(r'^wagtail/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    # url(r'^search/', include(wagtailsearch_frontend_urls)),
    url(r'^search/', view_search, name='search'),
    url(r'', include(wagtail_urls)),
]

# -----------------------------------------------------------------------------
# Django Debug Toolbar URLS
# -----------------------------------------------------------------------------
try:
    if settings.DEBUG:
        import debug_toolbar
        urlpatterns += [
            url(r'^__debug__/',
                include(debug_toolbar.urls)),
        ]
except ImportError:
    pass

# -----------------------------------------------------------------------------
# Static file DEBUGGING
# -----------------------------------------------------------------------------
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import os.path

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL + 'images/',
                          document_root=os.path.join(settings.MEDIA_ROOT,
                                                     'images'))
