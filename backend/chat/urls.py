from django.urls import path

from .views import (
    ChatSessionView,
    ChatMessageView,
    ChatPromptView
)

urlpatterns = [

    path("sessions/",ChatSessionView.as_view()),
    path("sessions/<int:session_id>/messages/",ChatMessageView.as_view()),
    path("prompt/",ChatPromptView.as_view()),
]