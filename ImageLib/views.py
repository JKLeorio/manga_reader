from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView
from django.http import HttpResponseNotFound
from django.core.exceptions import ValidationError

from .forms import MangaForm, ChapterForm, VolumeForm, PagesFormSet, AuthorForm, PainterForm, ChapterQuickForm
from .models import Manga, Chapter, Volume, Page, Author, Painter


# Create your views here.


class MangaCreateView(CreateView, LoginRequiredMixin):
    template_name = 'manga_create.html'
    form_class = MangaForm
    success_url = reverse_lazy('manga_list')


class MangaListView(ListView):
    template_name = 'manga_list.html'
    model = Manga
    context_object_name = 'manga_objects'


class MangaDetailView(DetailView):
    model = Manga
    template_name = "manga_detail.html"
    context_object_name = "manga_object"


class MangaUpdateView(LoginRequiredMixin, UpdateView):
    model = Manga
    form_class = MangaForm
    template_name = "manga_update.html"

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

        if "manga" in form.data:
            manga_p = new_form_data.pop("manga")[0]
            new_form.data = new_form_data
            if new_form.is_valid():
                volume_p = new_form.data["volume"]
                volume = Volume.objects.filter(pk=volume_p).first()
                manga = Manga.objects.filter(pk=manga_p, volume=volume).first()

        self.object = new_form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('manga_list')

    def formset_pages_valid(self, formset):
        pages = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter
        # set in inlineformset_factory func
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

    def get_context_data(self, **kwargs):
        ctx = super(ChapterCreateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
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
