from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.http import HttpResponseNotFound
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from .filters import MangaFilter
from .forms import MangaForm, ChapterForm, VolumeForm, PagesFormSet, AuthorForm, PainterForm, ChapterQuickForm
from .models import Manga, Chapter, Volume, Page, Author, Painter

import zipfile


# Create your views here.


class MangaCreateView(CreateView, LoginRequiredMixin):
    template_name = 'manga/manga_create.html'
    form_class = MangaForm
    success_url = reverse_lazy('manga_list')


class MangaListView(ListView):
    template_name = 'manga/manga_list.html'
    model = Manga
    context_object_name = 'manga_objects'
    filter_order = {"by_date_descending": "-release_year",
                    'by_date_ascending': "release_year",
                    "by_popularity": {}}

    filter_order_options = {"by_date_descending": "По убыванию даты создания",
                            "by_date_ascending": "По возрастанию даты создания",
                            "by_popularity": "По популярности"}

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        filter_action = None
        if 'order_by' in request.GET:
            filter_action = (self.filter_order[request.GET.get('order_by')])
        filter_ob = MangaFilter(request.GET, queryset=Manga.objects.all())
        if filter_action:
            filter_ob.qs.order_by(filter_action)
        response.context_data['filter'] = filter_ob
        response.context_data[self.context_object_name] = filter_ob.qs
        return response


class MangaDetailView(DetailView):
    model = Manga
    template_name = "manga/manga_detail.html"
    context_object_name = "manga_object"


class MangaUpdateView(LoginRequiredMixin, UpdateView):
    model = Manga
    form_class = MangaForm
    template_name = "manga/manga_update.html"

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("manga_update", kwargs={"pk": pk})


class MangaDeleteView(LoginRequiredMixin, DeleteView):
    model = Manga
    success_url = reverse_lazy("manga_list")


# class VolumeListView(ListView):
# 	model = Volume
# 	template_name = "Volume_list.html"
# 	context_object_name = "volume_objects"

class VolumeCreateView(CreateView, LoginRequiredMixin):
    template_name = "volume_create.html"
    form_class = VolumeForm
    success_url = reverse_lazy("chapter_create")


class ChapterDetailView(View):
    template_name = "chapter_detail.html"

    def get(self, request, chapter=None, m_pk=None, volume=None, page=None):

        manga_object = Manga.objects.filter(id=m_pk).first()
        if not manga_object:
            return HttpResponseNotFound()
        volume_object = Volume.objects.filter(number=volume, manga=manga_object).first()
        if not manga_object:
            return HttpResponseNotFound()
        chapter_object = Chapter.objects.filter(number=chapter, volume=volume_object).first()
        if not volume_object:
            return HttpResponseNotFound()
        page_objects = Page.objects.filter(chapter=chapter_object)
        if not page_objects:
            return HttpResponseNotFound()
        page_object = page_objects.filter(number=page).first()
        if not page_object:
            return HttpResponseNotFound()
        return render(request, self.template_name,
                      {
                          "manga_object": manga_object,
                          "volume_object": volume_object,
                          "chapter_object": chapter_object,
                          "page_objects": page_objects,
                          "page_object": page_object
                      })


# class ChapterCreateView(FormView, LoginRequiredMixin):

# 	template_name = "chapter_create.html"
# 	form_class = ChapterForm

# 	# def get(self, request):
# 	# 	form = ChapterForm()
# 	# 	return render(request, self.template_name, {"form" : form})

# 	def get_success_url(self):
# 		pk = self.kwargs["pk"]
# 		return reverse("manga_update", kwargs = {"pk" : pk})

# 	def post(self, request):
# 		form_class = self.get_form_class()
# 		form = self.get_form(form_class)
# 		if form.is_valid():
# 			return self.form_valid(form)
# 		else:
# 			return self.form_invalid(form)

# 	def form_valid(self, form):
# 		images = form.cleaned_data["images"]
# 		for image in images:
# 			pass
# 		return super().form_valid()


def validate_and_save_pages_archive(archive, chapter):
    acceptable_archive_extensions = ['zip']
    acceptable_images_extensions = ['jpeg', 'png', 'jpg']
    errors = []
    archive_members_names = []
    if archive.name.split('.')[-1] not in acceptable_archive_extensions:
        raise ValidationError(f'the file must be a [{", ".join(acceptable_archive_extensions)}] archive')
    with zipfile.ZipFile(archive, mode='r') as opened_archive:
        for archive_member in opened_archive.infolist():
            print(archive_member.filename.split('.')[-1], archive_member.is_dir())
            if archive_member.is_dir() or archive_member.filename.split('.')[-1] not in acceptable_images_extensions:
                errors.append('archive must contain only images files')
            elif not archive_member.filename.split('.')[0].isnumeric():
                errors.append('file name must contain only numbers')

            if archive_member.filename not in archive_members_names:
                archive_members_names.append(archive_member.filename)
            else:
                errors.append('file names must be unique')

            if errors:
                chapter.delete()
                raise ValidationError(errors)

            with opened_archive.open(archive_member, mode='r') as content:
                page = Page(number=int(archive_member.filename.split('.')[0]), chapter=chapter)
                page.image.save(archive_member.filename, ContentFile(content.read()))
                page.save()


class ChapterInline:
    model = Chapter
    form_class = ChapterQuickForm
    template_name = "chapter_create.html"

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

    # def post(self, request):
    # form = ChapterForm(request.POST)
    # form2 = ChapterImageForm(request.POST, request.FILES)
    # images = request.FILES.getlist('images')
    # if form.is_valid() and form2.is_valid():
    #     for image in images:
    #     	pass
    #     return redirect(reverse(self.success_url))
    # context = {'form': form, 'form2': form2}
    # return render(request, 'projects/project_form.html', context)
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
