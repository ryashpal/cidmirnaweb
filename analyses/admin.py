from django.contrib import admin

from analyses.models import Analysis, Filename, Job

class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('email', 'analysed')


admin.site.register(Analysis, AnalysisAdmin)
admin.site.register(Filename)
admin.site.register(Job)
