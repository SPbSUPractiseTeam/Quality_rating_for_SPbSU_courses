from django import forms


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=100, label="Введите название курса")
    log = forms.FileField()

class UploadFileSmallForm(forms.Form):
    log = forms.FileField()
