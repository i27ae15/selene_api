from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

class propertyTest(APIView):

    def post(self, request):

        print('-'*50)
        print('request.data: ', request.data)
        print('-'*50)

        if request.data.get('simple_example'):

            property_information = {
                'property_name': 'Property number 1',
                'property_address': '1234 Main Street',
                'bathrooms': '2',
                'bedrooms': '3',
                'square_feet': '1200',
                'pet_friendly': 'Yes',
            }


        return Response(property_information, status=status.HTTP_200_OK)
