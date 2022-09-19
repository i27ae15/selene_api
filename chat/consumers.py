import asyncio
from channels.consumer import AsyncConsumer
from random import randint
from time import sleep


import json 
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder

from colorama import Fore, Style, Back

import random
import pickle


import wikipediaapi
wiki = wikipediaapi.Wikipedia('en')


def call_wikipedia(query):
    
    page = wiki.page(query)
    
    if not page.exists():
        return "Sorry, I couldn't find any results for that."

    return page.summary
    



class PracticeConsumer(AsyncConsumer):

    current_step = None
    

    async def websocket_connect(self,event):
        # when websocket connects
        print("connected", event)

        await self.send({"type": "websocket.accept"})
        await self.send({"type":"websocket.send", "text":0})
 

    async def websocket_receive(self, event):
        # when messages is received from websocket
        # here we need to write the selene response
        
        TEXT = event.get("text")

        # this is the text that selene has to process to be able to send back to the client
        response = selene_response(text=TEXT)

        if type(response) == str:
            await self.send({"type": "websocket.send", "text": response})
            self.wikipedia = False
        else:

            for r in response:
                if r == "ask your question to Selene: ":
                    self.wikipedia = True

                await self.send({"type":"websocket.send",
                                "text":r})

    
    
    async def websocket_disconnect(self, event):
        # when websocket disconnects
        print("disconnected", event)




def selene_response(text:str, look_in_wikipedia:bool=False):

    if(look_in_wikipedia):
        return call_wikipedia(text.lower())

    # this should call the model that has the responses and return the response
    with open("static/data_to_train/test.json") as file:
        data = json.load(file)


    # load trained model
    model = keras.models.load_model('static/chat_model')

    # load tokenizer object
    with open('static/tokens/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # load label encoder object
    with open('static/tokens/label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)

    # parameters
    max_len = 20
    

    result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([text]),
    truncating='post', maxlen=max_len))

    tag = lbl_encoder.inverse_transform([np.argmax(result)])
    data_to_return = list()

    for i in data['intents']:
        if i['tag'] == tag:
            data_to_return.append(np.random.choice(i['responses']))
           
            if tag == 'Wikipedia':
                data_to_return.append("ask your question to Selene: ")

            break


    if not len(data_to_return):
        data_to_return.append("I don't understand")

    return data_to_return
        