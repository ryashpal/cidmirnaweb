from django.contrib import admin

# Register your models here.

from .models import Entities
from .models import Mirna
from .models import MirnaEntity

admin.site.register(Entities)
admin.site.register(Mirna)
admin.site.register(MirnaEntity)
