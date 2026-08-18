import secrets

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView, FormView
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import ListView

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User

User = get_user_model()

# Форма восстановления пароля
class RecoveryForm(forms.Form):
    email = forms.EmailField(label="Ваш Email")


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        # Проверка блокировки менеджером
        user = form.get_user()
        if user.is_blocked:
            messages.error(self.request,
                           "Ваш аккаунт заблокирован менеджером.")
            return redirect('users:login')
        # Проверка верификации
        if not user.is_verified:
            messages.error(self.request, "Пожалуйста, подтвердите ваш Email.")
            return redirect('users:login')
        return super().form_valid(form)


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)

        # Делаем пользователя неверифицированным по умолчанию
        user.is_verified = False

        # Генерируем уникальный токен подтверждения
        user.verification_token = secrets.token_hex(16)
        user.save()

        # Формируем ссылку для подтверждения
        token_url = self.request.build_absolute_uri(
            reverse('users:verify_email',
                    kwargs={'token': user.verification_token})
        )
        print(f"\n==== РАБОЧАЯ ССЫЛКА ДЛЯ БРАУЗЕРА: {token_url} ====\n")

        # Текст письма
        message_text = f"Здравствуйте! Для подтверждения вашей почты перейдите по ссылке:\n{token_url}"

        # Отправляем письмо через EmailMessage с явной кодировкой
        email = EmailMessage(
            subject="Подтверждение регистрации в Mailing Service",
            body=message_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.encoding = 'utf-8'  # Избавляет от кодирования в Base64 в консоли
        email.send(fail_silently=False)

        messages.success(self.request,
                         "Регистрация прошла успешно! На вашу почту отправлено письмо со ссылкой для активации.")
        return redirect(self.success_url)



def email_verification_view(request, token):
    user = User.objects.filter(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        user.save()
        messages.success(request,
                         "Email успешно подтвержден! Теперь вы можете войти.")
    else:
        messages.error(request, "Неверный или просроченный токен.")
    return redirect('users:login')


class PasswordRecoveryView(FormView):
    template_name = 'users/recovery.html'
    form_class = RecoveryForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            new_password = secrets.token_urlsafe(8)
            user.set_password(new_password)
            user.save()
            send_mail(
                subject="Восстановление пароля",
                message=f"Ваш новый временный пароль: {new_password}\nСмените его в личном кабинете после входа.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email]
            )
            messages.success(self.request,
                             "Новый пароль отправлен на вашу почту.")
        else:
            messages.error(self.request,
                           "Пользователь с таким Email не найден.")
        return super().form_valid(form)


# СПИСОК ПОЛЬЗОВАТЕЛЕЙ ДЛЯ МЕНЕДЖЕРА
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/user_list.html'

    def test_func(self):
        # Доступ к списку имеет только менеджер
        return self.request.user.is_manager


# ФУНКЦИЯ БЛОКИРОВКИ/РАЗБЛОКИРОВКИ ПОЛЬЗОВАТЕЛЯ
def toggle_user_block(request, pk):
    if not request.user.is_manager:
        return redirect('mailing:home')

    user = get_object_or_404(User, pk=pk)
    # Не даем менеджеру заблокировать самого себя или суперпользователя
    if user != request.user and not user.is_superuser:
        user.is_blocked = not user.is_blocked
        user.save()
    return redirect('users:user_list')
