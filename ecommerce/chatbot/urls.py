# chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_with_gemini, name='chat_with_gemini'),
    path('chat/clear/', views.clear_chat_history, name='clear_chat_history'),
]