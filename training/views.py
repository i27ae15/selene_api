from rest_framework.views import APIView
from rest_framework.response import Response

# others
from .training import train, SeleneModel


class TrainingAPI(APIView):

    def get(self, request):
        return Response({"message": "Hello, world!"})

    
    def post(self, request):
        """Endpoint for training a model"""

        if request.data.get('model_id'):

            model_id:int = request.data.get('model_id')
            model:SeleneModel = SeleneModel.objects.get(id=model_id)

            train(data_to_create_model, model_name='model_name', previous_model_version=model.last_version)

            # if the model id is passed then we can perform other actions on the nodes to copy then from the previous version
            # so that, there is no need to change on the bot that is going to be deployed

            return Response({"message": "Training started"})


        data_to_create_model = request.data['data_to_create_model']
        model_name = request.data['model_name']

        train(data_to_create_model, model_name)


        return Response({"message": "Model trained successfully!"})