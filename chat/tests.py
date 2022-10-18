# Django 

from django.test import TestCase


# python files
from .responses import SeleneResponseType, SeleneResponse
from .models import SeleneNode

# utils 
from print_pp.logging import Print
from faker import Faker



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



# Functions

class SeleneChat:

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
        self.selene_chat = SeleneChat(PERSON_PROFILE)


    def test_convert_message_with_selene_state(self):

        # Print('person', PERSON_PROFILE)

        message = 'Hello, my name is @Vname, I am @Vage... years old, my email is @Vemail, my phone number is @Vphone, my address is @Vaddress, my city is @Vcity, my state is @Vstate'

        new_message = self.selene_chat.convert_message_with_selene_state(message)
        Print(new_message)
        
        self.assertEquals(new_message.find('@V'), -1)
        

class SeleneResponseTestCase(TestCase):

    def setUp(self):

        self.selene_chat = SeleneChat(PERSON_PROFILE)

        self.node:SeleneNode = SeleneNode.objects.create(
            tokenized_name='test',
            responses=[
                {
                    "type": "text",
                    "properties": {},
                    "text": "This is a test message"
                }, 
            ]
        )


    def test_get_response(self):
        responses = self.selene_chat.get_selene_response(self.node)

        Print('response not converted', responses)
        self.assertEquals(type(responses), list)
        # Print(responses)

        response = SeleneResponse(responses).response
        response2 = SeleneResponse({
            'message': 'This is a test message',
            'type': 'text',
        }).response

        Print('converted response_1', response)
        Print('converted response_2', response2)


        

