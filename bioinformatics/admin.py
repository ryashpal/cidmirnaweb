from django.contrib import admin

from bioinformatics.models import Page

class PageAdmin(admin.ModelAdmin):
    list_display = ('internal_name', 'title', 'modified')


admin.site.register(Page)
