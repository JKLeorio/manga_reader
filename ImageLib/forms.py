from django import forms
from django.forms import inlineformset_factory
from django.forms.widgets import CheckboxSelectMultiple, ClearableFileInput, FileInput

from .models import Manga, Chapter, Volume, Page, Painter, Author


ZIP_FORMAT = "zip,application/octet-stream,application/zip,application/x-zip,application/x-zip-compressed"


class MangaForm(forms.ModelForm):
    class Meta:
        model = Manga
        fields = [
            "name", "description", "release_year", "status", "author",
            "painter", "genres", "release_format", "manga_cover"
        ]

        widgets = {
            'release_format': CheckboxSelectMultiple(),
        }


class VolumeForm(forms.ModelForm):
    class Meta:
        model = Volume
        fields = ["number", "manga"]


class PainterForm(forms.ModelForm):
    class Meta:
        model = Painter
        fields = ["first_name", "last_name", "Date_of_Birth"]


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["first_name", "last_name", "Date_of_Birth"]


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ["title", "volume", "number"]


class ChapterQuickForm(forms.ModelForm):
    manga = forms.ModelChoiceField(label="Манга", queryset=Manga.objects.all())
    images = forms.FileField(label="Страницы/Архив", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            is_file = type(visible.field.widget) in [FileInput, ClearableFileInput]
            if is_file:
                visible.field.widget.attrs["accept"] = ZIP_FORMAT

    class Meta:
        model = Chapter
        fields = ["manga", "volume", "title", "number", "images"]


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["number", "image"]


PagesFormSet = inlineformset_factory(
    Chapter,
    Page,
    form=PageForm,
    extra=1,
    can_delete=False,
    can_delete_extra=False
)
