from django.contrib import messages
from django.shortcuts import render, reverse, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.http import HttpResponseNotFound
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django_filters.views import FilterView

from .filters import MangaFilter
from .forms import MangaForm, ChapterForm, VolumeForm, PagesFormSet, AuthorForm, PainterForm, ChapterQuickForm
from .models import Manga, Chapter, Volume, Page, Author, Painter


import zipfile


class MangaCreateView(CreateView, LoginRequiredMixin):
    template_name = 'manga/manga_create.html'
    form_class = MangaForm
    success_url = reverse_lazy('manga_list')


class MangaListView(FilterView):
    filterset_class = MangaFilter
    template_name = 'manga/manga_list.html'
    model = Manga
    context_object_name = 'manga_objects'

    def get_queryset(self):
        params = self.request.GET
        queryset = Manga.objects.all()
        order_by = params.get('order_by')
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset


class MangaDetailView(DetailView):
    model = Manga
    template_name = "manga/manga_detail.html"
    context_object_name = "manga"


class MangaUpdateView(LoginRequiredMixin, UpdateView):
    model = Manga
    form_class = MangaForm
    template_name = "manga/manga_update.html"

    def get_success_url(self):
        return reverse("manga_detail", args=[self.kwargs['pk']])


class MangaDeleteView(LoginRequiredMixin, DeleteView):
    model = Manga
    success_url = reverse_lazy("manga_list")


class VolumeCreateView(CreateView, LoginRequiredMixin):
    template_name = "volume_create.html"
    form_class = VolumeForm
    success_url = reverse_lazy("chapter_create")


class ChapterDetailView(View):
    template_name = "chapter/chapter_detail.html"

    def get(self, request, chapter=None, m_pk=None, volume=None, page=None):
        manga = get_object_or_404(Manga, id=m_pk)
        volume = get_object_or_404(Volume, number=volume, manga=manga)
        chapter = get_object_or_404(Chapter, number=chapter, volume=volume)
        page = get_object_or_404(Page, number=page)
        pages = get_list_or_404(Page.objects.filter(chapter=chapter))

        context = {
            "manga": manga,
            "volume": volume,
            "chapter": chapter,
            "pages": pages,
            "page": page
        }
        return render(request, self.template_name, context)


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


def validate_archive_extension(archive):
    if archive.name.split('.')[-1] != 'zip':
        raise ValidationError('the file must be a zip archive')


def validate_image(image):
    errors = []
    image_formats = ['jpeg', 'png', 'jpg']
    added_images = []

    not_image = image.filename.split('.')[-1] not in image_formats
    name_is_number = image.filename.split('.')[0].isnumeric()

    if image.is_dir() or not_image:
        errors.append('archive must contain only images files')

    elif not name_is_number:
        errors.append('file name must contain only numbers')

    if image.filename in added_images:
        errors.append('file names must be unique')
        return errors

    added_images.append(image.filename)

    return errors


class ChapterInline:
    model = Chapter
    form_class = ChapterQuickForm
    template_name = "chapter/chapter_create.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        new_form_data = form.data.copy()
        new_form = ChapterForm(data=new_form_data, files=form.files)
        # if "manga" in form.data:
        if form.is_valid():
            manga_p = new_form_data.pop("manga")[0]
            new_form.data = new_form_data
            if new_form.is_valid():
                volume_p = new_form.data["volume"]
                volume = Volume.objects.filter(pk=volume_p).first()
                manga = Manga.objects.filter(pk=manga_p, volume=volume).first()
                if volume and manga:
                    self.object = new_form.save()
                else:
                    raise ValidationError(form.errors)
                archive = form.files.get('images', None)
                if archive:
                    validate_and_save_pages_archive(archive, self.object)
            else:
                raise ValidationError(new_form.errors)

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('manga_list')

    def formset_pages_valid(self, formset):
        pages = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for page in pages:
            page.chapter = self.object
            page.save()


class ChapterCreateView(ChapterInline, CreateView, LoginRequiredMixin):

    def get(self, request, *args, **kwargs):
        self.initial_form_data = kwargs['manga']
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ChapterCreateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        if self.initial_form_data:
            form = self.get_form_class()(initial={"manga": self.initial_form_data})
            ctx['form'] = form
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'pages': PagesFormSet(prefix='pages'),
            }
        else:
            return {
                'pages': PagesFormSet(self.request.POST or None, self.request.FILES or None, prefix='pages'),
            }


class ChapterUpdateView(ChapterInline, UpdateView, LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        ctx = super(ChapterUpdateView, self).get_context_data(**kwargs)
        form_data = self.get_object()
        form = self.get_form_class()(initial={"manga": form_data.volume.manga}, instance=form_data)
        ctx['form'] = form
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'pages': PagesFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object,
                                  prefix='pages]'),
        }


class AuthorCreateView(CreateView, LoginRequiredMixin):
    template_name = "author_create.html"
    model = Author
    form_class = AuthorForm


class PainterCreateView(CreateView, LoginRequiredMixin):
    template_name = "painter_create.html"
    model = Painter
    form_class = PainterForm


def delete_page(request, pk):
    try:
        page = Page.objects.get(id=pk)
    except Page.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
        )
        return redirect('chapter_create')

    page.delete()
    messages.success(
        request, 'Image deleted successfully'
    )
    return redirect('chapter_update', pk=page.chapter.id)
