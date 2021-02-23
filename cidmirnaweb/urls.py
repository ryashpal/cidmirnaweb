"""

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from bioinformatics import views
from analyses import views as analysesviews
from cidmirnaweb import views as cidmirnawebviews
from linc2function import views as linc2functionviews
from crc_finder import views as crcfinderviews

urlpatterns = [
    url(r'^theadmin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^cidmirna$', analysesviews.cidmirna, name='cidmirna'),
    url(r'^datasource_comparison$', linc2functionviews.datasource_comparison, name='datasource_comparison'),
    url(r'^linc2function$', linc2functionviews.linc2function, name='linc2function'),
    url(r'^linc2function/data_selection$', linc2functionviews.linc2function_data_selection, name='linc2function_data_selection'),
    url(r'^linc2function/feature_tree$', linc2functionviews.linc2function_feature_tree, name='linc2flinc2function_feature_treeunction'),
    url(r'^crc_finder$', crcfinderviews.get_crc, name='crc_finder'),
    url(r'^crc$', crcfinderviews.home, name='crc_finder_home'),
    url(r'^novel_crcs$', crcfinderviews.get_novel_crc, name='novel_crcs'),
    url(r'^download$', cidmirnawebviews.download, name='download'),
    url(r'^about$', cidmirnawebviews.about, name='about'),
    url(r'^submitted$', analysesviews.analysis_submitted, name='success'),

    url(r'^people$', views.people, name='people'),
    url(r'^research$', views.research, name='research'),
    url(r'^publications$', views.publications, name='publications'),
    url(r'^teaching$', views.teaching, name='teaching'),
    url(r'^news$', views.news, name='news'),
    url(r'^froala_editor/', include('froala_editor.urls')),
    path('download_csv/<str:csv_file>', views.send_file, name='send_file'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
