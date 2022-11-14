from django.contrib import admin
from .models import SeleneModel, SeleneBot, SeleneNode, SeleneModelVersion

admin.site.register(SeleneModel)
admin.site.register(SeleneBot)
admin.site.register(SeleneNode)
admin.site.register(SeleneModelVersion)
