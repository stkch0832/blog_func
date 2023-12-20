from django import forms
from .models import Post

class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        for field in self.base_fields.values():
            field.widget.attrs["class"] = "form-control mb-3"
        super().__init__(*args, **kwargs)


    class Meta:
        model = Post
        exclude = ['user']
