from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'cidmirnaweb.views.home', name='home'),
    url(r'^about$', 'cidmirnaweb.views.about', name='about'),
    url(r'^submitted$', 'analyses.views.analysis_submitted', name='success'),
    url(r'^theadmin/', include(admin.site.urls)),
)
