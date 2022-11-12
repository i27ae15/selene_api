
from django.utils.translation import gettext_lazy as _


from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import SeleneModel, SeleneNode, SeleneModelVersion
from .serializers import SeleneModelSerializer, SeleneNodeSerializer


class SeleneModelView(APIView):


    def get(self, request):

        version_id = int(request.query_params.get('version'))
        
        try:
            model_id = int(request.query_params['model_id'])
        except KeyError:
            raise exceptions.ValidationError(_("model_id is required"))

        model:SeleneModel = SeleneModel.objects.get(id=model_id)


        if not version_id:
            # get latest version
            nodes = model.nodes

            serializer = SeleneNodeSerializer(nodes, many=True)

            return Response(serializer.data)

        return Response({"message": "Hello, world!"})

