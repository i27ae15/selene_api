from django.test import TestCase
from .training import train


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
        
        data_to_train_model = {
            "intents": [
            {
            "node": "Make appointment",
            "patterns": ["I want to make an appointment", "I want to schedule an appointment", "I want to book an appointment", "Appointment", "Book an appointment", "Schedule an appointment", "Make an appointment", "I want to make an appointment with a doctor", "I want to schedule an appointment with a doctor", "I want to book an appointment with a doctor", "Appointment with a doctor", "Book an appointment with a doctor", "Schedule an appointment with a doctor", "Make an appointment with a doctor"],
            "responses": [
            {
                "type": "text",
                "settings": {},
                "text": "Of course, what day and time would you like to schedule your appointment?"
            }
            ],
            'steps': []
            }]
        }

        end = 3
        for step in range(0, end):
            data_to_train_model['intents'][0]['steps'].append({
                "name": "step_{}".format(step),
                "patterns": ["step_{}".format(step)],
                "responses": ["step_{}".format(step)],
                "do_after": "step_{}".format(step),
                "do_before": "step_{}".format(step),
                "block_step": False,
                "random_response": True,
            })
        

        column, reversed_line = train(data_to_train_model)

        print('-' * 50)
        print(reversed_line)
        print('-' * 50)

        print('-' * 50)
        print(column)
        print('-' * 50)

        self.assertEquals(column, test_column(end))
        self.assertEquals(reversed_line, test_reversed_column(end))
        