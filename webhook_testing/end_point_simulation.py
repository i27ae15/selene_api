def get_properties_test(parameters:dict) -> 'tuple(dict, int)':
    """
    This function will get the properties from the database
    """
    property_information = {}
    status_code = 200

    if 'simple_example' in parameters:

        property_information = {
            'property_name': 'Property number 1',
            'property_address': '1234 Main Street',
            'bathrooms': '2',
            'bedrooms': '3',
            'square_feet': '1200',
            'pet_friendly': 'Yes',
        }

        status_code = 200

    return property_information, status_code
