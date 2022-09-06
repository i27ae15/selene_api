# python
import secrets
import datetime

# django
from django.db import models
from django.utils import timezone


class SeleneModel(models.Model):

    created_at:datetime.datetime = models.DateTimeField(read_only=True)

    model = models.FileField(upload_to='models')

    name:str = models.CharField(max_length=255)

    updated_at:datetime.datetime = models.DateTimeField()

    data_trained_with:dict = models.JSONField()


    @property
    def active_bots(self):
        return self.selenebot_set.filter(is_active=True)


    def __str__(self):
        return self.name
    
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)


class SeleneBot(models.Model):

    # Foreign keys -----------------------------------------
    model:SeleneModel = models.ForeignKey(SeleneModel, on_delete=models.CASCADE)
    # ------------------------------------------------------

    active:bool = models.BooleanField(default=True)

    created_at:datetime.datetime = models.DateTimeField(read_only=True)

    token:str = models.CharField(max_length=255, read_only=True) # token is used to authenticate the bot with the server
    updated_at:datetime.datetime = models.DateTimeField()

    @property
    def number_of_interactions(self) -> int:
        return self.interactions_set.all().count()
    
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
            self.token = secrets.token_hex(16)
        else:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class SeleneNode(models.Model):
    # Foreign keys -----------------------------------------
    # even though this model field should not be null, the null=True, is needed since, we need first to create the SeleneNode
    # object and then, the model is created, at that point the model field got associeted with the model object
    model:SeleneModel = models.ForeignKey(SeleneModel, null=True, default=None, on_delete=models.CASCADE)
    
    head = models.ForeignKey('self', null=True, blank=True, default=None, on_delete=models.CASCADE, related_name='head')
    parent = models.ForeignKey('self', null=True, blank=True, default=None, on_delete=models.CASCADE, related_name='children')
    next = models.ForeignKey('self', null=True, blank=True, default=None, on_delete=models.CASCADE, related_name='previousnode')
    # ------------------------------------------------------
        
    block_step:bool = models.BooleanField(default=True)
    
    created_at:datetime.datetime = models.DateTimeField(read_only=True)
    
    do_after:dict = models.JSONField()
    do_before:dict = models.JSONField()
    
    name:str = models.CharField(max_length=255)

    updated_at:datetime.datetime = models.DateTimeField()
    
    random_response:bool = models.BooleanField(default=True)
    responses_raw_text:str = models.TextField()
    
    patterns_raw_text:str = models.TextField()


    @property
    def responses(self) -> list:
        return self.responses_raw_text.split(',')
    
    
    @property
    def patterns(self) -> list:
        return self.patterns_raw_text.split(',')
    
    
    @property
    def childs(self) -> list:
        return self.selenechildnode.all()
    

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)


