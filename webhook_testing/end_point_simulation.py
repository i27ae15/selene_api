def get_properties_test(parameters:dict) -> 'tuple(dict, int)':
    """
    This function will get the properties from the database
    """
    property_information = {}
    status_code = 200

    if 'simple_example' in parameters:

        property_information = {
            'kids_response': 'Absolutely, kids are allowed in the unit.',
            'pets_policy': 'Yes, some pets are allowed. Our pet policy includes a monthly fee of $ 25 per cat and $ 45 per dog. ',
            'unit_requirements': "Damage deposit CAD$ 1,125 is required to secure the unit, and first month's rent CAD$ 1,125 prior to move-in.",
            'less_than_6_months': 'in this case the rent will be 1500',
            'more_than_6_months': 'in this case the rent will be 1250',
            'number_of_rooms': '2',
        }

        status_code = 200

    return property_information, status_code
