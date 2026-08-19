from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView, TemplateView

from mailing.forms import MailingForm
from mailing.models import Message
from .models import Mailing, Client
from .services import send_mailing_messages


# ГЛАВНАЯ СТРАНИЦА С КЕШИРОВАНИЕМ
class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Берем данные из кэша
        mailing_count = cache.get('mailing_count')
        if not mailing_count:
            mailing_count = Mailing.objects.count()
            cache.set('mailing_count', mailing_count, 60)

        active_mailings = Mailing.objects.filter(status='Запущена',
                                                 is_active=True).count()
        unique_clients = Client.objects.values('email').distinct().count()

        context['mailing_count'] = mailing_count
        context['active_mailings'] = active_mailings
        context['unique_clients'] = unique_clients
        return context


# CRUD ДЛЯ РАССЫЛОК
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self):
        # Менеджер видит ВСЕ рассылки, обычный пользователь — только СВОИ
        if self.request.user.is_manager:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'

    def get_object(self, queryset=None):
        # Динамический пересчет статуса при просмотре
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def test_func(self):
        obj = self.get_object()
        # Доступ есть у владельца или менеджера
        return self.request.user == obj.owner or self.request.user.is_manager


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def test_func(self):
        obj = self.get_object()
        # Менеджер НЕ может редактировать чужие данные. Только владелец.
        return self.request.user == obj.owner


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def test_func(self):
        obj = self.get_object()
        # Удалять может только владелец
        return self.request.user == obj.owner


# ФУНКЦИЯ ДЛЯ МЕНЕДЖЕРА: ОТКЛЮЧЕНИЕ РАССЫЛКИ
def toggle_mailing_activity(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    # Отключать может только менеджер
    if request.user.is_manager:
        mailing.is_active = not mailing.is_active
        mailing.save()
    return redirect('mailing:mailing_list')


# РУЧНОЙ ЗАПУСК ОТПРАВКИ ПО ТРЕБОВАНИЮ
def trigger_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.user == mailing.owner:
        send_mailing_messages(mailing)  # ← Вызов функции отправки
    return redirect('mailing:mailing_detail', pk=pk)


# CRUD ДЛЯ КЛИЕНТОВ
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'

    def get_queryset(self):
        if self.request.user.is_manager:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def test_func(self):
        return self.request.user == self.get_object().owner


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def test_func(self):
        return self.request.user == self.get_object().owner


# CRUD ДЛЯ СООБЩЕНИЙ
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'

    def get_queryset(self):
        # Менеджер видит все сообщения, обычный пользователь — только свои
        if self.request.user.is_manager:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['title', 'body']
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        # Автоматически назначаем текущего пользователя владельцем сообщения
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Message
    fields = ['title', 'body']
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def test_func(self):
        return self.request.user == self.get_object().owner


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def test_func(self):
        return self.request.user == self.get_object().owner
