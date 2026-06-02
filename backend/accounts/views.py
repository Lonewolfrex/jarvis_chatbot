from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from chat.models import ChatSession

class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()

            ChatSession.objects.create(
                user=user,
                title="Welcome Chat"
            )

            return Response(
                {"message": "User created"},
                status=201
            )

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "tenant": request.user.tenant.name
        })