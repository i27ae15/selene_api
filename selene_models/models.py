# python
import secrets
import datetime

# django
from django.db import models
from django.utils import timezone


class SeleneModel(models.Model):

    created_at:datetime.datetime = models.DateTimeField()

    model_path = models.CharField(default='', max_length=256)

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

    created_at:datetime.datetime = models.DateTimeField()

    token:str = models.CharField(max_length=255, ) # token is used to authenticate the bot with the server
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
    
    head_id = models.IntegerField(null=True, default=None)
    parent_id = models.IntegerField(null=True, default=None)
    next_id = models.IntegerField(null=True, default=None)
    # ------------------------------------------------------
        
    block_step:bool = models.BooleanField(default=True)
    
    created_at:datetime.datetime = models.DateTimeField(null=True, default=None)
    
    do_after:dict = models.JSONField(null=True, default=dict)
    do_before:dict = models.JSONField(null=True, default=dict)
    
    name:str = models.CharField(max_length=255)

    updated_at:datetime.datetime = models.DateTimeField(null=True, default=None)
    
    random_response:bool = models.BooleanField(default=True)
    responses:dict = models.JSONField(default=dict)
    
    patterns_raw_text:str = models.TextField()

    @property
    def patterns(self) -> list:
        return self.patterns_raw_text.split(',')
    
    
    @property
    def childs(self) -> list:
        return self.selenechildnode.all()

    
    @property
    def head(self) -> 'SeleneNode':
        self.objects.get(id=self.head_id)


    @property
    def parent(self) -> 'SeleneNode':
        return self.objects.get(id=self.parent_id)
    

    @property
    def next(self) -> 'SeleneNode':
        return self.objects.get(id=self.next_id)

    

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
            print('-'*50)
            print('saving the model')
            print('-'*50)
        else:
            self.updated_at = timezone.now()

        super().save(*args, **kwargs)


