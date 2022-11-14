# python
import secrets
import datetime

# django
from django.db import models
from django.utils import timezone
from django.db.models import QuerySet

from django.db.models import FileField


class SeleneModel(models.Model):

    name:str = models.CharField(max_length=255)

    main_tags:dict = models.JSONField(default=list)
    
    token=models.CharField(max_length=255)
    
    # logs fields

    created_at:datetime.datetime = models.DateTimeField()
    updated_at:datetime.datetime = models.DateTimeField(null=True, blank=True, default=None)


    @property
    def active_bots(self):
        return self.selenebot_set.filter(is_active=True)


    @property
    def current_version(self) -> 'SeleneModelVersion':
        return self.selenemodelversion_set.get(is_current_version=True)


    @property
    def last_version(self) -> 'SeleneModelVersion':
        return self.selenemodelversion_set.order_by('-id').first()

    
    @property
    def nodes(self) -> 'QuerySet[SeleneNode]':
        """
            Returning the nodes that are attached to the main version of the model
        """
        return self.current_version.nodes()


    def __str__(self):
        return f'{self.id} - {self.name}'
        
    
    def save(self, *args, **kwargs):
        
        if not self.pk:
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()

        return super().save(*args, **kwargs)


class SeleneModelVersion(models.Model):
    version = models.CharField(max_length=255, default='1.0.0')
    model = models.ForeignKey(SeleneModel, on_delete=models.CASCADE)

    # the only models that can go in a website are the ones that have is_current_version=True
    is_current_version:bool = models.BooleanField(default=True)

    created_at:datetime.datetime = models.DateTimeField()
    updated_at:datetime.datetime = models.DateTimeField(null=True, blank=True, default=None)

    version_model_path = models.CharField(default='', max_length=256)
    

    def nodes(self) -> QuerySet['SeleneNode']:
        return self.selenenode_set.all()


    def difference_of_nodes(self, other_version: 'SeleneModelVersion') -> 'QuerySet[SeleneModelVersion]':
        """
            Returns the difference of nodes between this version and the other one.
        """
        return list(self.nodes().difference(other_version.nodes()))

    
    def save(self, *args, **kwargs):
        
        if not self.pk:
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()

        return super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.id} - {self.version}'


class SeleneBot(models.Model):

    # Foreign keys -----------------------------------------
    model:SeleneModel = models.ForeignKey(SeleneModel, on_delete=models.CASCADE)
    # ------------------------------------------------------

    active:bool = models.BooleanField(default=True)

    cover_image:FileField = models.ImageField(upload_to='static/selene_chat_bots/', null=True, default=None)    
    cover_title:str = models.CharField(max_length=30, default='')
    cover_description:str = models.CharField(max_length=256, default='')
    
    default_response_on_webhook_failure:str = models.CharField(max_length=256, default='There was a problem with the request. Please try again later.')

    token:str = models.CharField(max_length=255) # token is used to authenticate the bot with the server

    created_at:datetime.datetime = models.DateTimeField()
    updated_at:datetime.datetime = models.DateTimeField(null=True, blank=True, default=None)
    

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

    """
        The new structure for Selene Node is as follows:

            It will behave as a linked list, where each node will perform an inheritance from the last node, this way, the nodes
            can ne update without creatint problems with the nodes that are on the produciton environment.

            These nodes are going to be attached to a version of a model, so that, there can be multiple models attached to the same 
    """
    
    model_version = models.ForeignKey(SeleneModelVersion, on_delete=models.CASCADE)

    next_node_version:'SeleneNode' = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='next_selene_node_version')
    previous_node_version:'SeleneNode' = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='previous_selene_node_version')
    
    next_node:'SeleneNode' = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='next_nodes')
    previous_node:'SeleneNode' = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='previous_nodes')
    next_node_on_option :dict = models.JSONField(default=dict)

    """
        this will be a dictionary with the following structure:

        {
            'option[str]': node_name[str]  
        }

        So, this dicitonary will only be used when there are options on the response object
    """

    # ------------------------------------------------------
        
    block_step:bool = models.BooleanField(default=True)
    
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

    tokenized_name:str = models.CharField(max_length=255)

    patterns:list = models.JSONField(default=list)

    random_response:bool = models.BooleanField(default=True)
    responses:list = models.JSONField(default=list)
    response_time_wait:int = models.IntegerField(default=0)

    # the token is going to be used to differentiate the nodes, so that, we have the possibility to update everything
    # on the node and knowing it was from a node before
    token = models.CharField(max_length=255)

    created_at:datetime.datetime = models.DateTimeField()

    @property
    def name(self) -> str:
        return self.tokenized_name.split('s--s')[1]
    
    
    @property
    def children(self) -> list:
        return self.selenechildnode.all()

    
    @property
    def head(self) -> 'SeleneNode':
        node = None
        try: node = SeleneNode.objects.get(id=self.head_id)
        except: pass
        return node
    
    
    def set_previous_node(self, node:'SeleneNode'):
        self.previous_node = node
        self.save()
        

    def get_next_node_on_option(self, option:str=None) -> 'SeleneNode':
        
        if option is None:
            return None if not self.next_node_on_option else True
        
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
            if self.token == 'initial_token':
                self.token = secrets.token_hex(16)
            self.created_at = timezone.now()

        super().save(*args, **kwargs)


    def __str__(self) -> str:
        return f'{self.id} - {self.name}'

