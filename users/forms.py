from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name", "patronymic", "phone_number", "country")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "patronymic", "phone_number", "country")