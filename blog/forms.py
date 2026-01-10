from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    # Hidden input to store canvas data
    drawing_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Post
        fields = ['title', 'content', 'drawing_data']