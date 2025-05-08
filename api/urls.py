from django.urls import path
from .views import WebhookView, ConversationDetailView, ConversationListView

urlpatterns = [
    path('webhook/', WebhookView.as_view(), name='webhook'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:id>/', ConversationDetailView.as_view(), name='conversation-detail'),
]