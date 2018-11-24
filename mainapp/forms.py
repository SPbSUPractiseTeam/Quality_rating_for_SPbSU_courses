from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=100, label="Введите название курса")
    log = forms.FileField()


class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaWidget())
    email = forms.EmailField(max_length=200, help_text='Обязательное поле', label='Электронная почта')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')