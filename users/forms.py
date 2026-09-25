from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm

from mailing.forms import StyleFormMixin
from users.models import CustomUser


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name", "patronymic", "phone_number", "country")


class CustomUserChangeForm(StyleFormMixin, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "patronymic", "phone_number", "country")


class UserLoginForm(StyleFormMixin, AuthenticationForm):
    """Форма входа в систему с красивыми стилями Bootstrap"""

    pass
