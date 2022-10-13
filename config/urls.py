from django.conf import settings
from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from django.views import defaults as default_views
from armour.general.views import PrivateDocView
urlpatterns = [
    path('admin/', admin.site.urls),
    path("admin/", include('loginas.urls')),
    path('', include('armour.general.urls')),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('account/', include('armour.user.urls')),
    path('company/', include('armour.company.urls')),
    path('legislation/', include('armour.legislation.urls')),
    path('media/<path:path>/', PrivateDocView.as_view(), name='get-media'),
]

if settings.DEBUG:
    #from django.conf.urls.static import static
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
                          url(r'^__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns


admin.sites.AdminSite.site_header = 'Operationarmour Admin Panel'
admin.sites.AdminSite.site_title = 'Operationarmour Admin Panel'
admin.sites.AdminSite.index_title = 'Operationarmour'