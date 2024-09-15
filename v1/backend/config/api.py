// entire file content ...
from rest_framework import status, views
from rest_framework.response import Response

class APIView(views.APIView):
    def get(self, request):
        return Response({"message": "Hello from v1 backend!"}, status=status.HTTP_200_OK)
