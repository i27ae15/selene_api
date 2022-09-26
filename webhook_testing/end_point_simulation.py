def get_properties_test(parameters:dict) -> 'tuple(dict, int)':
    """
    This function will get the properties from the database
    """
    property_information = {}
    status_code = 200

    if 'simple_example' in parameters:

        property_information = {
            'kids_response': 'Kids are welcomed here',
            'pets_policy': 'Cats and dogs are allowed',
            'unit_requirements': 'You have to be 21 years old and have a job to be able to live here',
            'less_than_6_months': 'in this case the rent will be 1500',
            'more_than_6_months': 'in this case the rent will be 1250',
            'number_of_rooms': '2',
        }

        status_code = 200

    return property_information, status_code
