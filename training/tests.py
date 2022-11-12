from django.test import TestCase
from .training import train, SeleneNode, SeleneModelVersion

from print_pp.logging import Print

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
    
    def test_training(self):
        
        data_to_train_model = dict(intents = list(), version = '1.0.0')

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


        nodes_created = train(data_to_train_model, 'model_number_one')

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
        