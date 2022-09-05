# python
import secrets
import datetime

# django
from django.db import models
from django.utils import timezone



class SeleneModel(models.Model):

    created_at = models.DateTimeField()

    model = models.FileField(upload_to='models')

    name = models.CharField(max_length=255)

    updated_at = models.DateTimeField()

    data_trained_with = models.JSONField() # should this be a file field?

    @property
    def active_bots(self):
        return self.selenebot_set.filter(is_active=True)

    def __str__(self):
        return self.name


class SeleneBot(models.Model):

    # Foreign keys -----------------------------------------
    model = models.ForeignKey(SeleneModel, on_delete=models.CASCADE)
    # ------------------------------------------------------

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField()

    token = models.CharField(max_length=255)

    @property
    def number_of_interactions(self) -> int:
        return self.interactions_set.all().count()
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = secrets.token_hex(16)
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class SeleneNode(models.Model):
    # Foreign keys -----------------------------------------
    model = models.ForeignKey(SeleneModel, on_delete=models.CASCADE)
    # ------------------------------------------------------

    data_trained_with:dict = models.JSONField()
    do_after:dict = models.JSONField()
    do_before:dict = models.JSONField()
    
    name:str = models.CharField(max_length=255)

    created_at:datetime.datetime = models.DateTimeField()
    updated_at:datetime.datetime = models.DateTimeField()
    
    responses_raw_text:str = models.TextField()
    random_response:bool = models.BooleanField(default=True)
    

    @property
    def responses(self) -> list:
        return self.responses_raw_text.split(',')
    
    @
    

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)



class SeleneChildNode(models.Model):
    # Foreign keys -----------------------------------------
    model = models.ForeignKey(SeleneModel, on_delete=models.CASCADE)
    # ------------------------------------------------------
