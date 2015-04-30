from django.contrib import admin

from analyses.models import Analysis, Filename, Job

admin.site.register(Analysis)
admin.site.register(Filename)
admin.site.register(Job)
