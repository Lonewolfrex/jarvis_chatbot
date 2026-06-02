from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer
)


# 1. Create & List Sessions
class ChatSessionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        sessions = ChatSession.objects.filter(
            user=request.user
        )

        serializer = ChatSessionSerializer(
            sessions,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        session = ChatSession.objects.create(
            user=request.user,
            title=request.data.get(
                "title",
                "New Chat"
            )
        )

        return Response(
            ChatSessionSerializer(session).data
        )


# 2. Get Messages in a Session
class ChatMessageView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):

        messages = ChatMessage.objects.filter(
            session_id=session_id,
            session__user=request.user
        )

        return Response(
            ChatMessageSerializer(
                messages,
                many=True
            ).data
        )


# 3. Send Message (TEMP: dummy AI response)
class ChatPromptView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        session_id = request.data.get("session_id")
        user_message = request.data.get("message")

        session = ChatSession.objects.get(
            id=session_id,
            user=request.user
        )

        # Save user message
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=user_message
        )

        # Dummy AI (will be replaced with Ollama soon)
        from .ai_service import OllamaService
        ai_response = OllamaService.generate_response(user_message)

        ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=ai_response
        )

        return Response({
            "session_id": session.id,
            "response": ai_response
        })