# python
import time
import re
import requests
import json 
import os

# numpy
import numpy as np

# tensorflow
from tensorflow import keras
import pickle

#import
import django 

# django-channels
from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer

from selene_models.models import SeleneBot

# models
from .models import SeleneModel, SeleneNode, Interaction, MessageSent

# serializers
from .serializers import InteractionSerializer, MessageSentSerializer

# utils
from utils.send_email import SendEmail
from utils.logging import Print

# webhook testing
from webhook_testing.end_point_simulation import get_properties_test

from .responses import SeleneResponse, SeleneResponseType

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()


def check_variable(variable, variable_type) -> bool:
    if variable_type == 'int':
        try:
            variable = int(variable)
        except:
            return False
    elif variable_type == 'float':
        try:
            variable = float(variable)
        except:
            return False
    elif variable_type == 'str':
        try:
            variable = str(variable)
        except:
            return False
    elif variable_type == 'email':
        # check if the contend of variable is an email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not (re.fullmatch(regex, variable)):
            return False    
            
    return True


def is_status_code_valid(status_code) -> bool:
    if status_code >= 100 and status_code < 400:
        return True


class SeleneChat(AsyncConsumer):

    def __init__(self) -> None:

        Print('initializing selene chat')
        
        self.selene_functions = {
            'print_message': self.print_message,
            'to_wait': self.to_wait,
            'send_email': SendEmail,
        }
           
        super().__init__()


    async def websocket_connect(self, event):
        
        self.in_step:bool = False
        self.parent_node:SeleneNode = None
        self.current_node:SeleneNode = None
        self.selene_model_object:SeleneModel = None
        self.tf_model:keras.models.Model = None

        self.variables:dict = dict()
        self.input_object:dict = dict()

        self.is_input:bool = False
        self.options:bool = False

        self.name_to_save_variable:str = None
        self.variable_type_to_wait:str = None
        self.response_on_failure:str = None
        
        self.response_validators:dict = dict()

        self.selene_bot:SeleneBot = None
        self.interaction:Interaction = None
        

        await self.send({"type": "websocket.accept"})
 

    async def websocket_receive(self, event):
        
        proper_response = False
        object_dict:dict = json.loads(event['text'])

        MESSAGE = object_dict.get("message")        
        
        # intilize the current selene-bot interaction
        if not self.selene_bot and object_dict.get('token'):
            try:
                self.initialize_selene_bot(object_dict.get('token'))
            except SeleneBot.DoesNotExist:
                
                await self.send(SeleneResponse('token is not valid, closing connection').response)
                
                Print('token is not valid, closing connection')
                
                raise StopConsumer
                    
        # save current message

        selene_node:SeleneNode = None
        if not self.in_step:
            selene_node = self.get_selene_node(MESSAGE)
        

        if not self.parent_node or self.current_node and self.current_node != selene_node and selene_node is not None:

            if self.parent_node is None:
                self.parent_node = selene_node
            
            self.current_node = selene_node

            Print('parent_node', self.parent_node.name)
            
            ### Do before ###
            # -------------------------------------------------------------------------  
            functions_to_call = self.current_node.do_before.get('functions_to_call')
            if functions_to_call:
                function_res = self.model_functions_to_call(functions_to_call)
                if function_res:
                    for res in function_res:
                        await self.send(SeleneResponse(res).response)
                        
            # TODO: check if the satus code is valid
            status_code = self.call_webhook(webhook_object=self.current_node.do_before.get('web_hooks_to_call'))
        
            # -------------------------------------------------------------------------  
           
        # this is the text that selene has to process to be able to send back to the client
        if self.is_input:

            # we need to check the variable introduced
            if not check_variable(MESSAGE, self.variable_type_to_wait):
                await self.send(SeleneResponse(self.response_on_failure).response)
            else:

                self.variables[f"@V{self.name_to_save_variable}"] = MESSAGE
                self.is_input = False
                self.name_to_save_variable = None
                self.input_object = dict()

                proper_response = True

                Print('variables', self.variables)

        else:
            if selene_node.name != 'not_found':

                waiting_time = selene_node.response_time_wait
                # for front
                time.sleep(waiting_time)

                response_object = self.get_selene_response(selene_node)
                
                # the message field should change to a dictionary with the message and the type of message
                self.save_message(response_object)
                await self.send({"type":"websocket.send", "text":json.dumps({'responses': response_object})})
                proper_response = True

            else:
                text = 'I am sorry, I do not understand what you mean'
                self.save_message(text)
                await self.send({"type":"websocket.send", "text":text})   
        
        self.save_message(MESSAGE, sender=1)
        if proper_response:
            
            ### Do after ###
            # -------------------------------------------------------------------------  
            functions_to_call = self.current_node.do_after.get('functions_to_call')
            if functions_to_call:
                function_res = self.model_functions_to_call(functions_to_call)
                if function_res:
                    for res in function_res:
                        await self.send(SeleneResponse(res).response)
                        
                        
            self.call_webhook(webhook_object=self.current_node.do_after.get('web_hooks_to_call'))
            
            # -------------------------------------------------------------------------  

                
            # check if the current node has a next node, or a following step
            option_to_look_up = 'next_node'

            if self.options:
                option_to_look_up = MESSAGE
                self.options = False

            Print('before next node')

            if self.current_node.next(option_to_look_up):
                self.in_step = True

                if not self.is_input:
                    self.current_node = self.current_node.next(option_to_look_up)
                    
                    ### Do before ###
                    # -------------------------------------------------------------------------  
                    functions_to_call = self.current_node.do_before.get('functions_to_call')
                    if functions_to_call:
                        function_res = self.model_functions_to_call(functions_to_call)
                        if function_res:
                            for res in function_res:
                                await self.send(SeleneResponse(res).response)
                                
                    
                    self.call_webhook(webhook_object=self.current_node.do_before.get('web_hooks_to_call'))
                    
                    # -------------------------------------------------------------------------       
                    response_object = self.get_selene_response(self.current_node)
                    self.save_message(response_object)
                    await self.send({"type":"websocket.send", "text":json.dumps({'responses': response_object})})
                    
                    
                    ### Do after ###
                    # -------------------------------------------------------------------------  
                    functions_to_call = self.current_node.do_after.get('functions_to_call')
                    if functions_to_call:
                        function_res = self.model_functions_to_call(functions_to_call)
                        if function_res:
                            for res in function_res:
                                await self.send(SeleneResponse(res).response)
                                
                    
                    self.call_webhook(webhook_object=self.current_node.do_after.get('web_hooks_to_call'))
                    
                    # -------------------------------------------------------------------------         

                    Print('next to current node', self.current_node.next())
                    
                    if not self.current_node.next():
                        if self.in_step and not self.is_input:
                            self.in_step = False
                            self.parent_node = None
                            
                            # response_object =[{'message': 'Thank you for your time, I hope I have been able to help you', 'type': 'text'}, 
                            #             {'message': 'If you have any other questions, please do not hesitate to tell me about it', 'type': 'text'}]

                            # await self.send({"type":"websocket.send", "text":json.dumps({'responses': response_object})})

            # this won't be necessary anymore
            else:
                Print('no next node')
                if self.in_step:
                    self.in_step = False
                    
                    Print('no next step')


                    # response_object =[{'message': 'Thank you for your time, I hope I have been able to help you', 'type': 'text'}, 
                    #                   {'message': 'If you have any other questions, please do not hesitate to tell me about it', 'type': 'text'}]

                    # await self.send({"type":"websocket.send", "text":json.dumps({'responses': response_object})})

                    #we need to print a message saying that the conversation has ended within the current node    
    
        
    async def websocket_disconnect(self, event):
        # when websocket disconnects
        Print("disconnected", event)
        
        
    def initialize_selene_bot(self, token:str):
        self.selene_bot:SeleneBot = SeleneBot.objects.get(token=token)
            
        self.interaction:Interaction = Interaction.objects.create(selene_bot=self.selene_bot)

        # when connections occurs, the model is loaded
        self.selene_model_object:SeleneModel = self.selene_bot.model
        self.tf_model = keras.models.load_model(self.selene_model_object.model_path + 'model')    

    
    def get_selene_response(self, selene_node:SeleneNode) -> dict:
        response_object = list()

        for response in selene_node.responses:
            
            # this is two properties will cover a simple text response
            current_response = {
                "message": response['text'],
                "type": response['type'],
            }
            
            # if the response type is an image then we need to add the url, title and description field from the properties object
            if response['type'] == 'media':
                current_response['url'] = response['properties']['url']
                current_response['title'] = response['properties']['title']
                current_response['description'] = response['properties']['description']

            elif response['type'] == 'input':
                # field and actions for the general response of type input
                self.is_input = True
                self.name_to_save_variable = response['properties']['input_name']
                current_response['input_type'] = response['properties']['input_type']
                
                
                if current_response['input_type'] == 'options':
                    # when a option is active, a special function will manage the value that comes from the client
                    current_response['options'] = response['properties']['options']                    
                    self.variable_type_to_wait = 'str'
                    self.options = True
                
                elif current_response['input_type'] == 'selene_input':
                    # fields and actions for the response of type selene_input
                    self.response_on_failure = response['properties'].get('if_failure') if response['properties'].get('if_failure') else 'please enter a valid value'
                    current_response['type'] = 'text'

                    if response['properties'].get('variable_type'):
                        if response['properties']['variable_type'] == 'raw_text':
                            self.response_validators['max_length'] = response['properties']['max_length']
                            self.variable_type_to_wait = 'str'

                        elif response['properties']['variable_type'] == 'number':
                            self.response_validators['min_value'] = response['properties']['min_value']
                            self.response_validators['max_value'] = response['properties']['max_value']
                            self.variable_type_to_wait = 'int'
                    else:
                        self.variable_type_to_wait = 'str'

            response_object.append(current_response)

        # converting the message object message to use the selene current state

        for response in response_object:
            message = response['message']
            response['message'] = self.convert_message_with_selene_state(message)

        return response_object


    def get_selene_node(self, text:str) -> SeleneNode:

        # load tokenizer object
        with open(self.selene_model_object.model_path + 'tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        # load label encoder object
        with open(self.selene_model_object.model_path + 'label_encoder.pickle', 'rb') as enc:
            lbl_encoder = pickle.load(enc)

        # parameters
        max_len = 20

        result = self.tf_model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([text]),
        truncating='post', maxlen=max_len))

        tag = lbl_encoder.inverse_transform([np.argmax(result)])

        for node in self.selene_model_object.nodes:
            if node.name == tag:
                return node

        return False
    

    def model_functions_to_call(self, functions_to_call:list):
        response = list()
        for function in functions_to_call:
            func = self.selene_functions[function['name']]
            if function['name'] == 'print_message':
                response.append(func(**function['parameters']))
            else:
                func(**function['parameters'])

        return response
    

    def print_message(self, message:str) -> dict:
        
        message = self.convert_message_with_selene_state(message)
        return {"type":"websocket.send", "text":message}


    def to_wait(self, time_to_wait:int):
        time.sleep(time_to_wait)
        
    
    def call_webhook(self, webhook_object:'list[dict]'):
        """
            This function will call a webhook and will save the response of the webhook into the state variables
            
            the webhook_object follows the following structure:
            
            webhook_object = [
                {
                    "url": "https://www.youtube.com/results?search_query=never+gonna+give+you+up",
                    "parameters": [
                        {
                            "name": "Aquiles, el de los pies ligeros",
                            "age": "3200",
                            "like_apples": "@Vaquiles_like_apples"
                        }
                    ]
                }
            ]
        """

        ### TODO: ###

        # when calling a webhook, check if it was called early so that we 
        # don't call it again and just go to the variables in current session
        # to look for the needed information

        # Note that this only can be done with informative webhooks, not with
        # webhooks that change something in their origin

        if not webhook_object:
            return
        
        for webhook in webhook_object:
            url = webhook['url']
            parameters = webhook.get('parameters', {})
            
            Print(['call to webhook', 'parameters'], [url, parameters])

            # Testing -----------------------------------

            testing_response, status_code = get_properties_test(parameters)

            if is_status_code_valid(status_code):
                for key in testing_response:
                    self.variables[f'@V{key}'] = testing_response[key]

                Print(['testing_response', 'self.variables'], [testing_response, self.variables])
                
            return status_code

                    # -------------------------------------------
            response = requests.post('https://calendar-dev-api.herokuapp.com', params=parameters)
            
            print('status_code: ', response.status_code)
            print('response: ', response)
            print('-'*50)
            
            if response.status_code >= 200 and response.status_code < 400:
                for key in response:
                    self.variables[f'@V{key}'] = response[key]
                
                return response.status_code
            
            raise Exception(f'Error calling webhook: {url}, status_code: {response.status_code}')
        
        
    def save_message(self, message:dict, sender:int=0, understood:bool=True):
        """
            This function will save the message into the database
            more specific int he MessageSent object
            
            sender: 0 -> selene
            sender: 1 -> client
        """
        
        if type(message) is str:
            message = {"type":"text", "message":message}
        
        MessageSent.objects.create(
            node=self.current_node,
            interaction=self.interaction,
            message_object=message,
            sender=sender,
            understood_within_context=understood
        )
    

    def convert_message_with_selene_state(self, message:str):
        
        while message.find('@V') != -1:

            start_index = message.find('@V')
            end_index = message.find(' ', start_index)

            if end_index == -1:
                end_index = len(message)

            var_name = message[start_index : end_index]

            if var_name not in self.variables.keys():
                message = message.replace(var_name, f'@E:notFound-{var_name[2:]}')
            else:
                message = message.replace(var_name, self.variables[var_name])
    
        return message


    def print_current_session_state(self):
        print('-'*50)
        print('--currrent session state--')
        print('session.variables: ', self.variables)
        print('session.current_node: ', self.current_node.name)
        if self.current_node:
            print('session.next_node: ', self.current_node.next().name)
        else:
            print('session.next_node: ', None)
        
        if self.parent_node:
            print('session.parent_node: ', self.parent_node.name)
        else:
            print('session.parent_node: ', None)
        print('-'*50)