from django.db import models

from django.utils import timezone

from selene_models.models import SeleneModel, SeleneBot, Context


class Interaction(models.Model):

    selene_bot = models.ForeignKey(SeleneBot, on_delete=models.CASCADE)

    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    is_client_satified = models.BooleanField()


class MessageSent(models.Model):

    # Foreign keys -----------------------------------------
    context = models.ForeignKey(Context, on_delete=models.CASCADE)

    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)


    # ------------------------------------------------------

    message = models.TextField()

    sender = models.CharField(max_length=255)
    sent_at = models.DateTimeField()

    understood_within_context = models.BooleanField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.sent_at = timezone.now()
        super().save(*args, **kwargs)