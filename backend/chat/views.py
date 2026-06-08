from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse

from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer
)

import traceback

# 1. Create & List Sessions
class ChatSessionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        sessions = ChatSession.objects.filter(
            user=request.user
        ).order_by("-updated_at")

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

        try:

            session_id = request.data.get("session_id")
            user_message = request.data.get("message")

            session = ChatSession.objects.get(
                id=session_id,
                user=request.user
            )

            if session.title == "New Chat":

                title = OllamaService.generate_title(
                    user_message
                )

                session.title = title[:60]

                session.save(
                    update_fields=["title"]
                )

            ChatMessage.objects.create(
                session=session,
                role="user",
                content=user_message
            )

            history = ChatMessage.objects.filter(
                session=session
            ).order_by("-created_at")[:10]

            history = reversed(history)

            prompt = ""

            for msg in history:

                if msg.role == "user":
                    prompt += f"User: {msg.content}\n"

                else:
                    prompt += f"Assistant: {msg.content}\n"

            prompt += f"\nUser: {user_message}\nAssistant:"

            from .ai_service import OllamaService

            ai_response = OllamaService.generate_response(
                prompt
            )

            ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=ai_response
            )

            return Response({
                "session_id": session.id,
                "response": ai_response
            })

        except Exception as e:

            print("=" * 80)
            print("CHAT ERROR")
            print(traceback.format_exc())
            print("=" * 80)

            return Response(
                {"error": str(e)},
                status=500
            )

class ChatSessionDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, session_id):

        session = ChatSession.objects.get(
            id=session_id,
            user=request.user
        )

        session.title = request.data.get(
            "title",
            session.title
        )

        session.save()

        return Response({
            "status": "updated"
        })

    def delete(self, request, session_id):

        session = ChatSession.objects.get(
            id=session_id,
            user=request.user
        )

        session.delete()

        return Response({
            "status": "deleted"
        })

class RegenerateResponseView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        session_id = request.data.get("session_id")

        session = ChatSession.objects.get(
            id=session_id,
            user=request.user
        )

        last_user = ChatMessage.objects.filter(
            session=session,
            role="user"
        ).order_by("-created_at").first()

        if not last_user:
            return Response(
                {"error": "No user message found"},
                status=400
            )

        from .ai_service import OllamaService

        ai_response = OllamaService.generate_response(
            last_user.content
        )

        ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=ai_response
        )

        return Response({
            "response": ai_response
        })

class StreamPromptView(APIView):

    permission_classes=[IsAuthenticated]

    def post(self,request):

        session_id=request.data.get(
            "session_id"
        )

        message=request.data.get(
            "message"
        )

        session=ChatSession.objects.get(
            id=session_id,
            user=request.user
        )

        ChatMessage.objects.create(
            session=session,
            role="user",
            content=message
        )

        from .ai_service import OllamaService

        def generate():

            full_response=""

            for chunk in OllamaService.generate_stream(
                message
            ):

                full_response+=chunk

                yield chunk

            ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=full_response
            )

        return StreamingHttpResponse(
            generate(),
            content_type="text/plain"
        )

