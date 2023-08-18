from django import forms
from django.forms import inlineformset_factory
from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.admin import site as admin_site
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

# from django.urls import reverse
# from django.utils.safestring import mark_safe
# from django.forms import widgets
# from django.conf import settings

from .models import Manga, Chapter, Volume, Page, Painter, Author


# class RelatedFieldWidgetCanAdd(widgets.Select):

# 	def __init__(self, related_model, related_url=None, *args, **kw):

# 		super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kw)

# 		if not related_url:
# 			rel_to = related_model
# 			info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
# 			related_url = 'admin:%s_%s_add' % info

# 		# Be careful that here "reverse" is not allowed
# 		self.related_url = related_url

# 	def render(self, name, value, *args, **kwargs):
# 		self.related_url = reverse(self.related_url)
# 		output = [super(RelatedFieldWidgetCanAdd, self).render(name, value, *args, **kwargs)]
# 		output.append(u'<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
# 		(self.related_url, name))
# 		output.append(u'<img src="%sadmin/img/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.STATIC_URL, 'Add Another'))                                                                                                                               
# 		return mark_safe(u''.join(output))


class MangaForm(forms.ModelForm):
    class Meta:
        model = Manga
        fields = ["name", "description", "release_year", "status", "author", "painter", "release_format", "manga_cover"]

        widgets = {
            # 'manga_cover': forms.ClearableFileInput(attrs={'multiple': True}),
            'release_format': CheckboxSelectMultiple(),
        }


class VolumeForm(forms.ModelForm):
    class Meta:
        model = Volume
        fields = ["number", "manga"]


# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True


# class MultipleFileField(forms.ImageField):
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault("widget", MultipleFileInput())
#         super().__init__(*args, **kwargs)

#     def clean(self, data, initial=None):
#         single_file_clean = super().clean
#         if isinstance(data, (list, tuple)):
#             result = [single_file_clean(d, initial) for d in data]
#         else:
#             result = single_file_clean(data, initial)
#         return result

class PainterForm(forms.ModelForm):
    class Meta:
        model = Painter
        fields = ["first_name", "last_name", "Date_of_Birth"]


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["first_name", "last_name", "Date_of_Birth"]


class ChapterForm(forms.ModelForm):
    # manga = forms.ModelChoiceField(label="Манга", queryset=Manga.objects.all())
    # volume = forms.ModelChoiceField(label = "Том", queryset=Volume.objects.all())
    # number = forms.IntegerField(label = "Номер")
    # images = forms.FileField(label="Страницы/Архив")

    # volume = forms.ModelChoiceField(
    # 	required=False,
    # 	queryset=Volume.objects.all(),
    # 	widget=RelatedFieldWidgetCanAdd(Volume, related_url="volume_create"))

    # volume = forms.ModelChoiceField(required=True,
    # 	queryset=Volume.objects.all(),
    # 	label = "Volume",
    # 	empty_label="-----")

    # def __init__(self, *args, **kwargs):
    # 	super().__init__(*args, **kwargs)
    # 	self.fields['volume'].widget = (
    # 		RelatedFieldWidgetWrapper(
    # 			self.fields['volume'].widget,
    # 			self.instance._meta.get_field('volume').remote_field,
    # 			admin_site,
    # 		)
    # 	)

    class Meta:
        model = Chapter
        fields = ["title", "volume", "number"]


# widgets = {
# 	"images" : forms.ClearableFileInput(attrs={'multiple': True})
# }

# class Media:
# 	css = {
# 	'all': ('/static/admin/css/widgets.css',),
# 	}
# 	js = ('/admin/jsi18n',)


class ChapterQuickForm(ChapterForm):
    manga = forms.ModelChoiceField(label="Манга", queryset=Manga.objects.all())

    class Meta:
        model = Chapter
        fields = ["manga", "title", "volume", "number"]


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["number", "chapter", "image"]


PagesFormSet = inlineformset_factory(Chapter,
                                     Page,
                                     form=PageForm,
                                     extra=1,
                                     can_delete=False,
                                     can_delete_extra=False)
