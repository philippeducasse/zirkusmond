from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin

from .models import RentalObject


class RentalObjectForm(forms.ModelForm):
    description = forms.CharField(widget=TinyMCE(), required=False)

    class Meta:
        model = RentalObject
        fields = "__all__"


class RentalObjectAdmin(ModelAdmin):
    form = RentalObjectForm


admin.site.register(RentalObject, RentalObjectAdmin)
