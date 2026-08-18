from django.urls import path
from .apps import MailingConfig
from .views import (
    HomeView,
    MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView,
    MailingDeleteView,
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView,
    trigger_mailing_view, toggle_mailing_activity, MessageListView,
    MessageCreateView, MessageUpdateView, MessageDeleteView
)

app_name = MailingConfig.name

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # Рассылки
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(),
         name='mailing_detail'),
    path('mailings/create/', MailingCreateView.as_view(),
         name='mailing_create'),
    path('mailings/<int:pk>/update/', MailingUpdateView.as_view(),
         name='mailing_update'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(),
         name='mailing_delete'),
    path('mailings/<int:pk>/trigger/', trigger_mailing_view,
         name='mailing_trigger'),
    path('mailings/<int:pk>/toggle/', toggle_mailing_activity,
         name='mailing_toggle'),

    # Клиенты
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(),
         name='client_update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(),
         name='client_delete'),
# Сообщения
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
]
