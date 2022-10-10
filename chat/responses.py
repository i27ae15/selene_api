from utils.logging import Print

from enum import Enum
import json


class SeleneResponseType(Enum):
    TEXT = 1
    MEDIA = 2
    LINK = 3
    

class SeleneResponse:
    
    """

        This will convert the simple text response to the correct response for the chatbot
        
    """
    
    __response_text:dict = None
    __response_media:dict = None
    __response_link:dict = None
    
    def __init__(self, messages:'list[str]', message_type:SeleneResponseType=SeleneResponseType.TEXT, convert_all_messages:bool=True):
        self.message = messages if type(messages) == list or type(messages) == dict else [messages]
        self.message_type = message_type
        
        if convert_all_messages:
            self.__convert_message(type(messages) == dict)
    
    
    def __convert_message(self, is_dict:bool=False):
        
        res_object = {
            'type': 'websocket.send',
            'text': {'responses': list()},
        }
        
        if is_dict:
            self.message:dict
            if self.message.get('responses'):
                res_object['text'] = self.message
            else:
                res_object['text']['responses'] = [self.message]
        
        else:
            for message in self.message:
                Print('message', message)

                res:list[dict] = res_object['text']['responses']
                if message['type'] == 'input':
                    res.append({'type': message['type'], 'input_type':'options', 'options':message['options'], 'message': message['message']})
                else:
                    res.append({'type': message['type'], 'message': message['message']})
                    
                
                res_object['text']['responses'] = res
                

        res_object['text'] = json.dumps(res_object['text'])
        self.__response_text = res_object
    
    
    @property
    def response(self) -> dict:
        
        if self.message_type == SeleneResponseType.TEXT:
            return self.__response_text
        
        elif self.message_type == SeleneResponseType.MEDIA:
            return self.__response_media
            
        elif self.message_type == SeleneResponseType.LINK:
            return self.__response_link
        
        
        