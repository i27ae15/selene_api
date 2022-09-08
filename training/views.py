from rest_framework.views import APIView
from rest_framework.response import Response

from .training import train


class TrainingAPI(APIView):

    def get(self, request):
        return Response({"message": "Hello, world!"})

    
    def post(self, request):
        """Endpoint for training a model"""
        data_to_create_model = request.data['data_to_create_model']
        model_name = request.data['model_name']

        train(data_to_create_model, model_name)


        return Response({"message": "Model train successfully!"})