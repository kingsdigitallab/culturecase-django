from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from kdl_ldap.signal_handlers import \
    register_signal_handlers as kdl_ldap_register_signal_hadlers
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from culturecase_wagtail.views import view_search, view_audit
from rest_framework.compat import re_path

kdl_ldap_register_signal_hadlers()

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wagtail/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('search/', view_search, name='search'),
    path('audit/', view_audit, name='audit'),
]

# -----------------------------------------------------------------------------
# Django Debug Toolbar URLS
# -----------------------------------------------------------------------------
try:
    if settings.DEBUG:
        import debug_toolbar
        urlpatterns += [
            path(r'__debug__/',
                 include(debug_toolbar.urls)),
        ]
except ImportError:
    pass

# -----------------------------------------------------------------------------
# Static file DEBUGGING
# -----------------------------------------------------------------------------
production_debug = getattr(settings, 'PRODUCTION_DEBUG', False)
if settings.DEBUG or production_debug:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import os.path

    def test_500(request):
        raise Exception('Test 500')

    urlpatterns += [path('test/500/', test_500)]

    if production_debug:
        from django.views.static import serve
        urlpatterns += [
            re_path(
                r'^static/CACHE/(?P<path>.*)$', serve,
                {'document_root': '%s/CACHE' % settings.STATIC_ROOT}
            ),
            re_path(
                r'^media/(?P<path>.*)$', serve,
                {'document_root': '%s/media' % settings.MEDIA_ROOT}
            ),
            re_path(
                r'^static/(?P<path>.*)$', serve,
                {'document_root': settings.STATICFILES_DIRS[0]}
            )
        ]
    else:
        urlpatterns += staticfiles_urlpatterns()
        urlpatterns += static(
            settings.MEDIA_URL + 'images/',
            document_root=os.path.join(settings.MEDIA_ROOT, 'images')
        )

urlpatterns += [path('', include(wagtail_urls)), ]
