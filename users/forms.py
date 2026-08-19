from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Кастомная форма регистрации (без поля username)
class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomUserCreationForm(StyleFormMixin, forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}),
        label="Пароль"
    )

    class Meta:
        model = User
        fields = ('email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Этот метод Django правильно захеширует пароль и подготовит модель
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# Кастомная форма логина под авторизацию по Email
class CustomAuthenticationForm(StyleFormMixin, AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}), label="Email адрес")
