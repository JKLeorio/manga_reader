from django.contrib import admin
from .models import Author, ReleaseFormat, Painter, Manga, Volume, Chapter, Page

my_models = [Author, ReleaseFormat, Painter, Manga, Volume, Chapter, Page]
admin.site.register(my_models)
# Register your models here.
