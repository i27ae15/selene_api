# python
import re
import requests
import json 
import os


# Django 

from django.test import TestCase
from urllib.parse import unquote, urlparse


# python files
from selene_models.models import SeleneModelVersion

from .responses import SeleneResponseType, SeleneResponse
from .models import SeleneNode, SeleneModel, SeleneBot

# utils 
from print_pp.logging import Print
from faker import Faker
from training.tests import create_nodes

# numpy
import numpy as np

# tensorflow
from tensorflow import keras
import pickle

from selene_models.models import SeleneBot

# models
from .models import SeleneModel, SeleneNode, Interaction, MessageSent

# serializers
from .serializers import InteractionSerializer, MessageSentSerializer

# utils
from utils.send_email import SendEmail
from print_pp.logging import Print

# webhook testing
from webhook_testing.end_point_simulation import get_properties_test

from .responses import SeleneResponse, SeleneResponseType


Faker.seed(115)
fake:Faker = Faker()

# constants

PERSON_PROFILE = {
    '@Vname': fake.name(),
    '@Vage': fake.random_int(min=1, max=100),
    '@Vemail': fake.email(),
    '@Vphone': fake.phone_number(),
    '@Vaddress': fake.address(),
    '@Vcity': fake.city(),
    '@Vstate': fake.state(),
}


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


# Functions

class SeleneChatLocal:

    def __init__(self, variables:dict):

        self.variables = variables


    def convert_message_with_selene_state(self, message:str) -> str:
        
        while message.find('@V') != -1:

            start_index = message.find('@V')
            end_index = message.find(' ', start_index)
            
            if end_index == -1:
                end_index = len(message)

            var_name = message[start_index : end_index]

            # Print(var_name)

            # need to delete all special characters a variable name can have
            var_name = var_name.replace('.', '').replace(',', '').replace('?', '').replace('!', '').replace(';', '').replace(':', '')

            if var_name not in self.variables.keys():
                message = message.replace(var_name, f'@E:notFound-{var_name[2:]}')
            else:
                message = message.replace(var_name, str(self.variables[var_name]))
                
        return message


    def get_selene_response(self, selene_node:SeleneNode) -> list:
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
                    # TODO: set is input to True when changing other things
                    # self.is_input = True
                    self.name_to_save_variable = response['properties']['input_name']
                    current_response['input_type'] = response['properties']['input_type']
                    
                    
                    if current_response['input_type'] == 'options':
                        # when a option is active, a special function will manage the value that comes from the client
                        current_response['options'] = response['properties']['options']                    
                        self.variable_type_to_wait = 'str'
                        # TODO: set self.options to True when changing other things
                        # self.options = True
                    
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


class ChatFunctionsTestCase(TestCase):

    def setUp(self):
        self.selene_chat = SeleneChatLocal(PERSON_PROFILE)


    def test_convert_message_with_selene_state(self):

        # Print('person', PERSON_PROFILE)

        message = 'Hello, my name is @Vname, I am @Vage... years old, my email is @Vemail, my phone number is @Vphone, my address is @Vaddress, my city is @Vcity, my state is @Vstate'

        new_message = self.selene_chat.convert_message_with_selene_state(message)
        Print(new_message)
        
        self.assertEquals(new_message.find('@V'), -1)
        


class SeleneChat:
    
        __webhooks_called = dict()

        def __init__(self) -> None:

            self.selene_functions = {
                'print_message': self.print_message,
            }
            
            super().__init__()


        def websocket_connect(self):
            
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
            

            return {"type": "websocket.accept"}
    

        def websocket_receive(self, event:dict):
            
            proper_response = False
            object_dict:dict = json.loads(event['text'])

            CLIENT_MESSAGE = object_dict.get("message")
            Print('client message', CLIENT_MESSAGE)     
            
            # intilize the current selene-bot interaction
            if not self.selene_bot:
                try:
                    self.initialize_selene_bot(object_dict.get('token'))
                    self.selene_bot:SeleneBot
                    # in our first response we must return the cover image, if it exists
                    data_to_send = dict(
                        responses=[dict(
                            url=self.selene_bot.cover_image.url if self.selene_bot.cover_image else '',
                            title=self.selene_bot.cover_title,
                            description=self.selene_bot.cover_description,
                            type='media'
                        )]
                    )
                    
                    Print('initializing selene bot')
                    return (SeleneResponse(data_to_send).response)
                    
                except SeleneBot.DoesNotExist:
                    
                    Print('token is not valid, closing connection')
                    return (SeleneResponse('token is not valid, closing connection').response)
                    
            # save current message

            # firest we get the current node within the message that the user hast entered
            selene_node:SeleneNode = None
            selene_node = self.get_selene_node(CLIENT_MESSAGE)
            
            # selene_node is going to be false if the percentage is less than 0.95
            if not selene_node:
                text = {'message': 'I am sorry, I do not understand what you mean', 'type': 'text'}
                self.save_message(text)
                return (SeleneResponse(text).response)
            
            # Up to this point, we have a selene node that matches the message that the user has entered
            # we now have to check the different conditions that the node has

            # I think parent node is not longer necessary since steps is deprecated, let's check this out
            self.current_node = selene_node
            
            ### Do before ###
            # -------------------------------------------------------------------------  
            functions_to_call = self.current_node.do_before.get('functions_to_call')
            if functions_to_call:
                function_res = self.model_functions_to_call(functions_to_call)
                if function_res:
                    for res in function_res:
                        Print((SeleneResponse(res).response))
            
            ### Calling the webhook ###
            try:
                status_code, in_failure = self.call_webhook(webhook_object=self.current_node.do_before.get('web_hooks_to_call'))
                if not is_status_code_valid(status_code):
                    if in_failure:
                        Print((SeleneResponse(in_failure).response))
                    else:
                        Print((SeleneResponse(self.selene_bot.default_response_on_webhook_failure).response))
            # TODO: we should handle the exception
            except: pass
            # -------------------------------------------------------------------------  
            
            # this is the text that selene has to process to be able to come back to the client

            # self.print_current_session_state()

            if self.is_input:

                # we need to check the variable introduced
                if not check_variable(CLIENT_MESSAGE, self.variable_type_to_wait):
                    Print((SeleneResponse(self.response_on_failure).response))
                else:

                    self.variables[f"@V{self.name_to_save_variable}"] = CLIENT_MESSAGE
                    self.is_input = False
                    self.name_to_save_variable = None
                    self.input_object = dict()

                    proper_response = True

            response_object = self.get_selene_response(selene_node)
            
            # the message field should change to a dictionary with the message and the type of message
            self.save_message(response_object)

            Print((SeleneResponse(response_object).response))
            proper_response = True

            self.save_message(CLIENT_MESSAGE, sender=1)


            if proper_response:
                
                ### Do after ###
                # -------------------------------------------------------------------------  
                functions_to_call = self.current_node.do_after.get('functions_to_call')
                if functions_to_call:
                    function_res = self.model_functions_to_call(functions_to_call)
                    if function_res:
                        for res in function_res:
                            Print((SeleneResponse(res).response))
                            
                try:
                    status_code, in_failure = self.call_webhook(webhook_object=self.current_node.do_after.get('web_hooks_to_call'))
                    if not is_status_code_valid(status_code):
                        if in_failure:
                            Print((SeleneResponse(in_failure).response))
                        else:
                            Print((SeleneResponse(self.selene_bot.default_response_on_webhook_failure).response))
                # TODO: we should handle the exception
                except: pass
                # -------------------------------------------------------------------------  

                    
                # check if the current node has a next node
                option_to_look_up = None

                if self.options:
                    option_to_look_up = CLIENT_MESSAGE
                    self.options = False

                if self.current_node.get_next_node_on_option(option_to_look_up) or self.current_node.next_node:

                    if not self.is_input:
                        self.current_node = self.current_node.get_next_node_on_option(option_to_look_up) if option_to_look_up else self.current_node.next_node
                        
                        ### Do before ###
                        # -------------------------------------------------------------------------  
                        functions_to_call = self.current_node.do_before.get('functions_to_call')
                        if functions_to_call:
                            function_res = self.model_functions_to_call(functions_to_call)
                            if function_res:
                                for res in function_res:
                                    Print((SeleneResponse(res).response))
                                    
                        try:
                            status_code, in_failure = self.call_webhook(webhook_object=self.current_node.do_before.get('web_hooks_to_call'))
                            if not is_status_code_valid(status_code):
                                if in_failure:
                                    Print((SeleneResponse(in_failure).response))
                                else:
                                    Print((SeleneResponse(self.selene_bot.default_response_on_webhook_failure).response))
                        except: pass
                        # -------------------------------------------------------------------------       
                        response_object = self.get_selene_response(self.current_node)
                        self.save_message(response_object)
                        Print((SeleneResponse(response_object).response))
                        
                        
                        ### Do after ###
                        # -------------------------------------------------------------------------  
                        functions_to_call = self.current_node.do_after.get('functions_to_call')
                        if functions_to_call:
                            function_res = self.model_functions_to_call(functions_to_call)
                            if function_res:
                                for res in function_res:
                                    Print((SeleneResponse(res).response))
                                    
                        try:
                            status_code, in_failure = self.call_webhook(webhook_object=self.current_node.do_after.get('web_hooks_to_call'))
                            if not is_status_code_valid(status_code):
                                if in_failure:
                                    Print((SeleneResponse(in_failure).response))
                                else:
                                    Print((SeleneResponse(self.selene_bot.default_response_on_webhook_failure).response))
                        except: pass     

            
        def websocket_disconnect(self, event):
            # when websocket disconnects
            Print("disconnected", event)
            
            
        def initialize_selene_bot(self, token:str):
            
            """
                This only must be called at the beggining of the conversation
            
                Get the selene bot for this conversation
                setting it into self.selene_bot and creaters the current interaction, 
                setting it into interaction
            """
            
            self.selene_bot:SeleneBot = SeleneBot.objects.get(token=token)
                
            self.interaction:Interaction = Interaction.objects.create(selene_bot=self.selene_bot)

            # when connections occurs, the model with the current version is loaded
            self.selene_model_object:SeleneModel = self.selene_bot.model
            self.tf_model = keras.models.load_model(self.selene_model_object.current_version.version_model_path + 'model')    

        
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
                    # TODO: set is input to True when changing other things
                    # self.is_input = True
                    self.name_to_save_variable = response['properties']['input_name']
                    current_response['input_type'] = response['properties']['input_type']
                    
                    
                    if current_response['input_type'] == 'options':
                        # when a option is active, a special function will manage the value that comes from the client
                        current_response['options'] = response['properties']['options']                    
                        self.variable_type_to_wait = 'str'
                        # TODO: set self.options to True when changing other things
                        # self.options = True
                    
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
            with open(self.selene_model_object.current_version.version_model_path + 'tokenizer.pickle', 'rb') as handle:
                tokenizer = pickle.load(handle)

            # load label encoder object
            with open(self.selene_model_object.current_version.version_model_path + 'label_encoder.pickle', 'rb') as enc:
                lbl_encoder = pickle.load(enc)

            # parameters
            max_len = 20

            result = self.tf_model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([text]),
            truncating='post', maxlen=max_len))
            
            posible_node = False
            
            re = result[0]
            for r in re:
                # convert scientific notation to float
                str_num = '{:f}'.format(r * 100)
                Print('Percentage', str_num, bl=False, al=False, include_caller_line=False) 
                
                if int(str_num.split(".")[0]) >= 95:
                    posible_node = True
                    break
                
            max_result = np.argmax(result)
            Print(lbl_encoder.inverse_transform([max_result]))
            print(posible_node)
            Print('possible node', posible_node, al=False)
            
            if not posible_node: return False

            tag = lbl_encoder.inverse_transform([max_result])
            for node in self.selene_model_object.nodes:
                if node.name == tag:
                    return node
        

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
            
        
        def call_webhook(self, webhook_object:'list[dict]') -> 'tuple[str]':
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
                        "in_failure": "please enter a valid value",
                        "method": "GET",
                        ]
                    }
                ]
            """

            ### TODO: ###

            # when calling a webhook, check if it was called early so that we 
            # don't call it again and just go to the variables in current session
            # to look for the needed information

            # Note that this only can be done with get requets, since these are meant to not update 
            # anything in the database, if, something needs to be updated, then call POST, in the webhooks 
            # request, so that the webhook is called again
            
            in_failure:str = None

            if not webhook_object:
                return
            
            for webhook in webhook_object:
                
                method:str = 'GET' # webhook['method']
                url = webhook['url']
                
                if method == 'GET':
                    # check if the webhook was called before
                    if url in self.__webhooks_called:
                        # if it was called before, then get the response from the state
                        response = self.__webhooks_called[url]
                        # set the variables in the state
                        for key in response:
                            self.variables[f'@V{key}'] = response[key]
                        break
                    
                parameters = webhook.get('parameters', {})

                # Testing -----------------------------------
                # calling the webhook
                testing_response, status_code = get_properties_test(parameters)
                
                if method == 'GET':
                    # requests.get(url, params=parameters)
                    self.__webhooks_called[url] = testing_response
                    

                if is_status_code_valid(status_code):
                    for key in testing_response:
                        self.variables[f'@V{key}'] = testing_response[key]

                else:
                    in_failure = webhook.get('in_failure')
                    
                return status_code, in_failure

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

                # need to delete all special characters a variable name can have
                var_name = var_name.replace('.', '').replace(',', '').replace('?', '').replace('!', '').replace(';', '').replace(':', '').replace('¿', '')

                if var_name not in self.variables.keys():
                    message = message.replace(var_name, f'@E:notFound-{var_name[2:]}')
                else:
                    message = message.replace(var_name, str(self.variables[var_name]))
        
            return message


        def print_current_session_state(self):
            print('-'*50)
            print('--currrent session state--')
            print('session.variables: ', self.variables)
            print('session.current_node: ', self.current_node.name)
            if self.current_node.next():
                print('session.next_node: ', self.current_node.next().name)
            else:
                print('session.next_node: ', None)
            
            if self.parent_node:
                print('session.parent_node: ', self.parent_node.name)
            else:
                print('session.parent_node: ', None)
            print('-'*50)
     
import json
class SeleneTestChat(TestCase):

    def setUp(self) -> None:
        _, selene_bot = create_nodes()
        self.selene_bot = selene_bot
    
    def test_selene_chat(self):

        current_session = SeleneChat()
        Print(current_session.websocket_connect())

        event = {'text':json.dumps({"token": self.selene_bot.token})}
        current_session.websocket_receive(event)

        # getting the first selene node
        event = {'text':json.dumps({"message": "pattern 1"})}
        current_session.websocket_receive(event)
        

    