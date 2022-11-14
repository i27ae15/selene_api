from django.test import TestCase
from selene_models.models import SeleneNode, SeleneModelVersion, SeleneBot
from .training import train, SeleneNode, SeleneModelVersion

from print_pp.logging import Print

from enum import Enum

NODES_CREATED_IN_CLASS = 0

class NodeType(Enum):
    TEXT = 1
    INPUT = 2


class Node:

    __properties_for_simple_input = {
        "input_type": "selene_input",
        "input_name": "person_email"
    }


    def __init__(self, node_type:NodeType, node_name:str=None, node_text:str=None, node_properties:dict=None, node_patterns:list=None):
        global NODES_CREATED_IN_CLASS
        NODES_CREATED_IN_CLASS += 1


        """
            Properties:

                when node_type is INPUT:

                "properties": {
                    "input_type": "selene_input",
                    "input_name": "person_email"
                },
    
        """

        self.node_type = (node_type.name).lower()
        self.node_properties =  self.__properties_for_simple_input if node_properties is None else node_properties
        self.node_name = f'node {NODES_CREATED_IN_CLASS}' if node_name is None else node_name
        self.node_patterns = [f'pattern {NODES_CREATED_IN_CLASS}'] if node_patterns is None else node_patterns
        self.node_text = f'text {NODES_CREATED_IN_CLASS}' if node_text is None else node_text



def create_nodes(nodes_to_create:list[list[NodeType, int]]=[[NodeType.TEXT, 10], [NodeType.INPUT, 2]], num_of_versions:int=1, print_nodes_created=True) -> list[SeleneNode]:
    for version in range(0, num_of_versions):
        
            data_to_train_model = dict(intents = list(), version = f'{version}.0.0')

            for node_instance in nodes_to_create:
                
                for i in range(0, node_instance[1]):
                    
                    node = Node(node_type=node_instance[0])
                
                    data_to_train_model['intents'].append({
                        "node": node.node_name,
                        "patterns": node.node_patterns,
                        "responses": [
                        {
                            "type": node.node_type,
                            "settings": {},
                            "text": node.node_text,
                        }
                        ],
                    })

                    if node.node_type == NodeType.INPUT.name.lower():
                        data_to_train_model['intents'][-1]['responses'][0]['properties'] = node.node_properties


    nodes_created = train(data_to_train_model, 'model_number_one')

    if print_nodes_created:
        for node in nodes_created:
            Print(
                ('node_name', 'model_version', 'next_node', 'previous_node', 'token'), 
                (node.name, node.model_version.version, node.next_node, node.previous_node, node.token), 
                include_caller_line=False)
    

    # creating the model bot
    model_version = SeleneModelVersion.objects.get(version=f'{version}.0.0')
    selene_bot = SeleneBot.objects.create(model=model_version.model, token='', created_at='')


    return nodes_created, selene_bot


def test_column(total):
    column = str()
    # we count more one because the main node is also included
    for node in range(0, total + 1):
        column += f'{node + 1} <- '

    column += 'None'

    return column


def test_reversed_column(total):
    column = str()
    # we count more one because the main node is also included
    for node in range(total + 1, 0, -1):
        column += f'{node} <- '

    column += 'None'

    return column


class TrainingTestCase(TestCase):
    
    def test_training(self, nodes_to_create:list[list[NodeType, int]]=[[NodeType.TEXT, 10], [NodeType.INPUT, 2]], num_of_versions:int=1):

        for version in range(0, num_of_versions):
        
            data_to_train_model = dict(intents = list(), version = f'{version}.0.0')

            for node_instance in nodes_to_create:
                
                for i in range(0, node_instance[1]):
                    
                    node = Node(node_type=node_instance[0])
                
                    data_to_train_model['intents'].append({
                        "node": node.node_name,
                        "patterns": node.node_patterns,
                        "responses": [
                        {
                            "type": node.node_type,
                            "settings": {},
                            "text": node.node_text,
                        }
                        ],
                    })

                    if node.node_type == NodeType.INPUT.name.lower():
                        data_to_train_model['intents'][-1]['responses'][0]['properties'] = node.node_properties


        nodes_created = train(data_to_train_model, 'model_number_one')

        for node in nodes_created:
            Print(
                ('node_name', 'model_version', 'next_node', 'previous_node', 'token'), 
                (node.name, node.model_version.version, node.next_node, node.previous_node, node.token), 
                include_caller_line=False)


        return


        # Creating nodes with the new model system

        model_version = None
        try:
            model_version = SeleneModelVersion.objects.get(id=1)
        except SeleneModelVersion.DoesNotExist:
            Print('No model version found')
            pass

        data_to_train_model = dict(intents = list(), version = '2.0.0')

        for i in range(0, 10):
            data_to_train_model['intents'].append({
                "node": f"node {i}",
                "patterns": [f"pattern {i}"],
                "responses": [
                {
                    "type": "text",
                    "settings": {},
                    "text": "Of course, what day and time would you like to schedule your appointment?"
                }
                ],
                'steps': []
            })

            if i == 3:
                data_to_train_model['intents'][i]['next_node'] = 'node 4'

            if i == 4:
                data_to_train_model['intents'][i]['next_node'] = 'node 5'
            
            if i == 5:
                data_to_train_model['intents'][i]['next_node'] = 'node 6'


        if model_version:
            for index, node in enumerate(model_version.nodes()):
                data_to_train_model['intents'][index]['token'] = node.token


        Print('creating nodes with the new model system')

        nodes_created = train(data_to_train_model, 'model_number_one', model_version)


        for node in nodes_created:
            Print(
                ('node_name', 'model_version', 'next_node', 'previous_node', 'token'), 
                (node.name, node.model_version.version, node.next_node, node.previous_node, node.token), 
                include_caller_line=False)
        

        current_node:SeleneNode = next(filter(lambda node: node.name == 'node 3', nodes_created))


        while current_node:
            Print('current_node', current_node.name, al=False, bl=False, include_caller_line=False)
            current_node = current_node.next_node


        print(SeleneModelVersion.objects.all())
        