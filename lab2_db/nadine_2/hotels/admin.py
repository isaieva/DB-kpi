from django.contrib import admin
from django import forms

from .models import Hotel, Country, Comment, Room, Feature


class HotelAdminForm(forms.ModelForm):
    features = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Feature.objects,
        widget=forms.CheckboxSelectMultiple
    )


class HotelAdmin(admin.ModelAdmin):
    form = HotelAdminForm


admin.site.register(Hotel, HotelAdmin)

admin.site.register([
    Country, Comment, Room, Feature
])
