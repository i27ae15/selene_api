from print_pp.logging import Print

def get_properties_test(parameters:dict) -> 'tuple(dict, int)':
    """
    This function will get the properties from the database
    """
    property_information = {}
    status_code = 200

    unit = parameters.get('unit', None)

    if 'simple_example' in parameters and unit == 'unit 1':

        property_information = {
            'kids_response': 'Absolutely, kids are allowed in the unit.',
            'pets_policy': 'Yes, some pets are allowed. Our pet policy includes a monthly fee of $ 25 per cat and $ 45 per dog. ',
            'unit_requirements': "Damage deposit CAD$ 1,125 is required to secure the unit, and first month's rent CAD$ 1,125 prior to move-in.",
            'number_of_rooms': '2',
            'number_of_bathrooms': '1',
            'rent': 'CAD$ 1,125',
            'deposit': 'CAD$ 1,125',
            'utilities': 'Water and lawn maintenance are included in the rent. The tenant is responsible for electricity and natural gas.',
            'balcony': 'No, unfortunately the unit does no have a balcony.',
        }

        status_code = 200

    elif 'simple_example' in parameters and unit == 'unit 2':
        property_information = {
            'kids_response': 'Absolutely, kids are allowed in the unit.',
            'pets_policy': 'Yes, some pets are allowed. Our pet policy includes a monthly fee of $ 25 per cat and $ 45 per dog. ',
            'unit_requirements': "Damage deposit CAD$ 1,800 is required to secure the unit, and first month's rent CAD$ 1,800 prior to move-in.",
            'number_of_rooms': '3',
            'number_of_bathrooms': '3',
            'rent': 'CAD$ 1,800',
            'deposit': 'CAD$ 1,800',
            'utilities': 'Water and lawn maintenance are included in the rent. The tenant is responsible for electricity and natural gas.',
            'balcony': 'Yes, the unit has a private balcony.',
        }

        status_code = 200

    elif 'simple_example' in parameters and unit == 'unit 3':
        property_information = {
            'kids_response': 'Absolutely, kids are allowed in the unit.',
            'pets_policy': 'Yes, some pets are allowed. Our pet policy includes a monthly fee of $ 25 per cat and $ 45 per dog. ',
            'unit_requirements': "Damage deposit CAD$ 1,125 is required to secure the unit, and first month's rent CAD$ 1,125 prior to move-in.",
            'number_of_rooms': '2',
            'number_of_bathrooms': '2',
            'rent': 'CAD$ 1,125',
            'deposit': 'CAD$ 1,125',
            'utilities': 'Water and lawn maintenance are included in the rent. The tenant is responsible for electricity and natural gas.',
            'balcony': 'No, unfortunately the unit does no have a balcony.',
        }

        status_code = 200

    Print(parameters)

    return property_information, status_code
