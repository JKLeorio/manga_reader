import django_filters
from django_filters import FilterSet
from django.db import models
from django import forms
from .models import Manga, ReleaseFormat


class MangaFilter(FilterSet):
    release_format = django_filters.ModelMultipleChoiceFilter(queryset=ReleaseFormat.objects.all(),
                                                              widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Manga
        fields = ['release_year', 'author', 'painter', 'release_format']
