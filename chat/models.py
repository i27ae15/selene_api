import datetime
from django.db import models

from django.utils import timezone

from selene_models.models import SeleneModel, SeleneBot, SeleneNode


class Interaction(models.Model):

    selene_bot:SeleneBot = models.ForeignKey(SeleneBot, on_delete=models.CASCADE)

    started_at:datetime.datetime = models.DateTimeField()
    finished_at:datetime.datetime = models.DateTimeField(null=True, default=None)
    is_client_satified:bool = models.BooleanField(null=True, default=None)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.started_at = timezone.now()
        return super(Interaction, self).save(*args, **kwargs)
    
    
    def __str__(self) -> str:
        return f'{self.pk} - {self.selene_bot.model.name} - {self.started_at}'


class MessageSent(models.Model):

    # Foreign keys -----------------------------------------
    node:SeleneNode = models.ForeignKey(SeleneNode, on_delete=models.CASCADE)

    interaction:Interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)

    # ------------------------------------------------------

    message_object:dict = models.JSONField(default=dict)

    sender:str = models.CharField(max_length=255)
    sent_at:datetime.datetime = models.DateTimeField()

    understood_within_context:bool = models.BooleanField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.sent_at = timezone.now()
        super().save(*args, **kwargs)