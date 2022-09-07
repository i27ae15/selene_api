from django.contrib import admin

from .models import MessageSent, Interaction

admin.site.register(MessageSent)
admin.site.register(Interaction)

