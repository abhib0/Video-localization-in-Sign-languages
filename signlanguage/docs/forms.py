from django import forms
from docs.models import MyModel

class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'accept':'video/mp4'}))

