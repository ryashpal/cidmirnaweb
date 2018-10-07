from django.db import models

from froala_editor.fields import FroalaField

class Page(models.Model):
    internal_name = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=300, blank=True, null=True, help_text="The title of the HTML page. You can leave it blank")
    content = FroalaField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.internal_name
