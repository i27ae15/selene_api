# python
import time

import asyncio
from channels.consumer import AsyncConsumer
from random import randint
from time import sleep


import json 
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder

import random
import pickle

from .models import SeleneModel, SeleneNode

from utils.send_email import SendEmail


import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()


class SeleneChat(AsyncConsumer):

    current_node:SeleneNode = None
    selene_model_object:SeleneModel = None
    tf_model:keras.models.Model = None

    variables = dict()
    is_input = False
    input_object = dict()


    def __init__(self) -> None:
        
        self.SELENE_FUNCTIONS = {
            'print_message': self.print_message,
            'to_wait': self.to_wait,
            'send_email': SendEmail,
        }
        super().__init__()


    async def websocket_connect(self,event):
        # when websocket connects

        # when connections occurs, the model is loaded
        print("connected", event)

        self.selene_model_object:SeleneModel = SeleneModel.objects.get(id=1)
        self.tf_model = keras.models.load_model(self.selene_model_object.model_path + 'model')

        await self.send({"type": "websocket.accept"})
        await self.send({"type":"websocket.send", "text":0})
 

    async def websocket_receive(self, event):
        # when messages is received from websocket
        # here we need to write the selene response
        
        TEXT = event.get("text")

        if TEXT == 'Hi there!':
            await self.send({"type":"websocket.send", "text":'Hi there!'})
        else:

            # this is the text that selene has to process to be able to send back to the client
            if self.is_input:
                self.variables[f"@V{self.input_object['name']}"] = TEXT
                self.is_input = False
                self.input_object = dict()


                function_res = self.model_action(self.current_node.do_after['functions_to_call'])
                if function_res:
                    for res in function_res:
                        await self.send(res)

            else:
                selene_node = self.get_selene_node(TEXT)
                self.current_node = selene_node


                if selene_node.name != 'not_found':

                    # func = [{"name": "print_message", "parameters": {"message": "Sending message"}}, 
                    #         {"name": "send_email","parameters": {
                    #                     "send_to": "andresruse18@gmail.com",
                    #                     "subject": "Hello there",
                    #                     "html": "<h1>f'Hello @Vperson_name'<h1>",
                    #                 }}]

            

                    # function_res = self.model_action(func)                
                    # if function_res:
                    #     for res in function_res:
                    #         await self.send(res)


                    waiting_time = selene_node.response_time_wait


                    for response in selene_node.responses:

                        time.sleep(waiting_time)
                        await self.send({"type":"websocket.send", "text":response['text']})

                        if response['type'] == 'input':
                            self.is_input = True
                            break
                    

                        # if not self.is_input:
                        #     function_res = self.model_action(func)                
                        #     if function_res:
                        #         for res in function_res:
                        #             await self.send(res)

                else:
                    await self.send({"type":"websocket.send", "text":'Sorry, I do not understand'})   
        
        
    async def websocket_disconnect(self, event):
        # when websocket disconnects
        print("disconnected", event)


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
    

    def model_action(self, functions_to_call:dict):
        response = list()
        for function in functions_to_call:
            func = self.SELENE_FUNCTIONS[function['name']]
            if function['name'] == 'print_message':
                response.append(func(**function['parameters']))


        return response
    

    def print_message(self, message:str) -> dict:
        
        while message.find('@V') != -1:
            var_name = message[message.find('@V')+2:message.find(' ', message.find('@V'))]

            if var_name not in self.variables.keys():
                message = message.replace(f'@V{var_name}', f'@E:notFound-{var_name}')
            else:
                message = message.replace(f'@V{var_name}', self.variables[f'@V{var_name}'])
    
        return {"type":"websocket.send", "text":message}


    def to_wait(self, time_to_wait:int):
        time.sleep(time_to_wait)