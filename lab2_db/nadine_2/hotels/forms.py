from django import forms

from .models import Comment, Country, Hotel, Feature


class FeatureForm(forms.Form):
    new_feature = forms.CharField(max_length=50, min_length=1)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'message', 'rating']


class AddCountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', 'description']


class EditCountryForm(forms.ModelForm):
    name = forms.CharField(required=False, disabled=True)

    class Meta:
        model = Country
        fields = ['name', 'description']