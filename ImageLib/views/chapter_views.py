from django.forms import ModelForm
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from ..forms import ChapterForm, VolumeForm, PagesFormSet, ChapterQuickForm
from ..models import Manga, Chapter, Volume, Page
from ..utils import validate_archive_extension, validate_image

import zipfile


class VolumeCreateView(CreateView, LoginRequiredMixin):
    template_name = "volume_create.html"
    form_class = VolumeForm
    success_url = reverse_lazy("chapter_create")


class ChapterDetailView(View):
    template_name = "chapter/chapter_detail.html"

    def get(self, request, chapter=None, manga=None, volume=None, page=None):
        manga = get_object_or_404(Manga, id=manga)
        volume = get_object_or_404(Volume, id=volume, manga=manga)
        chapter = get_object_or_404(Chapter, id=chapter, volume=volume)
        page = get_object_or_404(Page, id=page)
        pages = Page.objects.filter(chapter=chapter).order_by("number")
        if not pages:
            raise Http404("page not found")

        context = {
            "manga": manga,
            "volume": volume,
            "chapter": chapter,
            "pages": pages,
            "page": page
        }
        return render(request, self.template_name, context)


# TODO add page replacement function for chapter update
def validate_and_save_pages_archive(file, chapter):
    validate_archive_extension(file)

    with zipfile.ZipFile(file, mode='r') as archive:
        pages = []

        for image in archive.infolist():
            errors = validate_image(image)

            if len(errors) > 0:
                chapter.delete()
                raise ValidationError(errors)

            with archive.open(image, mode='r') as content:
                number = int(image.filename.split('.')[0])

                page = Page(number=number, chapter=chapter)
                page.image.save(image.filename, ContentFile(content.read()))
                pages.append(page)

        Page.objects.bulk_create(pages)


class ChapterInline:
    model = Chapter
    form_class = ChapterQuickForm
    success_url = "/"
    template_name = "chapter/chapter_create.html"

    def form_valid(self, form: ModelForm):
        page_formset = self.get_pages_formset()

        if not page_formset.is_valid():
            form.add_error(None, "page formset error")
            return super().form_invalid(form)

        data = form.cleaned_data

        if data['manga'].pk != data['volume'].manga.pk:
            raise ValidationError('bad request')

        chapter = self.object

        if not self.object:
            new_form = ChapterForm(data=data, files=form.files)
            chapter = new_form.save()

        archive = form.files.get('images', None)
        if archive:
            validate_and_save_pages_archive(archive, chapter)

        for form in page_formset:
            self.form_pages_valid(form, chapter)

        return redirect("manga_list")

    def form_pages_valid(self, form, chapter):
        page = form.save(commit=False)
        page.chapter = chapter
        page.save()


class ChapterCreateView(ChapterInline, CreateView, LoginRequiredMixin):

    def get_initial(self):
        manga = self.kwargs['manga']
        if manga:
            return {"manga": manga}
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = PagesFormSet(prefix="pages")
        return context

    def get_pages_formset(self):
        if self.request.method == "GET":
            return PagesFormSet(prefix='pages')
        else:
            return PagesFormSet(self.request.POST or None, self.request.FILES or None, prefix='pages',
                                form_kwargs={'empty_permitted': False})


class ChapterUpdateView(ChapterInline, UpdateView, LoginRequiredMixin):

    def get_context_data(self, **kwargs):
        context = super(ChapterUpdateView, self).get_context_data(**kwargs)

        chapter = self.get_object()
        form = self.get_form_class()(initial={"manga": chapter.volume.manga}, instance=chapter)

        context['form'] = form
        context['formset'] = self.get_pages_formset()
        return context

    def get_pages_formset(self):
        return PagesFormSet(
            self.request.POST or None,
            self.request.FILES or None,
            instance=self.object,
            prefix='pages',
            form_kwargs={'empty_permitted': False}
        )
