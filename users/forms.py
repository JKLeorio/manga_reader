from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms


class RegisterForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('email','nickname','avatar')


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ('nickname', 'email', 'avatar')