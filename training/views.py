from rest_framework.views import APIView
from rest_framework.response import Response

from .training import train

class TrainingAPI(APIView):

    def get(self, request):
        return Response({"message": "Hello, world!"})

    
    def post(self, request):
        """Endpoint for training a model"""
        data_to_create_train_model = request.data


        train(data_to_create_train_model)


        return Response({"message": "Model train successfully!"})