# python
import secrets
import datetime

# django
from django.db import models
from django.utils import timezone

from django.db.models import FileField


class SeleneModel(models.Model):

    created_at:datetime.datetime = models.DateTimeField(null=True, default=None)

    model_path = models.CharField(default='', max_length=256)

    name:str = models.CharField(max_length=255)

    updated_at:datetime.datetime = models.DateTimeField(null=True, default=None)

    main_tags:dict = models.JSONField(default=list)
    
    token=models.CharField(max_length=255, default=secrets.token_urlsafe(16))
    
    # the only models that can go in a website are the ones that have is_main_model=True
    is_main_model:bool = models.BooleanField(default=True)


    @property
    def active_bots(self):
        return self.selenebot_set.filter(is_active=True)

    
    @property
    def nodes(self) -> 'list[SeleneNode]':
        return self.selenenode_set.all()


    def __str__(self):
        return f'{self.id} - {self.name}'
        
    
    def save(self, *args, **kwargs):
        
        if not self.pk:
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()

        return super().save(*args, **kwargs)


class SeleneBot(models.Model):

    # Foreign keys -----------------------------------------
    model:SeleneModel = models.ForeignKey(SeleneModel, on_delete=models.CASCADE)
    # ------------------------------------------------------

    active:bool = models.BooleanField(default=True)

    created_at:datetime.datetime = models.DateTimeField()
    cover_image:FileField = models.ImageField(upload_to='static/selene_chat_bots/', null=True, default=None)    
    cover_title:str = models.CharField(max_length=30, default='')
    cover_description:str = models.CharField(max_length=256, default='')
    
    default_response_on_webhook_failure:str = models.CharField(max_length=256, default='There was a problem with the request. Please try again later.')

    token:str = models.CharField(max_length=255) # token is used to authenticate the bot with the server
    
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
    
    head_id:int = models.IntegerField(null=True, default=None)
    # ------------------------------------------------------
        
    block_step:bool = models.BooleanField(default=True)
    
    created_at:datetime.datetime = models.DateTimeField(null=True, default=None)
    
    do_after:dict = models.JSONField(null=True, default=dict)
    do_before:dict = models.JSONField(null=True, default=dict)
    
    """
        do_afterlist[dict]; do_beforelist[dict];
        
        dict = "functions_to_call": [{
                    "name": "send_email",
                    "parameters": {
                        "send_to": "andresruse18@gmail.com",
                        "subject": "New conversation initiated",
                        "html": "<h1>f'A new conversation has initated with Selene'<h1>",
                    }
                    }]

    
    """

    end_steps:bool = models.BooleanField(default=False)

    tokenized_name:str = models.CharField(max_length=255)
    next_node_on_option :dict = models.JSONField(default=dict)
    """
        this will be a dictionary with the following structure:

        {
            'option[str]': node_name[str]  
        }

        So, this dicitonary will only be used when there are options on the response object
    """

    patterns:list = models.JSONField(default=list)

    random_response:bool = models.BooleanField(default=True)
    responses:list = models.JSONField(default=list)
    response_time_wait:int = models.IntegerField(default=0)
    
    updated_at:datetime.datetime = models.DateTimeField(null=True, default=None)

    
    @property
    def name(self) -> str:
        return self.tokenized_name.split('s--s')[1]
    
    
    @property
    def childs(self) -> list:
        return self.selenechildnode.all()

    
    @property
    def head(self) -> 'SeleneNode':
        node = None
        try: node = SeleneNode.objects.get(id=self.head_id)
        except: pass
        return node
    

    def next(self, option:str='next_node') -> 'SeleneNode':
        node_name:str = self.next_node_on_option.get(option)

        if node_name:
            return SeleneNode.objects.get(tokenized_name=node_name)
        else:
            return None
    
    
    def set_default_next_node(self, node_name:str):
        self.next_node_on_option['next_node'] = node_name
        self.save()


    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()

        super().save(*args, **kwargs)


    def __str__(self) -> str:
        return f'{self.id} - {self.tokenized_name}'

